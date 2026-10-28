<div align="center">
  <img src="assets/banner.svg" width="100%"/>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/automation-n8n-ff0033?style=flat-square" alt="automation">
  <img src="https://img.shields.io/badge/SOAR-incident_response-00ff88?style=flat-square" alt="SOAR">
  <img src="https://img.shields.io/badge/enrichment-VirusTotal-3949ab?style=flat-square" alt="enrichment">
</p>


<p align="center">
  <img src="https://img.shields.io/badge/n8n-workflow-00b4d8?style=flat-square" alt="n8n">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square" alt="Docker">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
</p>

Automated security incident response platform built on n8n — processes alerts from LogMind, CloudSentry, and external sources, enriches them with threat intelligence, and executes response playbooks in under 5 seconds.

## Architecture

```mermaid
graph TB
    subgraph "Alert Sources"
        LM[LogMind<br/>Log Analysis]
        CS[CloudSentry<br/>Cloud Security]
        EXT[External<br/>Alerts]
    end

    subgraph "SecureFlow n8n Platform"
        WH[Webhook Receivers]
        EN[Threat Enrichment]
        RP[Response Playbooks]
        AL[Approval Logic]
    end

    subgraph "Threat Intelligence"
        VT[VirusTotal API]
        AI[AbuseIPDB]
        VG[VectorGuard API]
        SH[Shodan API]
        WHO[WHOIS API]
    end

    subgraph "Response Actions"
        SL[Slack Alerts]
        JR[Jira Tickets]
        OCI[OCI API<br/>Isolation]
        EM[Email Notifications]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Audit Logs)]
        RD[(Redis<br/>Queue)]
        METRICS[Prometheus<br/>Metrics]
    end

    LM --> WH
    CS --> WH
    EXT --> WH

    WH --> EN
    EN --> VT
    EN --> AI
    EN --> VG
    EN --> SH
    EN --> WHO

    EN --> RP
    RP --> AL
    AL --> SL
    AL --> JR
    AL --> OCI
    AL --> EM

    WH --> PG
    RP --> RD
    SL --> METRICS
```

## Components

### n8n Workflow Engine
- **Webhook Receivers** — HTTP endpoints for LogMind, CloudSentry, external alerts
- **Threat Enrichment Nodes** — Parallel API calls across VirusTotal, AbuseIPDB, Shodan, WHOIS
- **Response Playbooks** — Automated incident workflows per threat category
- **Approval Logic** — Human-in-the-loop gate for destructive actions

### Playbook Library

| # | Playbook | Trigger |
|---|----------|---------|
| 1 | Malware Detection Response | Hash match, file alert |
| 2 | Brute Force Mitigation | Failed auth threshold |
| 3 | Data Exfiltration Investigation | Anomalous outbound traffic |
| 4 | Cloud Misconfiguration Remediation | CloudSentry finding |
| 5 | Phishing Email Analysis | Suspicious sender/URL |
| 6 | Suspicious Login Investigation | Geo/device anomaly |

### Integration Layer
- **Threat Intel APIs** — VirusTotal, AbuseIPDB, Shodan, WHOIS
- **Internal APIs** — VectorGuard threat query, OCI cloud operations
- **Communication** — Slack notifications, Jira ticket creation

### Data Layer
- **PostgreSQL** — Audit trails, incident history, SLA metrics
- **Redis** — Message queuing, workflow state
- **Prometheus** — Performance metrics, success rates, response times

## Technology Stack

| Component | Technology |
|-----------|------------|
| Workflow Engine | n8n |
| Orchestration | Docker Compose |
| Database | PostgreSQL |
| Queue | Redis |
| Mock Services | Python + Flask |
| Proxy | Nginx |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

```bash
git clone https://github.com/sinCodes11/secureflow SecureFlow
cd SecureFlow

cp .env.example .env
# Edit .env with your settings

docker-compose up -d

# Access n8n at http://localhost:5678
# Import workflows from /workflows/
```

## Security Model

- n8n user auth + API key validation on all webhook endpoints
- Webhook input sanitization and rate limiting
- Secrets via environment variables (Vault-ready)
- Complete audit trail for every automated action

## Performance Targets

| Metric | Target |
|--------|--------|
| Alert enrichment time | < 5 seconds |
| Throughput | 100+ incidents/hour |
| SLA acknowledgement | 95% within 2 minutes |

## Repository Structure

```
SecureFlow/
├── docker-compose.yml
├── .env.example
├── workflows/
│   ├── malware-response.json
│   ├── brute-force-mitigation.json
│   ├── data-exfiltration.json
│   ├── cloud-remediation.json
│   ├── phishing-analysis.json
│   └── suspicious-login.json
├── mock-apis/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── database/
│   ├── init.sql
│   └── audit-schema.sql
├── docs/
│   ├── playbook-guide.md
│   └── api-integration.md
└── scripts/
    ├── setup.sh
    └── generate-test-data.py
```

## License

MIT
