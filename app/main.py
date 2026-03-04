from fastapi import FastAPI, HTTPException

from .agent import NovelToScriptAgent
from .config import settings
from .gateway import GatewayClient
from .models import ErrorResponse, NovelToScriptRequest, NovelToScriptResponse
from .skills import load_skills

app = FastAPI(
    title="agent-mgc-novel-script",
    version="0.1.0",
    description="Independent DreamWorks novel-to-script agent application.",
)

gateway_client = GatewayClient(
    base_url=settings.llm_service_base_url,
    api_style=settings.llm_service_api_style,
    auth_token=settings.llm_service_auth_token,
    auth_scheme=settings.llm_service_auth_scheme,
    timeout_seconds=settings.request_timeout_seconds,
)
skill_registry = load_skills(settings.skills_dir)
agent = NovelToScriptAgent(settings=settings, gateway=gateway_client, skills=skill_registry)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "agent_id": settings.agent_id,
        "workflow_id": settings.workflow_id,
        "skills_count": len(skill_registry),
        "llm_service_configured": gateway_client.is_configured(),
        "llm_service_base_url": settings.llm_service_base_url,
        "llm_service_source": settings.llm_service_source,
        "llm_service_api_style": settings.llm_service_api_style,
    }


@app.get("/v1/health")
async def health_v1() -> dict:
    return await health()


@app.get("/v1/models")
async def list_models() -> dict:
    try:
        return await gateway_client.list_models()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(
    "/v1/novel-to-script",
    response_model=NovelToScriptResponse,
    responses={502: {"model": ErrorResponse}},
)
async def run_novel_to_script(request: NovelToScriptRequest) -> NovelToScriptResponse:
    try:
        return await agent.run(request)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
