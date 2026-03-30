#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config.json at runtime,
then launches `nanobot gateway`.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    # Paths
    config_path = Path("/app/nanobot/config.json")
    workspace_path = Path("/app/nanobot/workspace")
    resolved_path = Path("/app/nanobot/config.resolved.json")

    # Load base config
    with open(config_path) as f:
        config = json.load(f)

    # Resolve LLM provider API key and base URL from env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base_url = os.environ.get("LLM_API_BASE_URL")
    llm_api_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        config["providers"]["custom"]["apiKey"] = llm_api_key
    if llm_api_base_url:
        config["providers"]["custom"]["apiBase"] = llm_api_base_url
    if llm_api_model:
        config["agents"]["defaults"]["model"] = llm_api_model

    # Resolve gateway host/port from env vars
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")

    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)

    # Resolve MCP server environment variables
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")

    if "mcpServers" in config.get("tools", {}):
        if "lms" in config["tools"]["mcpServers"]:
            if lms_backend_url:
                config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = (
                    lms_backend_url
                )
            if lms_api_key:
                config["tools"]["mcpServers"]["lms"]["env"]["NANOBOT_LMS_API_KEY"] = (
                    lms_api_key
                )

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    # Launch nanobot gateway using subprocess
    # The venv is at /app/.venv (workspace root)
    nanobot_exe = str(Path("/app/.venv/bin/nanobot"))

    subprocess.run(
        [
            nanobot_exe,
            "gateway",
            "--config",
            str(resolved_path),
            "--workspace",
            str(workspace_path),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
