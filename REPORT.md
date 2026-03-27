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

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
