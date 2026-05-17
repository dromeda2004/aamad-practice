from __future__ import annotations

import hashlib

from app.schemas import (
    CandidatePoolItem,
    EvaluationRow,
    RequisitionInput,
    RecommendationRow,
)


def _seed(req: RequisitionInput) -> str:
    return hashlib.sha256(req.role_title.encode()).hexdigest()[:8]


def mock_research(req: RequisitionInput) -> dict:
    seed = _seed(req)
    skills_h = req.must_have_skills[:3]
    prefs = req.preferred_skills[:2]
    pool = []
    for i in range(3):
        cid = f"{seed}-c-{i + 1:03d}"
        name = ["Alex Rivera", "Jordan Kim", "Sam Patel"][i]
        matched = skills_h + (prefs if i == 1 else [])[:1]
        pool.append(
            CandidatePoolItem(
                candidate_id=cid,
                display_name=name,
                summary=(
                    f"{name}: aligns on {', '.join(skills_h[:2]) or 'role criteria'} "
                    f"for {req.role_title.strip()} ({req.experience_min_years}-{req.experience_max_years} YOE)."
                ),
                source="mock:deterministic",
                evidence=[
                    f"Matched skills: {', '.join(matched) or 'n/a'}",
                    (req.free_text_brief[:240] + "…")
                    if len(req.free_text_brief) > 240
                    else req.free_text_brief
                    if req.free_text_brief
                    else "Structured intake only (no free-text brief).",
                ],
                skills_matched=matched or ["role fit"],
            )
        )
    return {"candidate_pool": [p.model_dump() for p in pool]}


def mock_evaluate(req: RequisitionInput, pool: list[dict]) -> dict:
    evaluations = []
    for i, cand in enumerate(pool):
        cid = cand["candidate_id"]
        score = round(0.78 + 0.06 * i, 4)
        if score > 1.0:
            score = 1.0
        conf = "medium" if i == 1 else "high"
        evaluations.append(
            EvaluationRow(
                candidate_id=cid,
                score_normalized=score,
                rationale=(
                    "Strong alignment on must-have skills with supporting evidence snippets; "
                    "depth varies by candidate history."
                    if conf == "high"
                    else "Good fit with thinner evidence on breadth — flag for hiring manager QA."
                ),
                confidence=conf,  # type: ignore[arg-type]
                criteria_breakdown={
                    "Must_have_skills": min(5.0, 3 + score * 2),
                    "Impact": min(5.0, 2.5 + score * 2),
                    "Collaboration": min(5.0, 3 + score * 1.5),
                },
            )
        )
    return {"evaluations": [e.model_dump() for e in evaluations]}


def mock_recommend(
    req: RequisitionInput,
    pool: list[dict],
    evaluations: list[dict],
) -> dict:
    name_by_id = {p["candidate_id"]: p.get("display_name", "") for p in pool}
    ranked = sorted(
        evaluations,
        key=lambda x: float(x.get("score_normalized", 0)),
        reverse=True,
    )
    must = req.must_have_skills[:3]
    recs: list[RecommendationRow] = []
    for i, row in enumerate(ranked):
        cid = str(row["candidate_id"])
        # Mark as uncertain if confidence is NOT "high"
        uncertain = row.get("confidence") != "high"
        fs = float(row.get("score_normalized", 0.8))
        recs.append(
            RecommendationRow(
                rank=i + 1,
                candidate_id=cid,
                display_name=name_by_id.get(cid, f"Candidate {cid[-3:]}"),
                fit_score=fs,
                rationale=str(row.get("rationale", "See evaluation rationale.")),
                uncertainty=bool(uncertain),
                top_skills=(must or [])[:3] or ["culture add", "role execution"],
            )
        )
    return {"recommendations": [r.model_dump() for r in recs]}
