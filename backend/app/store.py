from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.schemas import ApiErrorEnvelope, RequisitionInput, RunStage


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class RunRecord:
    run_id: str
    trace_id: str
    stage: RunStage
    requisition: RequisitionInput
    created_at: str
    candidate_pool: Optional[list[dict]] = None
    evaluations: Optional[list[dict]] = None
    recommendations: Optional[list[dict]] = None
    error: Optional[ApiErrorEnvelope] = None
    bg_task: Optional[asyncio.Task[None]] = field(default=None, repr=False)


class RunStore:
    """In-memory store (MVP — no database per @backend.eng)."""

    def __init__(self) -> None:
        self._runs: dict[str, RunRecord] = {}
        self._lock = asyncio.Lock()

    async def create_run(self, req: RequisitionInput) -> RunRecord:
        run_id = str(uuid.uuid4())
        trace_id = f"trace-{run_id.split('-', 1)[0]}"
        rec = RunRecord(
            run_id=run_id,
            trace_id=trace_id,
            stage=RunStage.researching,
            requisition=req,
            created_at=_iso_now(),
        )
        async with self._lock:
            self._runs[run_id] = rec
        return rec

    async def get(self, run_id: str) -> Optional[RunRecord]:
        async with self._lock:
            return self._runs.get(run_id)

    async def update(
        self,
        run_id: str,
        *,
        stage: RunStage | None = None,
        candidate_pool: list[dict] | None = None,
        evaluations: list[dict] | None = None,
        recommendations: list[dict] | None = None,
        error: ApiErrorEnvelope | None = None,
    ) -> None:
        async with self._lock:
            r = self._runs.get(run_id)
            if not r:
                return
            if stage is not None:
                r.stage = stage
            if candidate_pool is not None:
                r.candidate_pool = candidate_pool
            if evaluations is not None:
                r.evaluations = evaluations
            if recommendations is not None:
                r.recommendations = recommendations
            if error is not None:
                r.error = error

    async def set_failed(
        self,
        run_id: str,
        *,
        error: ApiErrorEnvelope,
        preserve_partial: bool = True,
    ) -> None:
        async with self._lock:
            r = self._runs.get(run_id)
            if not r:
                return
            r.stage = RunStage.failed
            if not preserve_partial:
                r.candidate_pool = None
                r.evaluations = None
                r.recommendations = None
            r.error = error

    async def clear_for_rerun_from_researcher(self, run_id: str) -> None:
        async with self._lock:
            r = self._runs.get(run_id)
            if not r:
                return
            r.candidate_pool = None
            r.evaluations = None
            r.recommendations = None
            r.error = None

    async def clear_for_rerun_from_evaluator(self, run_id: str) -> None:
        async with self._lock:
            r = self._runs.get(run_id)
            if not r:
                return
            r.evaluations = None
            r.recommendations = None
            r.error = None

    async def clear_for_rerun_from_recommender(self, run_id: str) -> None:
        async with self._lock:
            r = self._runs.get(run_id)
            if not r:
                return
            r.recommendations = None
            r.error = None

    async def attach_bg_task(self, run_id: str, task: asyncio.Task[None]) -> None:
        async with self._lock:
            r = self._runs.get(run_id)
            if not r:
                return
            r.bg_task = task


store = RunStore()
