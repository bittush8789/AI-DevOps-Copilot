from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import structlog
import uuid
from typing import AsyncGenerator

from app.models.schemas import ChatRequest, ChatResponse
from app.services.bedrock_service import bedrock_service
from app.services.vector_service import vector_store
from app.services import guardrail

router = APIRouter()
logger = structlog.get_logger()

SYSTEM_PROMPT = """You are an expert DevOps AI assistant. You ONLY answer questions \
related to DevOps, including: Kubernetes, Docker, CI/CD pipelines, cloud infrastructure \
(AWS, GCP, Azure), Terraform, Ansible, monitoring, observability, incident troubleshooting, \
networking, security hardening, databases, and related engineering practices.

If the user asks about ANYTHING unrelated to DevOps or software infrastructure \
(e.g. cooking, sports, entertainment, finance, personal advice, general trivia), \
you MUST respond with EXACTLY this message and nothing else:
"I'm a DevOps AI assistant and can only help with DevOps-related topics such as \
Kubernetes, Docker, CI/CD, cloud infrastructure, Terraform, monitoring, and incident \
troubleshooting. Please ask a DevOps-related question."

For valid DevOps questions, be concise, technical, and provide actionable advice:
1. Identify the problem clearly
2. Explain the root cause
3. Provide specific solutions
4. Suggest preventive measures"""


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        allowed, refusal_msg = guardrail.check(request.message)
        if not allowed:
            logger.info("Guardrail blocked non-DevOps question",
                        message_preview=request.message[:80])
            return ChatResponse(
                response=refusal_msg,
                conversation_id=request.conversation_id or str(uuid.uuid4()),
                sources=None,
                metadata={"guardrail": "blocked"},
            )

        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        context_docs = []
        if request.use_rag:
            search_results = await vector_store.search(request.message, top_k=3)
            context_docs = [result["content"] for result in search_results]
        
        if context_docs:
            response_text = await bedrock_service.generate_with_rag(
                query=request.message,
                context_documents=context_docs,
                system_prompt=SYSTEM_PROMPT
            )
            sources = [{"content": doc[:200] + "..."} for doc in context_docs]
        else:
            context_messages = []
            if request.context:
                context_messages = [
                    {"role": msg.role.value, "content": msg.content}
                    for msg in request.context
                ]
            
            response_text = await bedrock_service.generate_response(
                prompt=request.message,
                system_prompt=SYSTEM_PROMPT,
                context=context_messages
            )
            sources = None
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            sources=sources,
            metadata={"model": bedrock_service.model_id}
        )
        
    except Exception as e:
        logger.error("Chat error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    try:
        async def generate() -> AsyncGenerator[str, None]:
            try:
                context_messages = []
                if request.context:
                    context_messages = [
                        {"role": msg.role.value, "content": msg.content}
                        for msg in request.context
                    ]
                
                async for chunk in bedrock_service.stream_response(
                    prompt=request.message,
                    system_prompt=SYSTEM_PROMPT,
                    context=context_messages
                ):
                    yield f"data: {chunk}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error("Streaming error", error=str(e))
                yield f"data: Error: {str(e)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error("Chat stream error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-knowledge")
async def upload_knowledge(content: str, metadata: dict = None):
    try:
        documents = [{
            "content": content,
            "metadata": metadata or {},
            "timestamp": None
        }]
        
        success = await vector_store.add_documents(documents)
        
        if success:
            return {"status": "success", "message": "Knowledge uploaded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to upload knowledge")
            
    except Exception as e:
        logger.error("Upload knowledge error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
