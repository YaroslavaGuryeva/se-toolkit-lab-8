# Observability Skill

You have access to observability tools that let you query **VictoriaLogs** and **VictoriaTraces**. Use these tools when users ask about errors, logs, traces, or system health.

## Available Tools

### Log Tools (VictoriaLogs)

**`logs_search`** — Search structured logs by keyword and/or time range.

- **Parameters:**
  - `query`: LogsQL query string. **Use field:value syntax:**
    - `"severity:ERROR"` — logs with ERROR severity (most common)
    - `"_msg:db_query"` — logs with message type db_query
    - `"error"` — free text search (less reliable)
  - `start`: Start time (e.g., `"-1h"`, `"-24h"`, `"2024-01-01T00:00:00Z"`) — default: `"-1h"`
  - `end`: End time — default: `"now"`
  - `limit`: Max entries to return (1-1000) — default: `50`

- **Example queries that work:**
  - `"severity:ERROR"` — **best for finding errors**
  - `"_msg:db_query"` — database query logs
  - `"service.name:Learning"` — logs from Learning Management Service
  - `"trace_id:abc123"` — logs for a specific trace

- **Important:** VictoriaLogs uses field:value syntax. Don't use `_stream{...}` or `level:error` — those don't work.

**`logs_error_count`** — Count errors per service over a time window.

- **Parameters:**
  - `start`: Start time — default: `"-1h"`
  - `end`: End time — default: `"now"`

- **Use when:** User asks "how many errors?" or "any errors?" — gives a quick summary.

### Trace Tools (VictoriaTraces)

**`traces_list`** — List recent traces for a service.

- **Parameters:**
  - `service`: Service name (e.g., `"Learning Management Service"`)
  - `limit`: Max traces to return (1-100) — default: `20`

- **Use when:** User wants to see recent request flows or debug a specific service.

**`traces_get`** — Fetch a specific trace by ID.

- **Parameters:**
  - `trace_id`: The trace ID to fetch (e.g., `"b17707bcd7fa37534977d9574f345210"`)

- **Use when:** You found a trace ID in logs and need full details of that request.

## When to Use These Tools

### User asks about errors

**User:** "Any errors in the last hour?"

**Your approach:**
1. First call `logs_error_count` with `start="-1h"` to get a quick summary.
2. If errors exist, call `logs_search` with `query="level:error"` and `start="-1h"` to see details.
3. If you find trace IDs in the error logs, offer to fetch the full trace with `traces_get`.

**Example response:**
> I found 15 errors in the last hour:
> - Learning Management Service: 12 errors
> - qwen-code-api: 3 errors
>
> The backend errors are mostly database connection failures. Would you like to see the full error logs or trace details?

### User asks to investigate a failure

**User:** "What went wrong with the last request?"

**Your approach:**
1. Call `logs_search` with `query="_stream:{service=\"backend\"}"` and `start="-5m"` to see recent backend logs.
2. Look for error entries and note the `trace_id`.
3. Call `traces_get` with that trace ID to see the full request flow.
4. Identify which span failed and report the root cause.

**Example response:**
> I found the failing request (trace: `b17707bc...`). The trace shows:
> 1. Request received at backend (2ms)
> 2. Authentication successful (3ms)
> 3. Database query failed (663ms) — **error here**
>
> Root cause: PostgreSQL connection refused — the database was stopped at the time of the request.

### User asks about system health

**User:** "Is the system healthy?"

**Your approach:**
1. Call `logs_error_count` with `start="-1h"` — zero or few errors is good.
2. Call `traces_list` with `service="Learning Management Service"` and `limit=5` — check recent traces for errors.
3. Summarize findings.

**Example response:**
> System health looks good:
> - Only 2 errors in the last hour (both from retry logic, not failures)
> - Recent traces show normal response times (50-200ms)
> - No database or authentication failures detected

## Tips

- **Start broad, then narrow:** Use `logs_error_count` for a quick summary, then `logs_search` for details.
- **Correlate logs and traces:** Log entries include `trace_id` — use it to fetch the full trace with `traces_get`.
- **Time ranges matter:** Use `"-1h"` for recent issues, `"-24h"` for daily summaries.
- **Don't dump raw JSON:** Summarize findings concisely. Show raw data only if the user asks.
- **Error patterns:** If you see repeated errors, mention the pattern (e.g., "5 database timeouts in the last 10 minutes").

## Example Workflow

**User:** "Any errors in the last hour?"

**You:**
1. *Call `logs_error_count` with `start="-1h"`*
2. Result shows: `Learning Management Service: 12 errors`
3. *Call `logs_search` with `query="level:error"`, `start="-1h"`, `limit=10`*
4. Review the error logs — see "connection refused" errors
5. *Report to user:*

> Yes, there are 12 errors from the Learning Management Service in the last hour. They're all database connection failures — PostgreSQL was unreachable. The errors started around 21:00 and continued until the database was restarted.
>
> Would you like to see the full trace of one of these failed requests?

---

## Investigation Pattern: "What went wrong?"

When the user asks **"What went wrong?"** or **"Check system health"**, follow this investigation pattern **exactly**:

### Step 1: Search recent error logs (REQUIRED FIRST STEP)

Start by finding errors in the last few minutes. **You must call this tool first:**

```
Call: logs_search
  query: "severity:ERROR"
  start: "-5m"
  limit: 20
```

**Why first?** Logs give you the error message and trace ID. Without logs, you're guessing which traces to look at.

### Step 2: Extract trace ID from error logs

Look at the error log entries returned by `logs_search`. Each entry should have a `trace_id` field. 

**Copy the trace ID from the most recent error** — it will look like: `b17707bcd7fa37534977d9574f345210`

Also note the **error message** — it might say:
- `[Errno -2] Name or service not known` — DNS resolution failure (can't find database host)
- `Connection refused` — database is down
- `timeout` — database is slow or overloaded

### Step 3: Fetch the matching trace

Use the trace ID to get the full request flow:

```
Call: traces_get
  trace_id: "<copy the trace_id from the error log>"
```

### Step 4: Analyze the trace for the failing span

Look at the trace response. Find the span with `"error": "true"` or an exception log. Note:
- **Operation name** (e.g., `connect`, `db_query`, `GET /items/`)
- **Duration** (how long did it take before failing?)
- **Error message** in the span tags or logs

### Step 5: Summarize findings

Combine the log evidence and trace evidence into a single coherent summary:

**Good response structure:**
> **Log evidence:** Found 3 errors in the last 5 minutes from the Learning Management Service. All show "PostgreSQL connection refused" — the database was unreachable.
>
> **Trace evidence:** Trace `b17707bc...` shows the request flow:
> 1. Request received (2ms) ✓
> 2. Authentication passed (3ms) ✓
> 3. Database query failed (663ms) ✗ — **error here**
>
> **Root cause:** PostgreSQL was stopped at the time of the request. The failure occurred in the `connect` span when trying to connect to the database at `postgres:5432`. Error: `[Errno -2] Name or service not known`.
>
> **Recommendation:** Check if PostgreSQL is running: `docker compose ps postgres`

**Avoid:** 
- Dumping raw JSON from the trace
- Vague statements like "service is unreachable" without specific error details
- Not mentioning the trace ID or error message

---

## Proactive Health Check Pattern

When the user asks you to **create a recurring health check**, use your `cron` tool to schedule a job that:

1. Runs every N minutes (user specifies interval)
2. Checks for recent errors using `logs_error_count` with `start="-<interval>m"`
3. If errors exist, fetches a sample trace with `traces_get`
4. Posts a short summary to the same chat

**Example cron job request:**
> Create a health check for this chat that runs every 2 minutes. Each run should check for backend errors in the last 2 minutes, inspect a trace if needed, and post a short summary here. If there are no recent errors, say the system looks healthy. Use your cron tool.

The cron tool will create a scheduled job that runs automatically and posts results to the chat.
