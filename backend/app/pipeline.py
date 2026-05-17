from __future__ import annotations

import asyncio
import logging
import traceback
from typing import Literal

from app import store as store_module
from app.crew_service import run_evaluate, run_recommend, run_research
from app.schemas import ApiErrorEnvelope, RunStage

logger = logging.getLogger(__name__)

StartPhase = Literal["researcher", "evaluator", "recommender"]


async def execute_pipeline(
    *,
    store: store_module.RunStore,
    run_id: str,
    start: StartPhase,
    notes: str | None = None,
) -> None:
    rec = await store.get(run_id)
    if rec is None:
        return

    req = rec.requisition
    trace = rec.trace_id

    async def fail(code: str, message: str, retryable: bool, action: str) -> None:
        await store.set_failed(
            run_id,
            error=ApiErrorEnvelope(
                error_code=code,
                message=message,
                retryable=retryable,
                suggested_action=f"{action} (notes: {notes!r})",
                trace_id=trace,
            ),
            preserve_partial=True,
        )

    logger.info(
        "pipeline start",
        extra={
            "run_id": run_id,
            "trace_id": trace,
            "start_phase": start,
            "notes": notes,
        },
    )

    try:
        if start == "researcher":
            await store.update(run_id, stage=RunStage.researching, error=None)
            logger.info(
                "agent start",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "researching",
                    "agent": "researcher",
                },
            )
            pool = run_research(req)
            await store.update(
                run_id, candidate_pool=pool, stage=RunStage.evaluating
            )
            logger.info(
                "agent complete",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "researching",
                    "agent": "researcher",
                },
            )

            await store.update(run_id, stage=RunStage.evaluating)
            logger.info(
                "agent start",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "evaluating",
                    "agent": "evaluator",
                },
            )
            evaluations = run_evaluate(req, pool)
            await store.update(
                run_id, evaluations=evaluations, stage=RunStage.recommending
            )
            logger.info(
                "agent complete",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "evaluating",
                    "agent": "evaluator",
                },
            )

            await store.update(run_id, stage=RunStage.recommending)
            logger.info(
                "agent start",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "recommending",
                    "agent": "recommender",
                },
            )
            recommendations = run_recommend(req, pool, evaluations)
            await store.update(
                run_id,
                recommendations=recommendations,
                stage=RunStage.awaiting_approval,
            )
            logger.info(
                "agent complete",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "recommending",
                    "agent": "recommender",
                },
            )
            return

        if start == "evaluator":
            latest = await store.get(run_id)
            if latest is None:
                return
            pool = latest.candidate_pool or []
            if len(pool) == 0:
                await fail(
                    "missing_pool",
                    "Cannot evaluate without a candidate pool.",
                    False,
                    "Rerun from researcher first.",
                )
                return

            await store.update(run_id, stage=RunStage.evaluating, error=None)
            logger.info(
                "agent start",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "evaluating",
                    "agent": "evaluator",
                },
            )
            evaluations = run_evaluate(req, pool)
            await store.update(
                run_id, evaluations=evaluations, stage=RunStage.recommending
            )
            logger.info(
                "agent complete",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "evaluating",
                    "agent": "evaluator",
                },
            )

            await store.update(run_id, stage=RunStage.recommending)
            logger.info(
                "agent start",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "recommending",
                    "agent": "recommender",
                },
            )
            recommendations = run_recommend(req, pool, evaluations)
            await store.update(
                run_id,
                recommendations=recommendations,
                stage=RunStage.awaiting_approval,
            )
            logger.info(
                "agent complete",
                extra={
                    "run_id": run_id,
                    "trace_id": trace,
                    "stage": "recommending",
                    "agent": "recommender",
                },
            )
            return

        # recommender-only
        latest = await store.get(run_id)
        if latest is None:
            return
        pool = latest.candidate_pool or []
        evaluations = latest.evaluations or []
        if len(pool) == 0 or len(evaluations) == 0:
            await fail(
                "missing_upstream",
                "Cannot recommend without pool and evaluations.",
                False,
                "Rerun from evaluator or researcher.",
            )
            return

        await store.update(run_id, stage=RunStage.recommending, error=None)
        logger.info(
            "agent start",
            extra={
                "run_id": run_id,
                "trace_id": trace,
                "stage": "recommending",
                "agent": "recommender",
            },
        )
        recommendations = run_recommend(req, pool, evaluations)
        await store.update(
            run_id,
            recommendations=recommendations,
            stage=RunStage.awaiting_approval,
        )
        logger.info(
            "agent complete",
            extra={
                "run_id": run_id,
                "trace_id": trace,
                "stage": "recommending",
                "agent": "recommender",
            },
        )
        logger.info(
            "pipeline complete",
            extra={
                "run_id": run_id,
                "trace_id": trace,
                "final_stage": "awaiting_approval",
            },
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.exception("pipeline failure run=%s", run_id)
        suggested = (
            "Set USE_MOCK_CREW=true to run deterministic mock crew, "
            "or configure OPENAI_API_KEY / model env vars.\n" + tb
        )
        await fail(
            "crew_pipeline_error",
            f"{type(e).__name__}: {e}",
            True,
            suggested,
        )


def schedule_pipeline(
    *,
    store: store_module.RunStore,
    run_id: str,
    start: StartPhase,
    notes: str | None = None,
) -> asyncio.Task[None]:
    async def runner() -> None:
        await execute_pipeline(store=store, run_id=run_id, start=start, notes=notes)

    task = asyncio.create_task(runner())
    asyncio.create_task(store.attach_bg_task(run_id, task))
    return task
