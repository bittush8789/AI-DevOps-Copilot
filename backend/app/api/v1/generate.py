from fastapi import APIRouter, HTTPException
import structlog

from app.models.schemas import CodeGenerationRequest, CodeGenerationResponse, CodeGenerationType
from app.services.bedrock_service import bedrock_service

router = APIRouter()
logger = structlog.get_logger()


GENERATION_PROMPTS = {
    CodeGenerationType.TERRAFORM: """Generate production-ready Terraform code for: {description}

Requirements:
- Use best practices and latest Terraform syntax
- Include variables and outputs
- Add comments explaining key configurations
- Follow naming conventions
- Include provider configuration if needed

{context}

Generate the complete Terraform code:""",

    CodeGenerationType.KUBERNETES: """Generate production-ready Kubernetes YAML manifests for: {description}

Requirements:
- Use latest Kubernetes API versions
- Include resource limits and requests
- Add health checks (liveness/readiness probes)
- Follow security best practices
- Include labels and annotations
- Use proper naming conventions

{context}

Generate the complete Kubernetes manifests:""",

    CodeGenerationType.GITHUB_ACTIONS: """Generate a GitHub Actions workflow for: {description}

Requirements:
- Use latest GitHub Actions syntax
- Include proper triggers
- Add caching where appropriate
- Include error handling
- Follow best practices for CI/CD
- Add comments for clarity

{context}

Generate the complete workflow YAML:""",

    CodeGenerationType.HELM: """Generate a Helm chart for: {description}

Requirements:
- Include Chart.yaml, values.yaml, and templates
- Use Helm best practices
- Add configurable values
- Include NOTES.txt with usage instructions
- Follow naming conventions

{context}

Generate the Helm chart files:""",

    CodeGenerationType.DOCKERFILE: """Generate a production-ready Dockerfile for: {description}

Requirements:
- Use multi-stage builds if appropriate
- Minimize image size
- Follow security best practices
- Use specific version tags
- Add health checks
- Optimize layer caching

{context}

Generate the complete Dockerfile:"""
}


@router.post("/", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    try:
        template = GENERATION_PROMPTS.get(request.type)
        if not template:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown generation type: {request.type}"
            )
        
        context = ""
        if request.context:
            context = f"Additional context:\n{request.context}"
        
        if request.parameters:
            context += f"\n\nParameters:\n"
            for key, value in request.parameters.items():
                context += f"- {key}: {value}\n"
        
        prompt = template.format(
            description=request.description,
            context=context
        )
        
        code = await bedrock_service.generate_response(
            prompt=prompt,
            system_prompt="You are an expert DevOps engineer. Generate clean, production-ready code.",
            max_tokens=4096
        )
        
        explanation_prompt = f"""Briefly explain what this code does and how to use it:

{code}

Provide a concise explanation (2-3 paragraphs):"""
        
        explanation = await bedrock_service.generate_response(
            prompt=explanation_prompt,
            max_tokens=500
        )
        
        filename_map = {
            CodeGenerationType.TERRAFORM: "main.tf",
            CodeGenerationType.KUBERNETES: "deployment.yaml",
            CodeGenerationType.GITHUB_ACTIONS: ".github/workflows/main.yml",
            CodeGenerationType.HELM: "Chart.yaml",
            CodeGenerationType.DOCKERFILE: "Dockerfile"
        }
        
        filename = filename_map.get(request.type, "generated.txt")
        
        return CodeGenerationResponse(
            code=code,
            filename=filename,
            explanation=explanation,
            additional_files=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Code generation error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/terraform")
async def generate_terraform(description: str, context: str = None):
    request = CodeGenerationRequest(
        type=CodeGenerationType.TERRAFORM,
        description=description,
        context=context
    )
    return await generate_code(request)


@router.post("/kubernetes")
async def generate_kubernetes(description: str, context: str = None):
    request = CodeGenerationRequest(
        type=CodeGenerationType.KUBERNETES,
        description=description,
        context=context
    )
    return await generate_code(request)


@router.post("/github-actions")
async def generate_github_actions(description: str, context: str = None):
    request = CodeGenerationRequest(
        type=CodeGenerationType.GITHUB_ACTIONS,
        description=description,
        context=context
    )
    return await generate_code(request)
