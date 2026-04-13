from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = None
    context: Optional[List[ChatMessage]] = None
    use_rag: bool = Field(default=True, description="Use RAG for context")
    stream: bool = Field(default=False, description="Stream response")


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class LogAnalysisRequest(BaseModel):
    source: str = Field(..., description="Log source: kubernetes, cloudwatch, or loki")
    namespace: Optional[str] = None
    pod_name: Optional[str] = None
    log_group: Optional[str] = None
    query: Optional[str] = None
    tail_lines: int = Field(default=100, description="Number of log lines to analyze")
    since_seconds: Optional[int] = None


class LogAnalysisResponse(BaseModel):
    analysis: str
    logs: str
    issues_found: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class CodeGenerationType(str, Enum):
    TERRAFORM = "terraform"
    KUBERNETES = "kubernetes"
    GITHUB_ACTIONS = "github_actions"
    HELM = "helm"
    DOCKERFILE = "dockerfile"


class CodeGenerationRequest(BaseModel):
    type: CodeGenerationType
    description: str = Field(..., description="What to generate")
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[str] = None


class CodeGenerationResponse(BaseModel):
    code: str
    filename: str
    explanation: str
    additional_files: Optional[List[Dict[str, str]]] = None


class RCARequest(BaseModel):
    incident_description: str
    logs: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    events: Optional[List[Dict[str, Any]]] = None
    namespace: Optional[str] = None
    pod_name: Optional[str] = None


class RCAResponse(BaseModel):
    root_cause: str
    analysis: str
    contributing_factors: List[str]
    recommendations: List[str]
    action_items: List[str]
    confidence_score: float


class PodStatusRequest(BaseModel):
    namespace: str
    pod_name: str


class PodStatusResponse(BaseModel):
    status: Dict[str, Any]
    analysis: Optional[str] = None


class DocumentUploadRequest(BaseModel):
    content: str
    metadata: Dict[str, Any]
    doc_type: str = Field(default="runbook", description="Type of document")


class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
    timestamp: datetime
