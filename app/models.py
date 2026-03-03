from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class NovelToScriptRequest(BaseModel):
    novel_content: str = Field(min_length=1, max_length=200000)
    novel_type: str = Field(default="unknown", max_length=128)
    target_audience: str = Field(default="unknown", max_length=128)
    expected_episode_count: Optional[int] = Field(default=None, ge=1, le=500)
    model: Optional[str] = Field(default=None, min_length=1, max_length=128)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=16000)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)


class StepResult(BaseModel):
    step_id: str
    step_name: str
    output: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    latency_ms: int = 0


class NovelToScriptResponse(BaseModel):
    request_id: str
    agent_id: str
    workflow_id: str
    model: str
    created_at: str
    steps: List[StepResult]
    final_output: str


class ErrorResponse(BaseModel):
    error: str

