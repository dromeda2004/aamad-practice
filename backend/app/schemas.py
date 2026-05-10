from __future__ import annotations

from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


class EmploymentType(str, Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    intern = "intern"


class RequisitionInput(BaseModel):
    role_title: str = Field(..., min_length=1)
    must_have_skills: list[str] = Field(..., min_length=1)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_min_years: int = Field(0, ge=0, le=40)
    experience_max_years: int = Field(40, ge=0, le=40)
    location: str = ""
    employment_type: Optional[Union[EmploymentType, Literal[""]]] = None
    free_text_brief: str = ""

    @field_validator("must_have_skills")
    @classmethod
    def strip_skills(cls, v: list[str]) -> list[str]:
        return [s.strip() for s in v if s and s.strip()]

    @field_validator("employment_type", mode="before")
    @classmethod
    def empty_employment(cls, v: object) -> object:
        if v == "":
            return None
        return v


class RunStage(str, Enum):
    pending = "pending"
    researching = "researching"
    evaluating = "evaluating"
    recommending = "recommending"
    awaiting_approval = "awaiting_approval"
    approved = "approved"
    failed = "failed"
    needs_clarification = "needs_clarification"


class CandidatePoolItem(BaseModel):
    candidate_id: str
    display_name: str
    summary: str
    source: Optional[str] = None
    evidence: Optional[list[str]] = None
    skills_matched: Optional[list[str]] = None


class EvaluationRow(BaseModel):
    candidate_id: str
    score_normalized: float = Field(..., ge=0, le=1)
    rationale: str
    confidence: Literal["high", "medium", "low"]
    criteria_breakdown: Optional[dict[str, float]] = None


class RecommendationRow(BaseModel):
    rank: int = Field(..., ge=1)
    candidate_id: str
    display_name: str
    fit_score: float = Field(..., ge=0, le=1)
    rationale: str
    uncertainty: bool
    top_skills: list[str] = Field(default_factory=list)


class ApiErrorEnvelope(BaseModel):
    error_code: str
    message: str
    retryable: Optional[bool] = None
    suggested_action: Optional[str] = None
    trace_id: Optional[str] = None


class WorkflowRunPayload(BaseModel):
    run_id: str
    trace_id: Optional[str] = None
    stage: RunStage
    error: Optional[ApiErrorEnvelope] = None
    created_at: Optional[str] = None
    candidate_pool: Optional[list[CandidatePoolItem]] = None
    evaluations: Optional[list[EvaluationRow]] = None
    recommendations: Optional[list[RecommendationRow]] = None


class CreateRunRequest(BaseModel):
    requisition: RequisitionInput


class RerunFromStage(str, Enum):
    researcher = "researcher"
    evaluator = "evaluator"
    recommender = "recommender"


class RerunRequest(BaseModel):
    from_stage: RerunFromStage
    notes: Optional[str] = None


class ApproveBody(BaseModel):
    """Frontend sends {} — accept arbitrary empty object."""

    model_config = {"extra": "allow"}


class HealthResponse(BaseModel):
    status: str = "ok"
