from __future__ import annotations

import logging
import os

from app.json_extract import extract_json_object
from app.mock_crew import mock_evaluate, mock_recommend, mock_research
from app.schemas import (
    CandidatePoolItem,
    EvaluationRow,
    RecommendationRow,
    RequisitionInput,
)

logger = logging.getLogger(__name__)


def _crew_runtime_params() -> tuple[int, int, str | None]:
    max_rpm = int(os.getenv("CREW_MAX_RPM", "10"))
    max_iter = min(12, int(os.getenv("CREW_MAX_ITER", "12")))
    model = os.getenv("OPENAI_MODEL") or os.getenv("CREW_MODEL") or None
    return max_rpm, max_iter, model


def should_use_mock_crew() -> bool:
    mode = (os.getenv("USE_MOCK_CREW") or "auto").strip().lower()
    has_key = bool(os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_KEY"))
    if mode in ("1", "true", "yes"):
        return True
    if mode in ("0", "false", "no"):
        return False
    # auto
    return not has_key


def run_research(requisition: RequisitionInput) -> list[dict]:
    if should_use_mock_crew():
        logger.info(
            "Using mock crew",
            extra={"crew_stage": "research", "use_mock": True},
        )
        out = mock_research(requisition)
        return [dict(x) for x in out["candidate_pool"]]

    from crew import run_research_llm

    max_rpm, max_iter, model = _crew_runtime_params()
    logger.info(
        "Using LLM crew",
        extra={"crew_stage": "research", "use_mock": False, "model": model},
    )
    text = run_research_llm(
        requisition=requisition.model_dump(),
        max_rpm=max_rpm,
        max_iter=max_iter,
        model=model,
    )
    data = extract_json_object(text)
    pool_raw = data.get("candidate_pool")
    if not isinstance(pool_raw, list):
        raise ValueError("research output missing candidate_pool array")
    validated = [CandidatePoolItem.model_validate(x).model_dump() for x in pool_raw]
    return validated


def run_evaluate(requisition: RequisitionInput, pool: list[dict]) -> list[dict]:
    if should_use_mock_crew():
        logger.info(
            "Using mock crew",
            extra={"crew_stage": "evaluate", "use_mock": True},
        )
        out = mock_evaluate(requisition, pool)
        return [dict(x) for x in out["evaluations"]]

    from crew import run_evaluator_llm

    max_rpm, max_iter, model = _crew_runtime_params()
    logger.info(
        "Using LLM crew",
        extra={"crew_stage": "evaluate", "use_mock": False, "model": model},
    )
    text = run_evaluator_llm(
        requisition=requisition.model_dump(),
        candidate_pool=pool,
        max_rpm=max_rpm,
        max_iter=max_iter,
        model=model,
    )
    data = extract_json_object(text)
    ev_raw = data.get("evaluations")
    if not isinstance(ev_raw, list):
        raise ValueError("evaluate output missing evaluations array")
    validated = [EvaluationRow.model_validate(x).model_dump() for x in ev_raw]
    return validated


def run_recommend(
    requisition: RequisitionInput,
    pool: list[dict],
    evaluations: list[dict],
) -> list[dict]:
    if should_use_mock_crew():
        logger.info(
            "Using mock crew",
            extra={"crew_stage": "recommend", "use_mock": True},
        )
        out = mock_recommend(requisition, pool, evaluations)
        return [dict(x) for x in out["recommendations"]]

    from crew import run_recommender_llm

    max_rpm, max_iter, model = _crew_runtime_params()
    logger.info(
        "Using LLM crew",
        extra={"crew_stage": "recommend", "use_mock": False, "model": model},
    )
    text = run_recommender_llm(
        requisition=requisition.model_dump(),
        candidate_pool=pool,
        evaluations=evaluations,
        max_rpm=max_rpm,
        max_iter=max_iter,
        model=model,
    )
    data = extract_json_object(text)
    raw = data.get("recommendations")
    if not isinstance(raw, list):
        raise ValueError("recommend output missing recommendations array")
    validated = [RecommendationRow.model_validate(x).model_dump() for x in raw]
    return validated
