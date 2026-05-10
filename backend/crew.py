"""
TalentFlow AI — CrewAI wiring for the Application Crew (researcher / evaluator / recommender).

Externalized agent + task expectation copy lives in backend/config/.
Sequential mini-crews (one agent, one task) are built per invocation from `run_*` helpers.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent
_AGENTS_YAML = ROOT_DIR / "config" / "agents.yaml"
_TASKS_YAML = ROOT_DIR / "config" / "tasks.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_agents_config() -> dict[str, dict[str, str]]:
    data = _load_yaml(_AGENTS_YAML).get("agents", {})
    if not isinstance(data, dict):
        raise ValueError("Invalid agents.yaml")
    return data  # type: ignore[return-value]


def load_tasks_config() -> dict[str, dict[str, str]]:
    data = _load_yaml(_TASKS_YAML).get("tasks", {})
    if not isinstance(data, dict):
        raise ValueError("Invalid tasks.yaml")
    return data  # type: ignore[return-value]


def _build_llm(model: str | None):
    """Explicit LLM wiring when CREW_MODEL/OPENAI_MODEL is set."""
    if not model:
        return None
    try:
        from crewai import LLM  # type: ignore
    except Exception:  # pragma: no cover
        logger.warning("crewai LLM helper unavailable — using CrewAI Agent defaults.")
        return None
    try:
        return LLM(model=model)
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to instantiate LLM(%s): %s", model, exc)
        return None


def _make_crew(
    *,
    agent_key: str,
    task_key: str,
    description: str,
    max_rpm: int,
    max_iter: int,
    model: str | None,
) -> Any:
    from crewai import Agent, Crew, Process, Task  # type: ignore

    agents_cfg = load_agents_config()
    tasks_cfg = load_tasks_config()
    if agent_key not in agents_cfg:
        raise KeyError(f"Unknown agent '{agent_key}'")
    if task_key not in tasks_cfg:
        raise KeyError(f"Unknown task '{task_key}'")

    meta = agents_cfg[agent_key]
    task_expect = tasks_cfg[task_key]["expected_output"]
    llm = _build_llm(model)

    kwargs: dict[str, object] = {
        "role": meta["role"],
        "goal": meta["goal"],
        "backstory": meta["backstory"],
        "allow_delegation": False,
    }
    if llm is not None:
        kwargs["llm"] = llm
    agent = Agent(**kwargs)  # type: ignore[arg-type]
    task = Task(
        description=description.strip(),
        expected_output=task_expect.strip(),
        agent=agent,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        memory=False,
        max_rpm=max_rpm,
        verbose=False,
    )
    if hasattr(task, "max_iter"):
        setattr(task, "max_iter", max_iter)
    return crew


def _kickoff_as_text(crew: Any) -> str:
    result = crew.kickoff()
    if hasattr(result, "raw"):
        return str(result.raw)
    return str(result)


def run_research_llm(*, requisition: dict[str, Any], max_rpm: int, max_iter: int, model: str | None) -> str:
    desc = f"""
You must return VALID JSON ONLY (no Markdown).

REQUISITION (JSON):
{json.dumps(requisition, ensure_ascii=False, indent=2)}

Produce:
{{ "candidate_pool": [ ... ] }}

Rules:
- 3–7 candidates unless the role is hyper-specialized; then still return at least 3 with honest caveats.
- Each candidate MUST include candidate_id, display_name, summary, source, evidence[], skills_matched[].
"""
    crew = _make_crew(
        agent_key="researcher",
        task_key="research",
        description=desc,
        max_rpm=max_rpm,
        max_iter=max_iter,
        model=model,
    )
    logger.info("CrewAI kickoff: research stage")
    return _kickoff_as_text(crew)


def run_evaluator_llm(
    *,
    requisition: dict[str, Any],
    candidate_pool: list[dict[str, Any]],
    max_rpm: int,
    max_iter: int,
    model: str | None,
) -> str:
    desc = f"""
You must return VALID JSON ONLY (no Markdown).

REQUISITION (JSON):
{json.dumps(requisition, ensure_ascii=False, indent=2)}

CANDIDATE_POOL (JSON):
{json.dumps(candidate_pool, ensure_ascii=False, indent=2)}

Produce:
{{ "evaluations": [ ... ] }}

Rules:
- score_normalized MUST be between 0 and 1 inclusive.
- confidence MUST be exactly one of: high, medium, low.
- Include rationale for each candidate tied to criteria.
"""
    crew = _make_crew(
        agent_key="evaluator",
        task_key="evaluate",
        description=desc,
        max_rpm=max_rpm,
        max_iter=max_iter,
        model=model,
    )
    logger.info("CrewAI kickoff: evaluate stage")
    return _kickoff_as_text(crew)


def run_recommender_llm(
    *,
    requisition: dict[str, Any],
    candidate_pool: list[dict[str, Any]],
    evaluations: list[dict[str, Any]],
    max_rpm: int,
    max_iter: int,
    model: str | None,
) -> str:
    desc = f"""
You must return VALID JSON ONLY (no Markdown).

REQUISITION (JSON):
{json.dumps(requisition, ensure_ascii=False, indent=2)}

CANDIDATE_POOL (JSON):
{json.dumps(candidate_pool, ensure_ascii=False, indent=2)}

EVALUATIONS (JSON):
{json.dumps(evaluations, ensure_ascii=False, indent=2)}

Produce:
{{ "recommendations": [ ... ] }}

Rules:
- rank starts at 1 and increases sequentially.
- fit_score aligns with evaluator scores but may be adjusted slightly — explain rationale.
- uncertainty MUST be boolean.
"""
    crew = _make_crew(
        agent_key="recommender",
        task_key="recommend",
        description=desc,
        max_rpm=max_rpm,
        max_iter=max_iter,
        model=model,
    )
    logger.info("CrewAI kickoff: recommend stage")
    return _kickoff_as_text(crew)
