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
    base_url=settings.gateway_base_url,
    token=settings.gateway_token,
    anthropic_version=settings.gateway_anthropic_version,
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
        "gateway_configured": gateway_client.is_configured(),
        "gateway_base_url": settings.gateway_base_url,
    }


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
