# Hangeul Turtle

Hangeul Turtle is a safety-first, local Red–Blue AI security laboratory. It evaluates approved virtual attack scenarios, synthetic insider-risk behavior, multi-model Blue analysis, independent policy decisions, and audit integrity without touching real customer data, IoT devices, firewalls, or external attack targets.

> This repository is an experimental security testbed. It is not an intrusion tool, IPS, production access-control system, or proof of real-world network blocking.

## What is implemented

- Approved Red scenario interface with schema validation, bounded steps, seeds, run IDs, and fail-closed errors.
- CyberBattleSim execution through a Docker-isolated child worker.
- Blue analysis with dry-run policies and administrator approval requirements.
- Conditional collaboration path for Qwen2.5 7B, Qwen3 4B, Gemma3 4B, and Phi-4 Mini through local Ollama structured output.
- Independent evaluation that separates detection from blocking. Abstract CyberBattleSim state cannot prove real blocking, so blocking remains `unknown`.
- Synthetic insider-risk analysis, high-risk approval controls, SHA-256 hash-chained audit records, and an isolated `jeon.txt` probe.
- Suricata offline PCAP to EVE JSON to common event to Blue dry-run path. Live capture and IPS are excluded.

## Safety boundaries

The system accepts approved scenario identifiers and synthetic event fields only. It does not accept arbitrary shell commands, URLs, IP targets, customer records, or tool instructions from Red input.

External network scanning or attacks, real customer accounts, IoT devices, real firewall changes, automatic policy promotion, external notifications, and storage of tokens/passwords/raw customer data are intentionally excluded.

CyberBattleSim runs inside the existing Docker boundary with an internal network, read-only filesystem, dropped capabilities, no-new-privileges, CPU/memory/PID limits, and bounded worker timeouts.

## Requirements

- Python 3.12+
- Docker Desktop / Docker Compose for CyberBattleSim execution
- Optional local Ollama for sLLM experiments
- Optional Suricata 7.x for offline PCAP analysis

Models used by the current local setup: `qwen2.5:7b`, `qwen3:4b`, `gemma3:4b`, and `phi4-mini:latest`.

## Quick start

```bash
cd /root/AI_Home_Shield_v3
python3 -m unittest discover -s tests -v
python3 -m compileall -q backend agents evaluator simulator red_team suricata_offline insider longrun tests
docker compose config
```

Generate synthetic events:

```bash
python3 simulator/generate_events.py --scenario login_burst --seed 42 --output /tmp/hangeul-turtle-events.jsonl
```

Run an isolated CyberBattleSim scenario:

```bash
AI_HOME_SHIELD_CYBERBATTLE_EXECUTOR=docker python3 -c 'from red_team.battle import run; import json; print(json.dumps(run({"scenario_id":"red-test-002","environment":"cyberbattlesim","objective":"evaluate_detection","strategy":"multi_step_simulated_intrusion","max_steps":3,"seed":100010}), ensure_ascii=False, indent=2))'
```

Run the dedicated Red API on port 8091 with a dedicated secret supplied through the environment. Never use `demo-token`:

```bash
export AI_HOME_SHIELD_RED_TOKEN="generate-a-dedicated-local-secret"
python3 -m backend.red_api --host 127.0.0.1 --port 8091 --allow-ip 127.0.0.1
```

Existing deployments preserve the 8080/8501/8091 arrangement. Do not expose these ports publicly without a separately reviewed deployment design.

## Tests and reports

The regression suite covers API authentication and allow-lists, Docker isolation markers, actual-result boundaries, Blue collaboration, insider approval controls, audit tamper detection, Suricata EVE conversion, Red–Blue battles, and the isolated file probe.

Latest local validation: 36/36 tests passed. The 12-hour local stability experiment recorded 116 synthetic/isolated events with zero execution errors. Runtime event streams are intentionally ignored by Git; reports remain local operator records.

Important reports: `NEXT_STAGE_REPORT.md`, `RED_BLUE_BATTLE_REPORT.md`, `RED_BLUE_3H_FAILURE_ANALYSIS.md`, `RED_BLUE_12H_REPORT.md`, `INSIDER_THREAT_EVALUATION.md`, `APPROVAL_AUDIT_REPORT.md`, `SURICATA_OFFLINE_REPORT.md`, `OPEN_SOURCE_RESEARCH.md`, and `AI_ATTACK_PATTERN_RESEARCH.md`.

## Repository layout

```text
backend/          Red API and laboratory server
agents/blue/      Rule analysis, Ollama adapter, multi-model collaboration
red_team/         Approved Red scenarios and isolated file probe
simulator/        CyberBattleSim adapter, worker, and synthetic events
evaluator/        Independent evaluation and holdout logic
insider/          Behavior analysis, approval engine, audit chain
suricata_offline/ EVE JSON parser and Blue boundary
longrun/          Bounded unattended experiment scheduler
tests/            Regression and safety tests
```

## License

Add the project license before publishing a public release. Third-party model and tool terms are separate from this repository; review each model card and dependency license before redistribution or commercial use.
