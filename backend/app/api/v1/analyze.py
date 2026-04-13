from fastapi import APIRouter, HTTPException
import structlog

from app.models.schemas import RCARequest, RCAResponse, PodStatusRequest, PodStatusResponse
from app.services.bedrock_service import bedrock_service
from app.services.kubernetes_service import kubernetes_service

router = APIRouter()
logger = structlog.get_logger()


@router.post("/rca", response_model=RCAResponse)
async def root_cause_analysis(request: RCARequest):
    try:
        context_parts = [f"Incident Description:\n{request.incident_description}"]
        
        if request.logs:
            context_parts.append(f"\nLogs:\n{request.logs}")
        
        if request.metrics:
            metrics_str = "\n".join([f"- {k}: {v}" for k, v in request.metrics.items()])
            context_parts.append(f"\nMetrics:\n{metrics_str}")
        
        if request.events:
            events_str = "\n".join([str(e) for e in request.events])
            context_parts.append(f"\nEvents:\n{events_str}")
        
        if request.namespace and request.pod_name:
            try:
                pod_status = await kubernetes_service.get_pod_status(
                    namespace=request.namespace,
                    pod_name=request.pod_name
                )
                context_parts.append(f"\nPod Status:\n{pod_status}")
                
                events = await kubernetes_service.get_events(
                    namespace=request.namespace,
                    field_selector=f"involvedObject.name={request.pod_name}"
                )
                if events:
                    context_parts.append(f"\nKubernetes Events:\n{events}")
            except Exception as e:
                logger.warning("Failed to get pod info", error=str(e))
        
        context = "\n".join(context_parts)
        
        rca_prompt = f"""Perform a detailed Root Cause Analysis (RCA) for this incident.

{context}

Provide:
1. Root Cause: The primary underlying cause
2. Analysis: Detailed technical analysis
3. Contributing Factors: Other factors that contributed
4. Recommendations: How to fix this issue
5. Action Items: Specific steps to take
6. Confidence Score: Your confidence in this analysis (0-1)

Format your response as a structured analysis."""
        
        analysis_text = await bedrock_service.generate_response(
            prompt=rca_prompt,
            system_prompt="You are an expert SRE performing root cause analysis. Be thorough and technical.",
            max_tokens=3000
        )
        
        root_cause_prompt = f"""Based on this analysis, state the root cause in one clear sentence:

{analysis_text}"""
        
        root_cause = await bedrock_service.generate_response(
            prompt=root_cause_prompt,
            max_tokens=200
        )
        
        factors_prompt = f"""List the contributing factors (one per line):

{analysis_text}"""
        
        factors_text = await bedrock_service.generate_response(
            prompt=factors_prompt,
            max_tokens=500
        )
        contributing_factors = [f.strip() for f in factors_text.split('\n') if f.strip()]
        
        recommendations_prompt = f"""List specific recommendations (one per line):

{analysis_text}"""
        
        rec_text = await bedrock_service.generate_response(
            prompt=recommendations_prompt,
            max_tokens=500
        )
        recommendations = [r.strip() for r in rec_text.split('\n') if r.strip()]
        
        actions_prompt = f"""List immediate action items (one per line):

{analysis_text}"""
        
        actions_text = await bedrock_service.generate_response(
            prompt=actions_prompt,
            max_tokens=500
        )
        action_items = [a.strip() for a in actions_text.split('\n') if a.strip()]
        
        confidence_score = 0.8
        
        return RCAResponse(
            root_cause=root_cause.strip(),
            analysis=analysis_text,
            contributing_factors=contributing_factors[:10],
            recommendations=recommendations[:10],
            action_items=action_items[:10],
            confidence_score=confidence_score
        )
        
    except Exception as e:
        logger.error("RCA error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pod-status", response_model=PodStatusResponse)
async def analyze_pod_status(request: PodStatusRequest):
    try:
        status = await kubernetes_service.get_pod_status(
            namespace=request.namespace,
            pod_name=request.pod_name
        )
        
        analysis_prompt = f"""Analyze this Kubernetes pod status and explain any issues:

{status}

Provide:
1. Current state summary
2. Any problems identified
3. Recommended actions

Be concise and actionable."""
        
        analysis = await bedrock_service.generate_response(
            prompt=analysis_prompt,
            system_prompt="You are a Kubernetes expert analyzing pod health.",
            max_tokens=1000
        )
        
        return PodStatusResponse(
            status=status,
            analysis=analysis
        )
        
    except Exception as e:
        logger.error("Pod status analysis error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pods/{namespace}")
async def list_pods(namespace: str, label_selector: str = None):
    try:
        pods = await kubernetes_service.list_pods(
            namespace=namespace,
            label_selector=label_selector
        )
        
        return {
            "namespace": namespace,
            "pods": pods,
            "count": len(pods)
        }
        
    except Exception as e:
        logger.error("List pods error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{namespace}")
async def get_events(namespace: str):
    try:
        events = await kubernetes_service.get_events(namespace=namespace)
        
        return {
            "namespace": namespace,
            "events": events,
            "count": len(events)
        }
        
    except Exception as e:
        logger.error("Get events error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
