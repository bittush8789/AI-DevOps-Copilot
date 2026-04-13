from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import structlog
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = structlog.get_logger()


class VectorStore(ABC):
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[Dict]) -> bool:
        pass


class OpenSearchVectorStore(VectorStore):
    def __init__(self):
        from opensearchpy import OpenSearch, RequestsHttpConnection
        from requests_aws4auth import AWS4Auth
        import boto3
        
        self.index_name = settings.OPENSEARCH_INDEX
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        if settings.OPENSEARCH_ENDPOINT:
            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                settings.AWS_REGION,
                'es',
                session_token=credentials.token
            )
            
            self.client = OpenSearch(
                hosts=[settings.OPENSEARCH_ENDPOINT],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection,
            )
            self._ensure_index()
        else:
            self.client = None
            logger.warning("OpenSearch endpoint not configured")
    
    def _ensure_index(self):
        if not self.client:
            return
            
        if not self.client.indices.exists(index=self.index_name):
            index_body = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                },
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 384,
                            "method": {
                                "name": "hnsw",
                                "space_type": "l2",
                                "engine": "nmslib"
                            }
                        },
                        "metadata": {"type": "object"},
                        "timestamp": {"type": "date"}
                    }
                }
            }
            self.client.indices.create(index=self.index_name, body=index_body)
            logger.info(f"Created OpenSearch index: {self.index_name}")
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self.client:
            return []
        
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            search_body = {
                "size": top_k,
                "query": {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": top_k
                        }
                    }
                }
            }
            
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "content": hit["_source"]["content"],
                    "metadata": hit["_source"].get("metadata", {}),
                    "score": hit["_score"]
                })
            
            return results
            
        except Exception as e:
            logger.error("OpenSearch search error", error=str(e))
            return []
    
    async def add_documents(self, documents: List[Dict]) -> bool:
        if not self.client:
            return False
        
        try:
            for doc in documents:
                content = doc.get("content", "")
                embedding = self.embedding_model.encode(content).tolist()
                
                body = {
                    "content": content,
                    "embedding": embedding,
                    "metadata": doc.get("metadata", {}),
                    "timestamp": doc.get("timestamp")
                }
                
                self.client.index(
                    index=self.index_name,
                    body=body
                )
            
            self.client.indices.refresh(index=self.index_name)
            logger.info(f"Added {len(documents)} documents to OpenSearch")
            return True
            
        except Exception as e:
            logger.error("OpenSearch add documents error", error=str(e))
            return False


class PineconeVectorStore(VectorStore):
    def __init__(self):
        from pinecone import Pinecone
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        if settings.PINECONE_API_KEY:
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index = pc.Index(settings.PINECONE_INDEX)
        else:
            self.index = None
            logger.warning("Pinecone API key not configured")
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self.index:
            return []
        
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return [
                {
                    "content": match.metadata.get("content", ""),
                    "metadata": match.metadata,
                    "score": match.score
                }
                for match in results.matches
            ]
            
        except Exception as e:
            logger.error("Pinecone search error", error=str(e))
            return []
    
    async def add_documents(self, documents: List[Dict]) -> bool:
        if not self.index:
            return False
        
        try:
            vectors = []
            for i, doc in enumerate(documents):
                content = doc.get("content", "")
                embedding = self.embedding_model.encode(content).tolist()
                
                vectors.append({
                    "id": f"doc_{i}_{hash(content)}",
                    "values": embedding,
                    "metadata": {
                        "content": content,
                        **doc.get("metadata", {})
                    }
                })
            
            self.index.upsert(vectors=vectors)
            logger.info(f"Added {len(documents)} documents to Pinecone")
            return True
            
        except Exception as e:
            logger.error("Pinecone add documents error", error=str(e))
            return False


def get_vector_store() -> VectorStore:
    if settings.VECTOR_DB_TYPE == "pinecone":
        return PineconeVectorStore()
    else:
        return OpenSearchVectorStore()


vector_store = get_vector_store()
