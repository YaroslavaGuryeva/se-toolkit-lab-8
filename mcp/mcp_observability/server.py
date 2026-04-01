"""Stdio MCP server exposing observability tools for VictoriaLogs and VictoriaTraces."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

server = Server("observability")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_VICTORIALOGS_URL: str = ""
_VICTORIATRACES_URL: str = ""


def _get_victorialogs_url() -> str:
    """Get VictoriaLogs base URL from environment."""
    url = os.environ.get("VICTORIALOGS_URL", "").rstrip("/")
    if not url:
        raise RuntimeError(
            "VictoriaLogs URL not configured. Set VICTORIALOGS_URL environment variable."
        )
    return url


def _get_victoriatraces_url() -> str:
    """Get VictoriaTraces base URL from environment."""
    url = os.environ.get("VICTORIATRACES_URL", "").rstrip("/")
    if not url:
        raise RuntimeError(
            "VictoriaTraces URL not configured. Set VICTORIATRACES_URL environment variable."
        )
    return url


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class _LogsSearchQuery(BaseModel):
    """Query logs by keyword and/or time range."""

    query: str = Field(
        default="",
        description="LogsQL query string. Examples: 'error', '_stream:{service=\"backend\"}', 'level:error'",
    )
    start: str = Field(
        default="-1h",
        description="Start time for the search. Examples: '-1h', '-24h', '2024-01-01T00:00:00Z'",
    )
    end: str = Field(
        default="now",
        description="End time for the search. Default is 'now'.",
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of log entries to return (default 50, max 1000).",
    )


class _LogsErrorCountQuery(BaseModel):
    """Count errors per service over a time window."""

    start: str = Field(
        default="-1h",
        description="Start time for the count. Examples: '-1h', '-24h'.",
    )
    end: str = Field(
        default="now",
        description="End time for the count. Default is 'now'.",
    )


class _TracesListQuery(BaseModel):
    """List recent traces for a service."""

    service: str = Field(
        default="Learning Management Service",
        description="Service name to filter traces. Example: 'Learning Management Service'.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of traces to return (default 20, max 100).",
    )


class _TracesGetQuery(BaseModel):
    """Fetch a specific trace by ID."""

    trace_id: str = Field(description="The trace ID to fetch.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(data: Any) -> list[TextContent]:
    """Serialize data to a JSON text block."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    elif isinstance(data, list):
        payload = [
            item.model_dump() if isinstance(item, BaseModel) else item for item in data
        ]
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


def _format_log_entry(entry: dict) -> str:
    """Format a single log entry for readable output."""
    timestamp = entry.get("_time", entry.get("timestamp", "unknown"))
    level = entry.get("level", entry.get("SeverityText", "INFO"))
    service = entry.get("resource.service.name", entry.get("service", "unknown"))
    message = entry.get("_msg", entry.get("message", str(entry)))
    trace_id = entry.get("trace_id", "")
    span_id = entry.get("span_id", "")

    result = f"[{timestamp}] [{level}] [{service}]"
    if trace_id:
        result += f" [trace:{trace_id[:16]}]"
    result += f" {message}"
    return result


def _format_trace_summary(trace: dict) -> str:
    """Format a trace summary for readable output."""
    trace_id = trace.get("traceID", "unknown")
    spans = trace.get("spans", [])
    service_names = set()
    for span in spans:
        if "process" in span:
            service_names.add(span["process"].get("serviceName", "unknown"))

    duration_ms = trace.get("duration", 0)
    start_time = trace.get("startTime", 0)

    # Find the root span (the one with the earliest start time)
    root_span = None
    if spans:
        root_span = min(spans, key=lambda s: s.get("startTime", float("inf")))

    result = f"Trace: {trace_id[:16]}...\n"
    result += f"  Duration: {duration_ms / 1000:.2f}ms\n"
    result += f"  Services: {', '.join(service_names)}\n"
    result += f"  Spans: {len(spans)}\n"
    if root_span:
        result += f"  Root: {root_span.get('operationName', 'unknown')}\n"

    # Check for errors in spans
    errors = []
    for span in spans:
        for log in span.get("logs", []):
            for field in log.get("fields", []):
                if field.get("key") == "error" or "error" in str(field).lower():
                    errors.append(span.get("operationName", "unknown"))
                    break

    if errors:
        result += f"  Errors in: {', '.join(set(errors))}\n"

    return result


# ---------------------------------------------------------------------------
# VictoriaLogs API client
# ---------------------------------------------------------------------------


async def _logs_search(query: str, start: str, end: str, limit: int) -> list[dict]:
    """Search logs using VictoriaLogs HTTP API.
    
    VictoriaLogs returns newline-delimited JSON (NDJSON), where each line is a separate JSON object.
    """
    url = f"{_VICTORIALOGS_URL}/select/logsql/query"
    params = {
        "query": query,
        "start": start,
        "end": end,
        "limit": limit,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                text = await response.text()
                raise RuntimeError(f"VictoriaLogs API error: {response.status} - {text}")

            # VictoriaLogs returns NDJSON (newline-delimited JSON)
            text = await response.text()
            if not text.strip():
                return []
            
            logs = []
            for line in text.strip().split('\n'):
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return logs


async def _logs_error_count(start: str, end: str) -> list[dict]:
    """Count errors per service using VictoriaLogs."""
    # Query for all error-level logs using VictoriaLogs LogsQL syntax
    # The severity field is uppercase: ERROR, INFO, WARN, etc.
    query = 'severity:ERROR'

    url = f"{_VICTORIALOGS_URL}/select/logsql/query"
    params = {
        "query": query,
        "start": start,
        "end": end,
        "limit": 1000,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                text = await response.text()
                raise RuntimeError(f"VictoriaLogs API error: {response.status} - {text}")

            # VictoriaLogs returns NDJSON (newline-delimited JSON)
            text = await response.text()
            if not text.strip():
                return []
            
            logs = []
            for line in text.strip().split('\n'):
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            # Count errors by service
            error_counts: dict[str, int] = {}
            for entry in logs:
                service = entry.get("resource.service.name", entry.get("service", "unknown"))
                error_counts[service] = error_counts.get(service, 0) + 1

            return [{"service": service, "error_count": count} for service, count in sorted(error_counts.items(), key=lambda x: -x[1])]


# ---------------------------------------------------------------------------
# VictoriaTraces API client (Jaeger-compatible)
# ---------------------------------------------------------------------------


async def _traces_list(service: str, limit: int) -> list[dict]:
    """List recent traces for a service using VictoriaTraces Jaeger API."""
    # VictoriaTraces Jaeger API is at /select/jaeger/api/traces, not /api/traces
    url = f"{_VICTORIATRACES_URL}/select/jaeger/api/traces"
    params = {
        "service": service,
        "limit": limit,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                text = await response.text()
                raise RuntimeError(f"VictoriaTraces API error: {response.status} - {text}")

            data = await response.json()
            # Jaeger API returns {"data": [...traces...]}
            traces = data.get("data", [])
            return traces


async def _traces_get(trace_id: str) -> dict:
    """Fetch a specific trace by ID using VictoriaTraces Jaeger API."""
    # VictoriaTraces Jaeger API is at /select/jaeger/api/traces/{trace_id}
    url = f"{_VICTORIATRACES_URL}/select/jaeger/api/traces/{trace_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                text = await response.text()
                raise RuntimeError(f"VictoriaTraces API error: {response.status} - {text}")

            data = await response.json()
            # Jaeger API returns {"data": [trace]}
            traces = data.get("data", [])
            return traces[0] if traces else {}


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def _logs_search_handler(args: _LogsSearchQuery) -> list[TextContent]:
    """Search logs by keyword and/or time range."""
    try:
        logs = await _logs_search(args.query, args.start, args.end, args.limit)

        if not logs:
            return [TextContent(type="text", text="No logs found matching the query.")]

        # Format logs for readability
        formatted = []
        for entry in logs:
            formatted.append(_format_log_entry(entry))

        result = f"Found {len(logs)} log entries:\n\n"
        result += "\n".join(formatted)
        return [TextContent(type="text", text=result)]

    except Exception as exc:
        return [TextContent(type="text", text=f"Error searching logs: {type(exc).__name__}: {exc}")]


async def _logs_error_count_handler(args: _LogsErrorCountQuery) -> list[TextContent]:
    """Count errors per service over a time window."""
    try:
        counts = await _logs_error_count(args.start, args.end)

        if not counts:
            return [TextContent(type="text", text="No errors found in the specified time window.")]

        result = f"Error count from {args.start} to {args.end}:\n\n"
        for item in counts:
            result += f"  {item['service']}: {item['error_count']} errors\n"

        return [TextContent(type="text", text=result)]

    except Exception as exc:
        return [TextContent(type="text", text=f"Error counting logs: {type(exc).__name__}: {exc}")]


async def _traces_list_handler(args: _TracesListQuery) -> list[TextContent]:
    """List recent traces for a service."""
    try:
        traces = await _traces_list(args.service, args.limit)

        if not traces:
            return [TextContent(type="text", text=f"No traces found for service: {args.service}")]

        result = f"Found {len(traces)} recent traces for '{args.service}':\n\n"
        for trace in traces[:args.limit]:
            result += _format_trace_summary(trace)
            result += "\n"

        return [TextContent(type="text", text=result)]

    except Exception as exc:
        return [TextContent(type="text", text=f"Error listing traces: {type(exc).__name__}: {exc}")]


async def _traces_get_handler(args: _TracesGetQuery) -> list[TextContent]:
    """Fetch a specific trace by ID."""
    try:
        trace = await _traces_get(args.trace_id)

        if not trace:
            return [TextContent(type="text", text=f"Trace not found: {args.trace_id}")]

        result = _format_trace_summary(trace)
        result += "\n--- Full Trace Data ---\n"
        result += json.dumps(trace, indent=2)

        return [TextContent(type="text", text=result)]

    except Exception as exc:
        return [TextContent(type="text", text=f"Error fetching trace: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Registry: tool name -> (input model, handler, Tool definition)
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (
        model,
        handler,
        Tool(name=name, description=description, inputSchema=schema),
    )


_register(
    "logs_search",
    "Search structured logs in VictoriaLogs. Use LogsQL queries like 'error', '_stream:{service=\"backend\"}', or 'level:error'. Returns formatted log entries with timestamps, levels, and trace IDs.",
    _LogsSearchQuery,
    _logs_search_handler,
)
_register(
    "logs_error_count",
    "Count errors per service over a time window. Returns a summary of error counts grouped by service name.",
    _LogsErrorCountQuery,
    _logs_error_count_handler,
)
_register(
    "traces_list",
    "List recent traces for a service from VictoriaTraces. Returns trace summaries with duration, services involved, and error indicators.",
    _TracesListQuery,
    _traces_list_handler,
)
_register(
    "traces_get",
    "Fetch a specific trace by ID from VictoriaTraces. Returns full trace details including all spans and their hierarchy.",
    _TracesGetQuery,
    _traces_get_handler,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    global _VICTORIALOGS_URL, _VICTORIATRACES_URL
    _VICTORIALOGS_URL = _get_victorialogs_url()
    _VICTORIATRACES_URL = _get_victoriatraces_url()

    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
