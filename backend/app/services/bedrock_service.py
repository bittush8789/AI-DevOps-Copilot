import boto3
import requests as http_requests
from typing import Dict, List, Optional, AsyncGenerator
import structlog
from app.core.config import settings

logger = structlog.get_logger()


def _build_converse_messages(context: Optional[List[Dict]], prompt: str) -> List[Dict]:
    messages = []
    if context:
        for msg in context:
            content = msg.get("content", "")
            if isinstance(content, str):
                content = [{"text": content}]
            messages.append({"role": msg["role"], "content": content})
    messages.append({"role": "user", "content": [{"text": prompt}]})
    return messages


class BedrockService:
    def __init__(self):
        self.model_id = settings.BEDROCK_MODEL_ID
        self.region = settings.AWS_REGION
        self.use_api_key = bool(settings.BEDROCK_API_KEY)

        if not self.use_api_key:
            client_kwargs = {
                "service_name": "bedrock-runtime",
                "region_name": self.region,
            }
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                client_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                client_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            self.boto_client = boto3.client(**client_kwargs)
        else:
            self.boto_client = None

        logger.info("BedrockService initialized",
                    model=self.model_id,
                    region=self.region,
                    auth="api_key" if self.use_api_key else "iam")

    def _http_converse(self, messages: List[Dict], inference_config: Dict,
                       system: Optional[str] = None) -> Dict:
        url = (f"https://bedrock-runtime.{self.region}.amazonaws.com"
               f"/model/{self.model_id}/converse")
        payload = {"messages": messages, "inferenceConfig": inference_config}
        if system:
            payload["system"] = [{"text": system}]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.BEDROCK_API_KEY}",
        }
        resp = http_requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def _boto_converse(self, messages: List[Dict], inference_config: Dict,
                       system: Optional[str] = None) -> Dict:
        kwargs = {
            "modelId": self.model_id,
            "messages": messages,
            "inferenceConfig": inference_config,
        }
        if system:
            kwargs["system"] = [{"text": system}]
        return self.boto_client.converse(**kwargs)

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None,
        context: Optional[List[Dict]] = None,
    ) -> str:
        try:
            max_tokens = max_tokens or settings.BEDROCK_MAX_TOKENS
            temperature = temperature or settings.BEDROCK_TEMPERATURE
            messages = _build_converse_messages(context, prompt)
            inference_config = {"maxTokens": max_tokens, "temperature": temperature}

            if self.use_api_key:
                response = self._http_converse(messages, inference_config, system_prompt)
            else:
                response = self._boto_converse(messages, inference_config, system_prompt)

            return response["output"]["message"]["content"][0]["text"]

        except Exception as e:
            logger.error("Bedrock converse error", error=str(e))
            raise Exception(f"Failed to generate response: {str(e)}")

    async def stream_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None,
        context: Optional[List[Dict]] = None,
    ) -> AsyncGenerator[str, None]:
        try:
            max_tokens = max_tokens or settings.BEDROCK_MAX_TOKENS
            temperature = temperature or settings.BEDROCK_TEMPERATURE
            messages = _build_converse_messages(context, prompt)
            inference_config = {"maxTokens": max_tokens, "temperature": temperature}

            if self.use_api_key:
                response = self._http_converse(messages, inference_config, system_prompt)
                text = response["output"]["message"]["content"][0]["text"]
                yield text
            else:
                kwargs = {
                    "modelId": self.model_id,
                    "messages": messages,
                    "inferenceConfig": inference_config,
                }
                if system_prompt:
                    kwargs["system"] = [{"text": system_prompt}]
                response = self.boto_client.converse_stream(**kwargs)
                stream = response.get("stream")
                if stream:
                    for event in stream:
                        if "contentBlockDelta" in event:
                            delta = event["contentBlockDelta"].get("delta", {})
                            text = delta.get("text", "")
                            if text:
                                yield text

        except Exception as e:
            logger.error("Bedrock stream error", error=str(e))
            raise Exception(f"Failed to stream response: {str(e)}")

    async def generate_with_rag(
        self,
        query: str,
        context_documents: List[str],
        system_prompt: Optional[str] = None,
    ) -> str:
        context_text = "\n\n".join([
            f"Document {i+1}:\n{doc}"
            for i, doc in enumerate(context_documents)
        ])

        enhanced_prompt = f"""Based on the following context documents, please answer the question.

Context:
{context_text}

Question: {query}

Please provide a detailed answer based on the context provided. If the context doesn't contain enough information, acknowledge that and provide the best answer you can."""

        return await self.generate_response(
            prompt=enhanced_prompt,
            system_prompt=system_prompt,
        )


bedrock_service = BedrockService()
