# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

### Question 1: "What is the agentic loop?"

**Response:**

The agentic loop is the fundamental cycle that autonomous AI agents follow to accomplish tasks. It's the core reasoning and action pattern that enables agents to work independently toward goals.

**The Basic Loop:**

```
Perceive → Reason → Act → Observe → (repeat)
```

1. **Perceive** - The agent gathers information about its environment (reads user input, observes current state, collects context)

2. **Reason** - The agent processes information and plans (analyzes goals, determines actions needed, decides on next steps)

3. **Act** - The agent executes actions (calls tools, makes changes, communicates)

4. **Observe** - The agent evaluates results (checks tool outputs, assesses progress, detects errors)

5. **Repeat** - Based on observations, the agent loops back (continues if more work needed, stops if goal achieved)

### Question 2: "What labs are available in our LMS?"

**Response:**

The agent found information from local workspace files about the SET course structure:
- 10 labs total, each 3 hours long
- Currently working on Lab 8: "The Agent is the Interface"
- References to Lab 6, Lab 7 in documentation

**Note:** The agent is reading from local files, NOT from the LMS backend API. It has no MCP tools configured yet.

---

## Task 1B — Agent with LMS tools

### Question 1: "What labs are available?"

**Response:**

The agent returned real lab data from the LMS backend:

| ID | Lab Title |
|----|-----------|
| 1 | Lab 01 – Products, Architecture & Roles |
| 2 | Lab 02 — Run, Fix, and Deploy a Backend Service |
| 3 | Lab 03 — Backend API: Explore, Debug, Implement, Deploy |
| 4 | Lab 04 — Testing, Front-end, and AI Agents |
| 5 | Lab 05 — Data Pipeline and Analytics Dashboard |
| 6 | Lab 06 — Build Your Own Agent |
| 7 | Lab 07 — Build a Client with an AI Coding Agent |
| 8 | lab-08 (The Agent is the Interface) |

**Note:** The agent is now calling the `lms_labs` MCP tool and returning real data from the backend, not just reading local files.

### Question 2: "Describe the architecture of the LMS system"

**Response:**

The agent described the full LMS architecture including:

**Client Layer:**
- React Web UI (Flutter optional)
- nanobot Agent
- pgAdmin (DB Admin)

**Gateway (Caddy):**
- Single entry point on port 42002
- Routes requests to backend, pgAdmin, Flutter, WebSocket, static files

**Application Layer:**
- Backend (FastAPI) on port 42001
- MCP Servers (mcp_lms for LMS tools, observability tools)
- PostgreSQL database on port 5432

**Observability Stack (Lab 8+):**
- VictoriaLogs
- VictoriaTraces
- OTel Collector

**Key Features:**
- MCP (Model Context Protocol) for standardized tool interface
- Structured Logging via OpenTelemetry → VictoriaLogs
- Distributed Tracing via OpenTelemetry → VictoriaTraces
- Health Checks via Docker Compose
- API Authentication with Bearer token (LMS_API_KEY)

**Current Status:** LMS Backend is healthy with 56 items in database.

---

## Task 1C — Skill prompt

### Question: "Show me the scores" (without specifying a lab)

**Response:**

The agent used the skill prompt to provide a comprehensive overview:

**Completion Rates by Lab:**

| Lab | Completion Rate | Passed | Total |
|-----|-----------------|--------|-------|
| Lab 01 – Products, Architecture & Roles | ✅ 100.0% | 258 | 258 |
| Lab 02 – Run, Fix, and Deploy a Backend Service | ✅ 89.1% | 131 | 147 |
| Lab 03 – Backend API: Explore, Debug, Implement, Deploy | ✅ 89.7% | 156 | 174 |
| Lab 04 – Testing, Front-end, and AI Agents | ✅ 96.7% | 238 | 246 |
| Lab 05 – Data Pipeline and Analytics Dashboard | ✅ 98.4% | 246 | 250 |
| Lab 06 – Build Your Own Agent | ✅ 98.4% | 241 | 245 |
| Lab 07 – Build a Client with an AI Coding Agent | ✅ 99.6% | 236 | 237 |
| Lab 08 – The Agent is the Interface | ⏳ 0.0% | 0 | 0 |

**Task-Level Scores:** The agent also provided detailed breakdowns for each lab showing average scores and attempt counts per task.

**Key Insights:**
- Highest completion: Lab 07 (99.6%)
- Lowest completion: Lab 02 & 03 (~89%)
- Most attempted task: Lab 04 Task 2 (Back-end Testing) — 753 attempts
- Highest avg score: Lab 01 "Lab setup" — 84.3%
- Lowest avg score: Lab 01 "Optional: Plan skill development" — 20.0%

**Note:** The skill prompt guided the agent to:
1. Automatically fetch data for all labs when no specific lab was mentioned
2. Format percentages as `XX.X%`
3. Use markdown tables for structured data
4. Provide key insights summarizing the data
5. Keep responses concise but informative

---

## Task 2A — Deployed agent

**Nanobot gateway startup log:**

```
Using config: /app/nanobot/config.resolved.json
🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
2026-03-30 08:58:49.691 | DEBUG    | nanobot.channels.registry:discover_all:64 - Skipping built-in channel 'matrix': Matrix dependencies not installed. Run: pip install nanobot-ai[matrix]
2026-03-30 08:58:50.115 | INFO     | nanobot.channels.manager:_init_channels:54 - WebChat channel enabled
✓ Channels enabled: webchat
✓ Heartbeat: every 1800s
2026-03-30 08:58:50.117 | INFO     | nanobot.cron.service:_load_store:83 - Cron: jobs.json modified externally, reloading
2026-03-30 08:58:50.118 | INFO     | nanobot.cron.service:start:182 - Cron service started with 0 jobs
2026-03-30 08:58:50.118 | INFO     | nanobot.heartbeat.service:start:122 - Heartbeat started (every 1800s)
2026-03-30 08:58:50.483 | INFO     | nanobot.channels.manager:start_all:87 - Starting webchat channel...
2026-03-30 08:58:50.484 | INFO     | nanobot.channels.manager:_dispatch_outbound:115 - Outbound dispatcher started
2026-03-30 08:58:50.484 | INFO     | nanobot_webchat.channel:start:72 - WebChat starting on 0.0.0.0:8765
/app/.venv/bin/python: No module named mcp_lms
2026-03-30 08:58:50.654 | ERROR    | nanobot.agent.tools.mcp:connect_mcp_servers:184 - MCP server 'lms': failed to connect: Connection closed
2026-03-30 08:58:50.654 | INFO     | nanobot.agent.loop:run:260 - Agent loop started
```

**Status:** The nanobot gateway is running as a Docker service. The WebChat channel is enabled and listening on port 8765.

**Note:** The MCP server error for 'lms' is expected - the `mcp_lms` module needs to be installed in the nanobot Docker image. This is addressed by the Dockerfile which copies and installs the MCP package from the workspace.

---

## Task 2B — Web client

**WebSocket endpoint test:**

```
Sent: What can you do in this system?
Received: {"type":"text","content":"I'm **nanobot** 🐈, your personal AI assistant. Here's what I can do:\n\n## Core Capabilities\n\n**File & System Operations**\n- Read, write, and edit files\n- List directory contents\n- Execute shell commands (with safety limits)\n\n**Web & Information**\n- Search the web for information\n- Fetch and extract content from URLs\n\n...","format":"markdown"}
```

**Flutter web client:** Accessible at `http://localhost:42002/flutter/`

**Files created/modified:**
- `nanobot/Dockerfile` — Fixed to copy `nanobot-websocket-channel` before `uv sync`
- `nanobot/pyproject.toml` — Added `nanobot-webchat` dependency
- `nanobot/uv.lock` — Updated with new dependency

## Task 3A — Structured logging

### Happy-path log excerpt (status 200)

```
2026-03-30 20:38:12,314 INFO [app.main] [main.py:60] [trace_id=444db2a769e07f7b1b36cd5b433d2226 span_id=590c951a098fa92d resource.service.name=Learning Management Service trace_sampled=True] - request_started
2026-03-30 20:38:12,316 INFO [app.auth] [auth.py:30] [trace_id=444db2a769e07f7b1b36cd5b433d2226 span_id=590c951a098fa92d resource.service.name=Learning Management Service trace_sampled=True] - auth_success
2026-03-30 20:38:12,317 INFO [app.db.items] [items.py:16] [trace_id=444db2a769e07f7b1b36cd5b433d2226 span_id=590c951a098fa92d resource.service.name=Learning Management Service trace_sampled=True] - db_query
2026-03-30 20:38:12,385 INFO [app.main] [main.py:68] [trace_id=444db2a769e07f7b1b36cd5b433d2226 span_id=590c951a098fa92d resource.service.name=Learning Management Service trace_sampled=True] - request_completed
INFO:     172.18.0.10:60096 - "GET /items/ HTTP/1.1" 200
```

**Flow:** `request_started` → `auth_success` → `db_query` → `request_completed` (200 OK)

### Error-path log excerpt (PostgreSQL stopped)

```
2026-03-30 21:02:11,648 INFO [app.main] [main.py:60] [trace_id=b17707bcd7fa37534977d9574f345210 span_id=8327577da0a98ac4 resource.service.name=Learning Management Service trace_sampled=True] - request_started
2026-03-30 21:02:11,661 INFO [app.auth] [auth.py:30] [trace_id=b17707bcd7fa37534977d9574f345210 span_id=8327577da0a98ac4 resource.service.name=Learning Management Service trace_sampled=True] - auth_success
2026-03-30 21:02:11,663 INFO [app.db.items] [items.py:16] [trace_id=b17707bcd7fa37534977d9574f345210 span_id=8327577da0a98ac4 resource.service.name=Learning Management Service trace_sampled=True] - db_query
2026-03-30 21:02:12,326 ERROR [app.db.items] [items.py:20] [trace_id=b17707bcd7fa37534977d9574f345210 span_id=8327577da0a98ac4 resource.service.name=Learning Management Service trace_sampled=True] - db_query
2026-03-30 21:02:12,328 INFO [app.main] [main.py:68] [trace_id=b17707bcd7fa37534977d9574f345210 span_id=8327577da0a98ac4 resource.service.name=Learning Management Service trace_sampled=True] - request_completed
INFO:     172.18.0.10:37742 - "GET /items/ HTTP/1.1" 404
```

**Flow:** `request_started` → `auth_success` → `db_query` (INFO) → `db_query` (ERROR) → `request_completed` (404)

**Error details:** `[Errno -2] Name or service not known` — database connection failed

### VictoriaLogs query screenshot

![VictoriaLogs error query](instructors/file-reviews/images/victorialogs-error-query.png)

*Query:* `{"service.name"="Learning Management Service"} AND SeverityText=ERROR`


## Task 3B — Traces

### Healthy Trace

**Trace ID:** `75c9eeac49619e29fde05bd4aebda101`

**Span Hierarchy:**

```
GET /items/ (849ms) [server]
├── connect (349ms) [client - PostgreSQL connection]
│   ├── BEGIN; (9ms)
│   └── ROLLBACK; (1ms)
├── SELECT db-lab-8 (28ms) [client - SQLAlchemy query]
├── BEGIN; (0.5ms) [client - asyncpg]
└── GET /items/ http send (0.1ms) [response]
```

**Services involved:**
- Learning Management Service (FastAPI)
- PostgreSQL (database)

**Key spans:**
| Operation | Duration | Type |
|-----------|----------|------|
| GET /items/ | 849ms | Server (root span) |
| connect | 349ms | Database connection |
| SELECT db-lab-8 | 28ms | SQL query |
| BEGIN/ROLLBACK | <1ms | Transaction control |

**Status:** HTTP 200 OK — all spans completed successfully.

### Error Trace (PostgreSQL stopped)

When PostgreSQL was stopped, the backend logged errors with trace ID `538065887ec488a8c935348809f89a59`:

**Error log excerpt:**
```
2026-03-31 21:20:45,026 ERROR [app.db.items] [items.py:20] 
  [trace_id=538065887ec488a8c935348809f89a59 span_id=2169126c57556e0c] 
  - db_query
```

**Error details:**
- **Location:** `app.db.items` module, line 20
- **Operation:** `db_query` event
- **Root cause:** PostgreSQL connection refused — database was stopped
- **Trace correlation:** The trace ID in the error log can be used to fetch the full trace from VictoriaTraces

**Note:** The error trace shows how distributed tracing correlates logs with spans — even when a request fails, the trace ID helps identify exactly where in the request flow the failure occurred.

### VictoriaTraces UI

**Screenshot to add:** Open `http://localhost:42002/utils/victoriatraces/select/vmui` and search for trace `75c9eeac49619e29`. Save a screenshot as `instructors/file-reviews/images/victoriatraces-healthy-trace.png`.

*Expected: VictoriaTraces UI showing the span hierarchy for a healthy request. Each bar represents a span, with the width showing duration.*

---

## Task 3C — Observability MCP tools

### MCP Tools Implemented

The following observability tools are registered in the MCP server (`mcp/mcp_observability/`):

**Log tools (VictoriaLogs):**
- `logs_search` — Search logs by LogsQL query and time range
- `logs_error_count` — Count errors per service over a time window

**Trace tools (VictoriaTraces):**
- `traces_list` — List recent traces for a service
- `traces_get` — Fetch a specific trace by ID

### Tool Test: "Any errors in the last hour?" (Normal conditions)

**Agent response:**

> I searched for errors in the last hour using the observability tools:
>
> **Error count:** 0 errors found across all services.
>
> **System health:**
> - Learning Management Service: No errors
> - qwen-code-api: No errors
> - otel-collector: No errors
>
> Recent traces show normal response times (50-200ms) for database queries and HTTP requests.

### Tool Test: "Any errors in the last hour?" (PostgreSQL stopped)

After stopping PostgreSQL and triggering a request:

**Agent response:**

> Yes, I found errors in the last hour:
>
> **Error summary:**
> - Learning Management Service: 1 error
>
> **Error details:**
> ```
> [2026-03-31 21:20:45] [ERROR] [Learning Management Service] 
> [trace:538065887ec488a8] db_query
> ```
>
> **Root cause:** Database connection failed — PostgreSQL was unreachable at the time of the request.
>
> **Trace analysis:** The error occurred during the `db_query` span. The trace ID `538065887ec488a8...` shows the request started successfully but failed when attempting to connect to the database.
>
> **Recommendation:** Check if PostgreSQL is running: `docker compose ps postgres`

### Files created/modified

| File | Purpose |
|------|---------|
| `mcp/mcp_observability/server.py` | MCP server with 4 observability tools |
| `mcp/mcp_observability/__init__.py` | Package init |
| `mcp/mcp_observability/__main__.py` | Entry point for running as stdio MCP server |
| `nanobot/workspace/skills/observability/SKILL.md` | Skill prompt teaching agent when/how to use observability tools |
| `docker-compose.yml` | Added `VICTORIALOGS_URL` and `VICTORIATRACES_URL` env vars to nanobot service |

### Verification

**VictoriaLogs query API test:**
```bash
curl "http://localhost:42010/select/logsql/query?query=_stream:{service.name=\"Learning%20Management%20Service\"}&start=-1h&limit=5"
```

Returns structured logs with trace IDs:
```json
{
  "_msg": "request_completed",
  "trace_id": "75c9eeac49619e29fde05bd4aebda101",
  "span_id": "0bac2fb50383cc07",
  "service.name": "Learning Management Service",
  "severity": "INFO",
  "status": "200"
}
```

**VictoriaTraces Jaeger API test:**
```bash
curl "http://localhost:42002/utils/victoriatraces/select/jaeger/api/traces?service=Learning%20Management%20Service&limit=3"
```

Returns trace summaries with span hierarchies.

## Task 4A — Multi-step investigation

**Agent response to "What went wrong?" (with PostgreSQL stopped):**

Based on my investigation, here's what went wrong with the LMS system:

## Issue Summary

**The LMS backend service is unreachable.** The system is experiencing connection failures.

## Evidence

1. **API Errors:**
   - `GET /items/` → HTTP 404 Not Found (when listing labs)
   - `POST /pipeline/sync` → HTTP 500 Internal Server Error

2. **Health Check:**
   - Status: **unhealthy**
   - Item count: unknown

3. **Trace Analysis:**
   - Recent traces show errors in:
     - `POST /pipeline/sync` 
     - `connect` operations
   - Multiple `GET /items/` requests failing at the connection layer

## Root Cause

The pattern of "connect" errors in the traces suggests the LMS backend service (`http://backend:8000`) is either:
- **Not running** (service crashed or never started)
- **Network isolation** (can't reach the backend container/host)
- **Misconfigured** (wrong port or endpoint)

## Recommended Actions

1. Check if the backend service is running
2. Verify network connectivity to `backend:8000`
3. Review backend service logs for startup errors
4. Check container/service orchestration (Docker, Kubernetes, etc.)

---

**Note:** The agent's response was generic. The actual root cause (found via direct trace inspection) is:
- **Error:** `[Errno -2] Name or service not known` (socket.gaierror)
- **Location:** `connect` span when trying to connect to `postgres:5432`
- **Root cause:** PostgreSQL was stopped, so the backend couldn't resolve the `postgres` hostname

The agent should have used the observability MCP tools to:
1. Call `logs_search` with `query="level:error"` and `start="-5m"`
2. Extract the `trace_id` from error logs
3. Call `traces_get` with that trace ID
4. Summarize the span hierarchy showing the database connection failure


## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

### 1. Root Cause — Planted Bug

**Location:** `backend/app/routers/items.py`, lines 17-22

**Bug:** The `get_items` endpoint caught all exceptions (including database connection errors) and returned HTTP 404 Not Found:

```python
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    """Get all items."""
    try:
        return await read_items(session)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  # ← BUG: Should be 500
            detail="Items not found",
        ) from exc
```

**Why it's wrong:** A 404 status code means "resource not found" — the requested URL doesn't exist. But when PostgreSQL is stopped, the database connection fails, which is a **server error** (500), not a missing resource.

### 2. Fix Applied

Changed the exception handler to return HTTP 500 with the actual error message:

```python
@router.get("/", response_model=list[ItemRecord])
async def get_items(session: AsyncSession = Depends(get_session)):
    """Get all items."""
    try:
        return await read_items(session)
    except Exception as exc:
        # Database errors (connection failures, etc.) should return 500, not 404
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(exc)}",
        ) from exc
```

**Diff:**
```diff
- status_code=status.HTTP_404_NOT_FOUND,
- detail="Items not found",
+ status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
+ detail=f"Database error: {str(exc)}",
```

### 3. Post-Fix Verification (PostgreSQL Stopped)

After rebuilding and redeploying the backend, with PostgreSQL stopped:

**Request:**
```bash
curl http://localhost:42002/items/ -H "Authorization: Bearer <key>"
```

**Response (after fix):**
```json
{"detail":"Database error: [Errno -2] Name or service not known"}
```
**HTTP Status:** 500 (was 404 before fix)

The error message now correctly identifies the root cause: DNS resolution failure when trying to connect to the `postgres` hostname.

### 4. Healthy Follow-Up (PostgreSQL Restarted)

After restarting PostgreSQL:

```bash
docker compose --env-file .env.docker.secret start postgres
```

**Request:**
```bash
curl http://localhost:42002/items/ -H "Authorization: Bearer <key>"
```

**Response:**
```json
[{"id":1,"type":"lab","title":"Lab 01 – Products, Architecture & Roles",...}, ...]
```
**HTTP Status:** 200 OK

The system is now healthy and returns the expected data.
