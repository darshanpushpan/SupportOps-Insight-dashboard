# SupportOps Insight

A production-support dashboard for IT/application support teams: upload raw application logs, get them parsed and classified automatically, and turn a pile of errors into a professional incident report in a few clicks.

Built with **Python, Flask, and Jinja2** — no JavaScript frameworks, no database. Everything from log parsing to severity scoring to HTML report generation is implemented from scratch to keep the stack small and the logic transparent.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Why I built this

Support and on-call teams spend a lot of time doing the same manual work: pulling raw log files, scanning for errors, figuring out if three tickets are actually one incident, and writing up what happened for escalation. SupportOps Insight automates the repetitive parts of that workflow — parsing, grouping, and severity scoring — so a human can focus on the actual triage decision.

To make the project demonstrate a realistic support environment (not just a log parser), I added a simulated ticket queue, an authentication/application-health signals dashboard, and a runbook knowledge base, all built around one consistent fictional scenario (a retail company called "Northstar Retail" running an order-management system called "OrderFlow"). Every simulated data set is clearly labeled as fictional in the UI.

## Screenshots

**Dashboard** — at-a-glance stats and a guided quick-start
![Dashboard](docs/screenshots/dashboard.png)

**Upload** — multi-file upload with automatic format detection
![Upload](docs/screenshots/upload.png)

**Log Analysis** — filter, search, and group repeated errors by pattern
![Log Analysis](docs/screenshots/analyze.png)

**Incident Report** — a generated, print-ready HTML report
![Incident Report](docs/screenshots/incident-report.png)

**Ticket Queue** — a simulated support queue with SLA tracking and triage
![Tickets](docs/screenshots/tickets.png)

**Operations Signals** — authentication and application health at a glance
![Operations](docs/screenshots/operations.png)

## Features

**Log intelligence**
- Auto-detects and parses four log formats: standard `LEVEL [service] [host] message`, JSON, syslog, and simple `[ERROR] message` styles
- Filters by severity, service, and free-text search; sorts by timestamp or severity
- Groups repeated errors by message pattern and shows occurrence counts, affected services/hosts, and time range
- Severity scoring that combines log level with keyword and service-name heuristics (e.g. `payment`, `auth`, `database` push severity up)

**Incident reporting**
- Generates a self-contained, print-friendly HTML incident report from selected logs or "all errors"
- Auto-computed severity, affected components, top error messages, and a full log table
- Reports are saved to disk and listed on a Reports page for later reference

**Simulated support operations** *(portfolio scenario — clearly labeled as fictional in-app)*
- A 26-ticket support queue with priority, SLA status, triage checklists, timelines, and root-cause notes
- An operations dashboard summarizing authentication events (lockouts, MFA failures, failed-login clustering) and application health (uptime, API latency, job success)
- A runbook knowledge base with cross-linked Markdown docs (rendered by a small built-in Markdown-to-HTML converter) covering incident escalation, account lockouts, MFA troubleshooting, and more

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.8+, Flask 3.0 (application-factory pattern) |
| Parsing / data | Regex-based multi-format log parser, `python-dateutil` for timestamp normalization |
| Templates | Jinja2 |
| Frontend | Vanilla HTML5/CSS3/JS — no build step, no framework |
| Storage | In-memory for parsed logs (per session), flat files (JSON/Markdown) for tickets and docs |
| Deployment | Gunicorn + `render.yaml` / `Procfile` for one-click deploy |

## Architecture

```
Upload (Flask route) → LogParser (auto-detect format) → in-memory store
                                                              │
                              ┌───────────────────────────────┤
                              ▼                                ▼
                    SeverityClassifier                  Analysis UI
                    (score + group errors)          (filter/search/sort)
                              │
                              ▼
                    IncidentGenerator
                    (renders self-contained HTML report)
```

- **`utils/log_parser.py`** — tries JSON, then standard, then syslog, then simple regex patterns against each line; normalizes every match into a common schema (`timestamp`, `level`, `service`, `host`, `message`, …).
- **`utils/severity_classifier.py`** — scores each entry (base severity from log level, +1 per matched critical keyword/service) and groups related errors by the first 50 characters of their message.
- **`utils/incident_generator.py`** — renders a complete, inline-styled HTML report (no external CSS dependency, so it's portable and print-safe).
- **`utils/ticket_store.py`**, **`utils/ops_signals.py`**, **`utils/markdown_lite.py`** — support the simulated ticket queue, auth/health signal aggregation, and the runbook viewer, respectively.

## Getting Started

```bash
git clone https://github.com/darshanpushpan/SupportOps-Insight-dashboard.git
cd SupportOps-Insight-dashboard

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Sample log files (`sample_standard.log`, `sample_json.log`, `sample_syslog.log`) are included in the repo root for quick testing.

To populate the simulated ticket queue and operations dashboard with fresh fictional data:

```bash
python scripts/generate_sample_tickets.py
python scripts/generate_sample_logs.py
python scripts/analyze_auth_logs.py
```

## Project Structure

```
SupportOps-Insight-dashboard/
├── app.py                       # Flask app factory and all routes
├── config.py                    # Dev/production configuration
├── requirements.txt
├── render.yaml / Procfile       # Deployment config (Render / Heroku-style)
├── utils/
│   ├── log_parser.py            # Multi-format log parsing
│   ├── severity_classifier.py   # Error grouping and severity scoring
│   ├── incident_generator.py    # HTML incident report generation
│   ├── ticket_store.py          # Simulated ticket queue + metrics
│   ├── ops_signals.py           # Auth/app health signal aggregation
│   └── markdown_lite.py         # Dependency-free Markdown renderer
├── scripts/                     # Generators for the simulated data sets
├── templates/                   # Jinja2 templates
├── static/{css,js}/             # Styles and frontend interactivity
├── docs/                        # Runbooks + incident write-ups (Markdown)
├── data/                        # Simulated ticket data (JSON)
├── uploads/ / reports/ / logs/  # Runtime storage (auto-created)
└── sample_*.log                 # Sample files for each supported format
```

## API

```
GET /api/logs/<file_id>?level=ERROR&search=timeout&sort_by=timestamp&sort_order=desc
```

Returns JSON with the filtered log entries and computed error groups for a given uploaded file.

## Deployment

The repo includes a `render.yaml` blueprint and `Procfile`, so it deploys to [Render](https://render.com) in a few clicks: **New +** → **Blueprint** → select this repo. Gunicorn serves the app in production; `SECRET_KEY` is auto-generated by the blueprint.

> Note: the free tier's filesystem is ephemeral — uploaded logs and generated reports won't survive a redeploy. Fine for a demo, not for production use without persistent storage.

## License

MIT
