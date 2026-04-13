from fastapi import APIRouter, HTTPException
import structlog

from app.models.schemas import LogAnalysisRequest, LogAnalysisResponse
from app.services.bedrock_service import bedrock_service
from app.services.kubernetes_service import kubernetes_service

router = APIRouter()
logger = structlog.get_logger()


@router.post("/analyze", response_model=LogAnalysisResponse)
async def analyze_logs(request: LogAnalysisRequest):
    try:
        logs = ""
        
        if request.source == "kubernetes":
            if not request.namespace or not request.pod_name:
                raise HTTPException(
                    status_code=400,
                    detail="namespace and pod_name required for Kubernetes logs"
                )
            
            logs = await kubernetes_service.get_pod_logs(
                namespace=request.namespace,
                pod_name=request.pod_name,
                tail_lines=request.tail_lines,
                since_seconds=request.since_seconds
            )
        
        elif request.source == "cloudwatch":
            raise HTTPException(
                status_code=501,
                detail="CloudWatch integration coming soon"
            )
        
        elif request.source == "loki":
            raise HTTPException(
                status_code=501,
                detail="Loki integration coming soon"
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown log source: {request.source}"
            )
        
        analysis_prompt = f"""Analyze the following logs and provide:
1. Summary of what's happening
2. Any errors or issues found
3. Specific recommendations to fix issues
4. Preventive measures

Logs:
{logs}

Provide a structured analysis."""
        
        analysis = await bedrock_service.generate_response(
            prompt=analysis_prompt,
            system_prompt="You are an expert at analyzing system logs and identifying issues."
        )
        
        issues_prompt = f"""From these logs, list only the specific errors or issues found (one per line):
{logs}"""
        
        issues_text = await bedrock_service.generate_response(
            prompt=issues_prompt,
            max_tokens=500
        )
        issues = [i.strip() for i in issues_text.split('\n') if i.strip()]
        
        recommendations_prompt = f"""Based on these logs, provide specific actionable recommendations (one per line):
{logs}"""
        
        rec_text = await bedrock_service.generate_response(
            prompt=recommendations_prompt,
            max_tokens=500
        )
        recommendations = [r.strip() for r in rec_text.split('\n') if r.strip()]
        
        return LogAnalysisResponse(
            analysis=analysis,
            logs=logs[:1000] + "..." if len(logs) > 1000 else logs,
            issues_found=issues[:10],
            recommendations=recommendations[:10],
            metadata={
                "source": request.source,
                "namespace": request.namespace,
                "pod_name": request.pod_name,
                "lines_analyzed": len(logs.split('\n'))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Log analysis error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pods/{namespace}/{pod_name}")
async def get_pod_logs(namespace: str, pod_name: str, tail_lines: int = 100):
    try:
        logs = await kubernetes_service.get_pod_logs(
            namespace=namespace,
            pod_name=pod_name,
            tail_lines=tail_lines
        )
        
        return {
            "namespace": namespace,
            "pod_name": pod_name,
            "logs": logs
        }
        
    except Exception as e:
        logger.error("Get pod logs error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
