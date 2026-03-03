import time
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from .config import Settings
from .gateway import GatewayClient
from .models import NovelToScriptRequest, NovelToScriptResponse, StepResult, utc_now_iso
from .skills import SkillSpec


class NovelToScriptAgent:
    def __init__(
        self,
        settings: Settings,
        gateway: GatewayClient,
        skills: Dict[str, SkillSpec],
    ) -> None:
        self.settings = settings
        self.gateway = gateway
        self.skills = skills
        self.pipeline: List[Tuple[str, str]] = [
            ("novel-intake-parse", "Novel Intake Parse"),
            ("novel-story-synopsis-generate", "Story Synopsis"),
            ("novel-character-profile-generate", "Character Profiles"),
            ("novel-episode-outline-generate", "Episode Outline"),
            ("novel-full-script-generate", "Full Script Draft"),
        ]

    async def run(self, request: NovelToScriptRequest) -> NovelToScriptResponse:
        model = request.model or self.settings.default_model
        max_tokens = request.max_tokens or self.settings.default_max_tokens
        temperature = request.temperature
        if temperature is None:
            temperature = self.settings.default_temperature

        steps: List[StepResult] = []

        intake_started = time.perf_counter()
        intake_output = self._build_intake_output(request)
        steps.append(
            StepResult(
                step_id="novel-intake-parse",
                step_name="Novel Intake Parse",
                output=intake_output,
                model="local-rule",
                usage=None,
                latency_ms=self._latency_ms(intake_started),
            )
        )

        story_prompt = self._build_story_prompt(request, intake_output)
        story_output, story_usage, story_latency = await self._llm_step(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt=story_prompt,
        )
        steps.append(
            StepResult(
                step_id="novel-story-synopsis-generate",
                step_name="Story Synopsis",
                output=story_output,
                model=model,
                usage=story_usage,
                latency_ms=story_latency,
            )
        )

        character_prompt = self._build_character_prompt(request, story_output)
        character_output, character_usage, character_latency = await self._llm_step(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt=character_prompt,
        )
        steps.append(
            StepResult(
                step_id="novel-character-profile-generate",
                step_name="Character Profiles",
                output=character_output,
                model=model,
                usage=character_usage,
                latency_ms=character_latency,
            )
        )

        outline_prompt = self._build_outline_prompt(request, story_output, character_output)
        outline_output, outline_usage, outline_latency = await self._llm_step(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt=outline_prompt,
        )
        steps.append(
            StepResult(
                step_id="novel-episode-outline-generate",
                step_name="Episode Outline",
                output=outline_output,
                model=model,
                usage=outline_usage,
                latency_ms=outline_latency,
            )
        )

        full_script_prompt = self._build_full_script_prompt(
            request=request,
            story_output=story_output,
            character_output=character_output,
            outline_output=outline_output,
        )
        full_script_output, full_script_usage, full_script_latency = await self._llm_step(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt=full_script_prompt,
        )
        steps.append(
            StepResult(
                step_id="novel-full-script-generate",
                step_name="Full Script Draft",
                output=full_script_output,
                model=model,
                usage=full_script_usage,
                latency_ms=full_script_latency,
            )
        )

        return NovelToScriptResponse(
            request_id=f"req_{uuid4().hex}",
            agent_id=self.settings.agent_id,
            workflow_id=self.settings.workflow_id,
            model=model,
            created_at=utc_now_iso(),
            steps=steps,
            final_output=full_script_output,
        )

    async def _llm_step(
        self,
        *,
        model: str,
        max_tokens: int,
        temperature: Optional[float],
        prompt: str,
    ) -> Tuple[str, Optional[Dict[str, object]], int]:
        started = time.perf_counter()
        output, usage = await self.gateway.messages(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return output, usage, self._latency_ms(started)

    def _latency_ms(self, started: float) -> int:
        return int((time.perf_counter() - started) * 1000)

    def _build_intake_output(self, request: NovelToScriptRequest) -> str:
        preview = self._clip(request.novel_content, 800)
        episodes = (
            str(request.expected_episode_count)
            if request.expected_episode_count is not None
            else "unknown"
        )
        lines = [
            "[Novel Intake Summary]",
            f"novel_type: {request.novel_type.strip() or 'unknown'}",
            f"target_audience: {request.target_audience.strip() or 'unknown'}",
            f"expected_episode_count: {episodes}",
            f"content_length: {len(request.novel_content)}",
            "",
            "content_preview:",
            preview,
            "",
            "next_steps:",
            "1) Generate adaptation-ready story synopsis",
            "2) Generate character bible",
            "3) Generate episode outlines",
            "4) Generate full script draft",
        ]
        return "\n".join(lines).strip()

    def _build_story_prompt(self, request: NovelToScriptRequest, intake_output: str) -> str:
        skill_prompt = self._skill_prompt("novel-story-synopsis-generate")
        return (
            f"{skill_prompt}\n\n"
            "You are DreamWorks adaptation strategist.\n"
            f"Novel type: {request.novel_type}\n"
            f"Target audience: {request.target_audience}\n"
            f"Expected episodes: {request.expected_episode_count or 'unknown'}\n\n"
            "Intake summary:\n"
            f"{intake_output}\n\n"
            "Novel content:\n"
            f"{request.novel_content}\n\n"
            "Output in markdown with sections:\n"
            "1. Theme\n"
            "2. Core premise\n"
            "3. Main conflict\n"
            "4. Tone and style\n"
            "5. Adaptation opportunities\n"
            "6. Adaptation risks and mitigations"
        )

    def _build_character_prompt(self, request: NovelToScriptRequest, story_output: str) -> str:
        skill_prompt = self._skill_prompt("novel-character-profile-generate")
        return (
            f"{skill_prompt}\n\n"
            "You are DreamWorks character writer.\n"
            f"Target audience: {request.target_audience}\n\n"
            "Story synopsis:\n"
            f"{story_output}\n\n"
            "Output in markdown. For each core character include:\n"
            "- Name\n"
            "- Archetype\n"
            "- Goal\n"
            "- Motivation\n"
            "- Inner conflict\n"
            "- Relationship map\n"
            "- Growth arc\n"
            "- Dialogue style notes\n"
            "- Visual tags"
        )

    def _build_outline_prompt(
        self,
        request: NovelToScriptRequest,
        story_output: str,
        character_output: str,
    ) -> str:
        skill_prompt = self._skill_prompt("novel-episode-outline-generate")
        expected = request.expected_episode_count or 12
        return (
            f"{skill_prompt}\n\n"
            "You are DreamWorks head writer.\n"
            f"Expected episode count: {expected}\n\n"
            "Story synopsis:\n"
            f"{story_output}\n\n"
            "Character bible:\n"
            f"{character_output}\n\n"
            "Output in markdown. For each episode provide:\n"
            "- Episode title\n"
            "- A-plot / B-plot\n"
            "- Major turning points\n"
            "- Character progression\n"
            "- Cliffhanger\n"
            "Keep each episode concise and production-oriented."
        )

    def _build_full_script_prompt(
        self,
        *,
        request: NovelToScriptRequest,
        story_output: str,
        character_output: str,
        outline_output: str,
    ) -> str:
        skill_prompt = self._skill_prompt("novel-full-script-generate")
        return (
            f"{skill_prompt}\n\n"
            "You are DreamWorks screenplay room.\n"
            f"Novel type: {request.novel_type}\n"
            f"Target audience: {request.target_audience}\n\n"
            "Story synopsis:\n"
            f"{story_output}\n\n"
            "Character bible:\n"
            f"{character_output}\n\n"
            "Episode outline:\n"
            f"{outline_output}\n\n"
            "Output in markdown with:\n"
            "1) Episode-by-episode scene list\n"
            "2) Key dialogue samples\n"
            "3) Stage directions and pacing notes\n"
            "4) QA checklist for adaptation consistency"
        )

    def _clip(self, text: str, limit: int) -> str:
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return compact[: max(0, limit - 3)].rstrip() + "..."

    def _skill_prompt(self, skill_id: str) -> str:
        skill = self.skills.get(skill_id)
        if skill is None:
            raise RuntimeError(f"Required skill not found: {skill_id}")
        return skill.prompt_template
