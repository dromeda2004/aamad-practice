from __future__ import annotations

import os
import time
from typing import Callable

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.logging_config import configure_logging, get_logger

from app.pipeline import schedule_pipeline
from app.schemas import (
    ApiErrorEnvelope,
    CandidatePoolItem,
    CreateRunRequest,
    EvaluationRow,
    HealthResponse,
    RecommendationRow,
    RerunRequest,
    RunStage,
    WorkflowRunPayload,
)
from app.store import RunRecord, store

load_dotenv()

configure_logging()
logger = get_logger(__name__)
logger.info(
    "Application startup complete",
    extra={"environment": os.getenv("ENVIRONMENT", "development")},
)

app = FastAPI(
    title="TalentFlow AI",
    description="Recruitment Assistant API (MVP)",
    version="0.1.0",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> JSONResponse:
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", "")
    client_ip = request.client.host if request.client else "unknown"

    logger.info(
        "Request start",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": client_ip,
        },
    )

    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "Request complete",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
            },
        )
        return response
    except Exception:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.exception(
            "Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
            },
        )
        raise


def record_to_payload(rec: RunRecord) -> WorkflowRunPayload:
    cp = (
        [CandidatePoolItem.model_validate(x) for x in rec.candidate_pool]
        if rec.candidate_pool
        else None
    )
    ev = (
        [EvaluationRow.model_validate(x) for x in rec.evaluations]
        if rec.evaluations
        else None
    )
    recs = (
        [RecommendationRow.model_validate(x) for x in rec.recommendations]
        if rec.recommendations
        else None
    )
    err: ApiErrorEnvelope | None = rec.error
    return WorkflowRunPayload(
        run_id=rec.run_id,
        trace_id=rec.trace_id,
        stage=rec.stage,
        error=err,
        created_at=rec.created_at,
        candidate_pool=cp,
        evaluations=ev,
        recommendations=recs,
    )


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/api/v1/runs", response_model=WorkflowRunPayload)
async def create_run(body: CreateRunRequest) -> WorkflowRunPayload:
    req = body.requisition
    rec = await store.create_run(req)
    logger.info(
        "Run created",
        extra={
            "run_id": rec.run_id,
            "trace_id": rec.trace_id,
            "role_title": req.role_title,
            "location": req.location,
        },
    )
    schedule_pipeline(store=store, run_id=rec.run_id, start="researcher")
    refreshed = await store.get(rec.run_id)
    assert refreshed is not None
    return record_to_payload(refreshed)


@app.get("/api/v1/runs/{run_id}", response_model=WorkflowRunPayload)
async def get_run(run_id: str) -> WorkflowRunPayload:
    rec = await store.get(run_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return record_to_payload(rec)


@app.post("/api/v1/runs/{run_id}/rerun", response_model=WorkflowRunPayload)
async def rerun_run(run_id: str, body: RerunRequest) -> WorkflowRunPayload:
    rec = await store.get(run_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Run not found")

    fs = body.from_stage.value
    if fs == "researcher":
        await store.clear_for_rerun_from_researcher(run_id)
        schedule_pipeline(
            store=store, run_id=run_id, start="researcher", notes=body.notes
        )
    elif fs == "evaluator":
        await store.clear_for_rerun_from_evaluator(run_id)
        schedule_pipeline(
            store=store, run_id=run_id, start="evaluator", notes=body.notes
        )
    elif fs == "recommender":
        await store.clear_for_rerun_from_recommender(run_id)
        schedule_pipeline(
            store=store, run_id=run_id, start="recommender", notes=body.notes
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid from_stage")

    refreshed = await store.get(run_id)
    assert refreshed is not None
    return record_to_payload(refreshed)


@app.post("/api/v1/runs/{run_id}/approve", response_model=WorkflowRunPayload)
async def approve_run(run_id: str) -> WorkflowRunPayload:
    rec = await store.get(run_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if rec.stage != RunStage.awaiting_approval:
        raise HTTPException(
            status_code=400,
            detail="Run is not awaiting approval",
        )
    await store.update(run_id, stage=RunStage.approved, error=None)
    refreshed = await store.get(run_id)
    assert refreshed is not None
    return record_to_payload(refreshed)


@app.on_event("startup")
async def startup_log() -> None:
    mode = os.getenv("USE_MOCK_CREW", "auto")
    key = bool(os.getenv("OPENAI_API_KEY"))
    logger.info("USE_MOCK_CREW=%s OPENAI_API_KEY_set=%s", mode, key)
