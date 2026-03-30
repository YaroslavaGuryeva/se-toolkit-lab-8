# Multi-stage build for nanobot gateway
# Adapted from backend/Dockerfile

# ---
# Stage 1: build the application in the `/app` directory.
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads, because we want to use the system interpreter
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace files (config.json, workspace/, entrypoint.py)
# Build context is ./nanobot, so these are relative to nanobot/
COPY . /app/nanobot/

# Copy root pyproject.toml and uv.lock for workspace resolution
# Accessed via additional_contexts: workspace: .
COPY --from=workspace pyproject.toml uv.lock /app/

# Copy MCP package for workspace resolution
# Must copy full directory so uv sync can install the package
COPY --from=workspace mcp/ /app/mcp/

# Copy nanobot-websocket-channel for workspace resolution
# Must be done BEFORE uv sync because the lock file references it
COPY --from=workspace nanobot-websocket-channel /app/nanobot-websocket-channel

# Sync nanobot package with dependencies (nanobot-ai, lms-mcp, nanobot-webchat)
# Install all workspace packages needed by nanobot
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot --package lms-mcp

# ---
# Stage 2: use a final image without uv
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

# Set environment variables for Python and application
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
# The venv is at /app/.venv (root of workspace)
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/nanobot"

# Use the non-root user to run our application
USER nonroot

# Use `/app/nanobot` as the working directory
WORKDIR /app/nanobot

# Run the nanobot gateway via entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
