# Market Requirements Document (MRD)

## Document Control
- Product: Recruitment Assistant Application
- Working Name: TalentFlow AI
- Version: 1.0
- Date: 2026-05-08
- Owner Persona: `@product-mgr`
- Runtime Intent: CrewAI-based multi-agent workflow

## Executive Summary
Recruitment teams spend disproportionate time on repetitive, low-leverage work: drafting and tuning job descriptions, sourcing candidates, screening resumes, scheduling interviews, and maintaining stakeholder communication. Existing ATS tools centralize data but often do not deliver proactive intelligence or coordinated automation across the full hiring lifecycle.

This MRD defines a market-ready opportunity for a CrewAI-powered Recruitment Assistant that coordinates specialized agents to accelerate time-to-hire, improve candidate quality, and reduce recruiter workload. The product targets SMB and mid-market organizations with lean talent teams that need enterprise-grade hiring outcomes without enterprise-scale headcount.

The primary opportunity is not replacing recruiters, but augmenting them with transparent, controllable multi-agent workflows that keep humans in decision-critical steps while automating orchestration and analysis.

## Problem Statement
Recruiting operations face a persistent execution gap:
- Sourcing and screening are labor intensive and inconsistent across recruiters.
- Hiring managers often receive delayed or low-signal shortlists.
- Candidate communication quality varies and drops during peak hiring cycles.
- Funnel analytics are fragmented across ATS, spreadsheets, and messaging tools.

These issues create longer time-to-fill, higher cost-per-hire, and avoidable candidate drop-off.

### Why Manual Candidate Sourcing and Evaluation Is Inefficient
- High time cost per requisition: recruiters repeatedly perform search, profile review, and outreach steps manually.
- Inconsistent candidate assessment: evaluation quality varies by recruiter workload, experience, and subjective judgment.
- Fragmented systems and context switching: data lives across ATS, job boards, spreadsheets, and inboxes, slowing decisions.
- Delayed stakeholder feedback loops: hiring managers receive updates late, which extends shortlist and interview timelines.
- Limited scalability under high volume: manual workflows degrade quickly when open requisitions and applicant counts increase.

## Target Market
### Primary Segment
- SMB and mid-market companies (50-2,000 employees)
- Talent teams with 1-20 recruiters
- Knowledge-worker hiring (engineering, product, operations, sales)
- Regions: North America first, then UK/EU expansion

### Secondary Segment
- Recruiting agencies handling high-volume requisitions
- Internal recruiting COEs in larger enterprises piloting AI-assisted workflows

### Ideal Customer Profile (ICP)
- Uses an ATS (Greenhouse/Lever/Workable/Ashby or equivalent)
- Has measurable hiring SLAs and recruiter productivity goals
- Open to AI-assisted drafting and ranking with auditability requirements

## Target Users
### Target User 1: Recruiter (Primary User)
- Goals: fill roles faster with better candidate quality
- Pain points: repetitive sourcing/screening, context switching, communication overhead
- Success criteria: fewer manual steps, faster qualified shortlist generation

### Target User 2: Hiring Manager (Decision Stakeholder)
- Goals: receive high-quality candidates aligned with role needs
- Pain points: noisy candidate pipelines, delayed updates
- Success criteria: better fit, fewer interview loops, visibility into funnel status

### Target User 3: TA Leader / Head of People (Economic Buyer)
- Goals: improve hiring efficiency, quality, and reporting
- Pain points: limited team bandwidth, inconsistent recruiter performance
- Success criteria: reduced time-to-fill and cost-per-hire, improved hiring predictability

### Target User 4: Candidate (Indirect User)
- Goals: clear communication and fair evaluation experience
- Pain points: long response times, unclear process steps
- Success criteria: timely updates, professional interactions

## Jobs-to-be-Done
- When opening a role, recruiters need high-quality role briefs and sourcing plans quickly.
- When pipelines are large, recruiters need consistent initial screening and ranking support.
- When coordinating interviews, teams need automated scheduling and timely communication.
- When reviewing performance, TA leaders need funnel insights and bottleneck diagnosis.

## Market Opportunity
### Value Hypothesis
A multi-agent recruitment assistant can deliver measurable business value by:
- Reducing manual recruiter workload on repetitive tasks.
- Increasing throughput of qualified candidate evaluations.
- Improving hiring cycle efficiency through proactive orchestration.
- Standardizing candidate and stakeholder communication.

### Opportunity Size (Directional)
- TAM: Global HR tech and recruiting software spend (large and growing segment).
- SAM: AI-enabled recruitment workflow software for SMB/mid-market.
- SOM (12-24 months): early adopters using modern ATS and remote-first hiring practices.

## Competitive Landscape
### Direct Competitors
- ATS platforms with built-in AI assistants
- AI sourcing/screening point solutions
- Candidate matching and automation tools

### Indirect Competitors
- Manual recruiter workflows
- Outsourced recruiting agencies
- Generic LLM copilots without workflow orchestration

### Differentiation Opportunities
- End-to-end CrewAI orchestration across sourcing, screening, communication, and analytics.
- Transparent agent reasoning and configurable decision criteria.
- Human-in-the-loop control points at shortlist, rejection, and final recommendation stages.
- Integration-first approach with existing ATS rather than replacing the stack.

## User Journey and Workflow Gaps
1. Requisition intake from hiring manager
2. Job description optimization and channel plan
3. Candidate sourcing and enrichment
4. Resume screening and initial ranking
5. Interview coordination and communication
6. Offer pipeline tracking and reporting

Current market tools often optimize one stage but not the full workflow. The largest unmet need is coordinated orchestration with preserved context between stages.

## Product Requirements (Market-Level)
### Must-Have (MVP)
- Requisition intake assistant with role clarifications
- JD optimization with inclusive language checks
- Candidate profile scoring against role criteria
- Interview scheduling coordination with standard messaging templates
- Recruiter dashboard for status, actions, and approvals

### Should-Have (Post-MVP)
- Automated sourcing across multiple talent channels
- Candidate engagement sequencing (email + follow-up logic)
- Funnel bottleneck analytics and recommendations

### Could-Have (Future)
- Predictive quality-of-hire signals
- Offer acceptance probability guidance
- Internal mobility and referral matching

## Business Model and Pricing Hypothesis
- SaaS subscription, seat + usage model
- Starter: small teams with core automation limits
- Growth: higher workflow volume, advanced analytics, integrations
- Enterprise: compliance features, SSO, audit controls, custom workflows

## Success Metrics (Market and Product)
### Business KPIs
- Time-to-fill reduction: target 20-35%
- Cost-per-hire reduction: target 15-25%
- Qualified shortlist cycle time reduction: target 30-50%
- Pipeline conversion improvement (screen-to-interview): target 10-20%

### Adoption KPIs
- Weekly active recruiters / licensed recruiters > 70%
- Workflow automation usage in active requisitions > 60%
- Hiring manager satisfaction score > 4.2/5

### Candidate Experience KPIs
- Candidate response SLA adherence > 90%
- Candidate NPS improvement quarter-over-quarter

## Constraints and Guardrails
- The system provides recommendations, not autonomous final hiring decisions.
- Sensitive attributes must not be used in scoring decisions.
- All AI outputs must remain explainable and reviewable.
- Integrations should preserve existing ATS source-of-truth ownership.

## Risks and Mitigations
### High Risk
- Bias/fairness concerns in candidate evaluation
  - Mitigation: explicit fairness checks, protected-attribute exclusion, human approval gates
- Integration friction with ATS ecosystems
  - Mitigation: phased connector strategy, clear API contract versioning

### Medium Risk
- Recruiter trust and adoption barriers
  - Mitigation: transparent rationale, override controls, staged rollout
- Model output inconsistency across role types
  - Mitigation: role-specific prompt templates, benchmarked scoring rubrics

### Low Risk
- UI learning curve
  - Mitigation: guided onboarding and in-product workflow tips

## Go/No-Go Criteria
### Go
- MVP can demonstrate measurable reduction in recruiter cycle time within pilot accounts.
- Bias and explainability controls are validated in pilot evaluation.
- Core ATS integration reliability meets operational threshold.

### No-Go
- Inability to provide auditable reasoning for scoring recommendations.
- Integration reliability blocks daily recruiter workflows.
- Pilot users do not show sustained adoption after onboarding period.

## Phased Rollout Recommendation
- Phase 1: Recruiter copilots for intake, screening, and communication support
- Phase 2: Multi-agent orchestration across sourcing and scheduling
- Phase 3: Analytics intelligence and optimization recommendations

## Sources
- CrewAI official documentation and examples (including recruitment-oriented workflows)
- Public HR technology market reports (industry benchmark references)
- Public hiring operations benchmarks (time-to-fill and recruiting funnel metrics)
- Common ATS platform integration documentation

## Assumptions
- Initial release focuses on English-language hiring workflows.
- Target users already maintain ATS-based hiring processes.
- Pilot customers can provide baseline metrics for comparison.
- Data privacy and compliance requirements vary by customer tier.

## Open Questions
- Which ATS integrations should be prioritized in the first 90 days?
- What level of customization is required for role-specific scoring frameworks?
- Should candidate communication include multilingual support in MVP?
- Which fairness metrics are mandatory for pilot acceptance?

## Audit
- Timestamp: 2026-05-08
- Persona: `@product-mgr`
- Action: Authored MRD for Recruitment Assistant based on CrewAI recruitment use case and AAMAD artifact conventions.
