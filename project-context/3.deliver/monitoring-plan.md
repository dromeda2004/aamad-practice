# Monitoring and Logging Plan

## Goals

- Provide observability for TalentFlow AI backend request handling, run orchestration, and CrewAI task execution.
- Capture structured logs with run/trace correlation for debugging and performance reviews.
- Document CrewAI tracing configuration and operational monitoring guidance.
- Enable teams to detect failures, slow pipelines, and approval-state anomalies.

## Backend Logging Strategy

### Centralized logging

- `backend/app/logging_config.py` configures structured logs for both console and file output.
- Logs include contextual fields such as `run_id`, `trace_id`, `stage`, `status_code`, `request_id`, `client_ip`, and `duration_ms`.
- The backend chooses JSON output by default in production and a readable text formatter in development.
- File logging is enabled outside of the `development` environment and writes to `LOG_FILE_PATH`.

### Important log events

- Application startup:
  - `Application startup complete`
- HTTP request lifecycle:
  - `Request start`
  - `Request complete`
  - `Request failed`
- Pipeline lifecycle:
  - `agent start`
  - `agent complete`
  - `pipeline complete`
- CrewAI execution mode:
  - `Using mock crew`
  - `Using LLM crew`
- Run lifecycle:
  - `Run created`

## Trace Correlation

- Each workflow run is assigned a `trace_id`.
- The trace ID is propagated through pipeline execution logs and can be used to group logs across request, store, and agent stages.
- `run_id` and `trace_id` together support fast lookup of a single candidate evaluation sequence.

## CrewAI Tracing Integration

### Environment variables

- `CREWAI_TRACING_ENABLED=false` controls whether CrewAI AOP tracing is enabled.
- `CREW_AOP_API_KEY=` stores the CrewAI tracing API key for service-side instrumentation.
- `LOG_LEVEL`, `LOG_FORMAT`, and `LOG_FILE_PATH` allow runtime configuration of log emission.

### Instrumentation guidance

- Use CrewAI tracing for service-level trace collection when `CREWAI_TRACING_ENABLED=true`.
- Ensure the tracing API key is provisioned securely and never committed to source control.
- For development and testing, mock crew execution remains available with `USE_MOCK_CREW=auto`.
- Prefer `LOG_FORMAT=json` in production for log ingestion and `LOG_FORMAT=text` locally for easier debugging.

## Monitoring Targets

- Request latency and error rate for `POST /api/v1/runs`, `GET /api/v1/runs/{run_id}`, and approval endpoints.
- Pipeline stage transitions:
  - `researching`
  - `evaluating`
  - `recommending`
  - `awaiting_approval`
  - `approved`
- CrewAI mode selection and fallback behavior.
- Persistent errors or repeated reruns from a single `run_id`.

## Alerting and Ops

- Alert on repeated `Request failed` or `pipeline complete` with an error state.
- Alert if `awaiting_approval` stage remains active longer than expected.
- Monitor log volume spike events in production indicating retry storms or defective input.

## Operational Documentation

- To enable production logging, set:
  - `ENVIRONMENT=production`
  - `LOG_FORMAT=json`
  - `LOG_LEVEL=INFO`
  - `LOG_FILE_PATH=/var/log/talentflow`
- To enable CrewAI tracing, set:
  - `CREWAI_TRACING_ENABLED=true`
  - `CREW_AOP_API_KEY=<secure-key>`
- Verify logs are being written and that each run emits a `trace_id`.
- Use the `trace_id` field to drill into service execution during postmortems.
- For local development, use console logs and `LOG_FORMAT=text` to keep output readable.
- View production logs with:
  - `tail -f /var/log/talentflow/app.log`
  - `grep "trace_id=<id>" /var/log/talentflow/app.log`
  - `jq -r '.message, .trace_id, .run_id' /var/log/talentflow/app.log` for JSON log inspection

## CrewAI Tracing

### Setup

- Create a CrewAI AOP account at `app.crewai.com`.
- Install the CrewAI CLI tools:
  - `pip install "crewai[tools]"`
- Authenticate locally with:
  - `crewai login`
- Enable tracing in your application by setting:
  - `CREWAI_TRACING_ENABLED=true`
  - or using explicit Crew configuration when available.

### Accessing Traces

1. Visit `app.crewai.com`
2. Log in to your CrewAI AOP account
3. Navigate to your project dashboard
4. Click the `Traces` tab to view execution details

### What to Monitor

- Agent decision-making process
- Task execution timeline
- Tool usage and results
- LLM call performance
- Error occurrences

## DevOps Collaboration

- Review log format, log rotation, and retention with the DevOps team.
- Confirm `LOG_FILE_PATH` is writable in the deployment environment.
- Iterate on alert thresholds and trace dashboards as needed.

## Next Steps

- Add alert rules and dashboards in the chosen observability platform.
- Validate that logs produced by `backend/app/logging_config.py` can be ingested by the logging pipeline.
- Confirm CrewAI tracing data appears in the CrewAI dashboard when enabled.
