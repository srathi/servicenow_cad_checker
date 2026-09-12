# ServiceNow Ticket Approval Agent

> Automates ServiceNow approval workflow by checking assets against CAD compliance rules.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)](https://playwright.dev)

---

## Overview

The ServiceNow Ticket Approval Agent automates the manual process of:

1. **Monitoring** ServiceNow for pending approval requests
2. **Searching** assets in IIS server
3. **Validating** CAD compliance rules
4. **Approving/Rejecting** tickets with comments
5. **Logging** all decisions for audit trail

### Key Features

- ✅ **Manual Login** - Uses your existing browser session (no credential storage)
- ✅ **SSO Compatible** - Works with Microsoft ADFS/Azure AD SSO
- ✅ **Browser Automation** - No API access required
- ✅ **CAD Compliance** - Configurable validation rules
- ✅ **Audit Logging** - Full decision trail with timestamps
- ✅ **System/User Tracking** - Know who made each decision

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SERVICE NOW TICKET APPROVAL AGENT                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐                                                 │
│  │   USER LOGIN    │  User completes login manually in browser      │
│  │   (Manual)      │  Agent detects login and takes over            │
│  └────────┬────────┘                                                 │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐     ┌─────────────────┐                       │
│  │  SERVICENOW     │     │   IIS SERVER    │                       │
│  │  BROWSER        │────▶│   BROWSER       │                       │
│  │  AUTOMATION     │◀────│   AUTOMATION    │                       │
│  │                 │     │                 │                       │
│  │  - Fetch Tickets│     │  - Asset Search │                       │
│  │  - Approve      │     │  - CAD Status   │                       │
│  │  - Reject       │     │  - Compliance   │                       │
│  └────────┬────────┘     └────────┬────────┘                       │
│           │                       │                                  │
│           └───────────┬───────────┘                                  │
│                       │                                              │
│                       ▼                                              │
│           ┌─────────────────────┐                                   │
│           │   DECISION ENGINE   │                                   │
│           │                     │                                   │
│           │  - CAD Validation   │                                   │
│           │  - Accept/Reject    │                                   │
│           │  - Comment Generate │                                   │
│           └──────────┬──────────┘                                   │
│                      │                                               │
│                      ▼                                               │
│           ┌─────────────────────┐                                   │
│           │   LOGGING MODULE    │                                   │
│           │                     │                                   │
│           │  - Ticket ID        │                                   │
│           │  - Decision         │                                   │
│           │  - Reason           │                                   │
│           │  - Timestamp        │                                   │
│           │  - System/User Flag │                                   │
│           └─────────────────────┘                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### 1. Clone Repository

```bash
git clone https://github.com/srathi/servicenow_cad_checker.git
cd servicenow_cad_checker
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Update Configuration

Edit `config.yaml` with your server details:

```yaml
snow:
  instance_url: "https://yourcompany.service-now.com"
  
iis:
  base_url: "https://iis-server.company.com"
```

### 4. Run the Agent

```bash
python main.py
```

### 5. Login Manually

The agent will open browser windows for ServiceNow and IIS server. **Complete login manually** using your existing credentials. The agent will detect login and start processing tickets.

---

## How It Works

```
1. Agent opens ServiceNow in browser
         ↓
2. YOU complete login manually (SSO/credentials)
         ↓
3. Agent detects login and takes over
         ↓
4. Agent fetches pending approval tickets
         ↓
5. For each ticket:
   - Searches asset in IIS server
   - Checks CAD compliance
   - Approves or rejects with comment
   - Logs decision
         ↓
6. Waits and repeats
```

---

## Configuration

### config.yaml

```yaml
# ServiceNow Settings
snow:
  instance_url: "https://yourcompany.service-now.com"
  approvals_path: "/approvals.do"

# IIS Server Settings
iis:
  base_url: "https://iis-server.company.com"
  asset_search_path: "/asset-search"

# Browser Settings
browser:
  headless: false      # Set to true for production
  slow_mo: 100         # Delay between actions (ms)
  timeout: 30000       # Timeout for operations (ms)

# Login Settings
login:
  wait_for_login: true
  login_timeout: 120000  # 2 minutes to complete login

# Schedule Settings
schedule:
  interval_minutes: 5  # Check every 5 minutes
  max_runs_per_day: 10 # Safety limit
```

---

## Project Structure

```
snow-agent/
├── config.yaml              # Configuration file
├── main.py                  # Main orchestrator
├── requirements.txt         # Python dependencies
├── modules/
│   ├── __init__.py
│   ├── snow_browser.py      # ServiceNow automation
│   ├── iis_checker.py       # IIS server automation
│   ├── cad_validator.py     # CAD compliance logic
│   ├── decision_engine.py   # Accept/Reject logic
│   └── logger.py            # Decision logging
├── logs/                    # Audit trail
│   └── decisions.csv
├── README.md                # This file
└── USER_GUIDE.md            # Detailed user guide
```

---

## Logging

All decisions are logged to `logs/decisions.csv`:

```csv
timestamp,ticket_id,requestor,asset_id,decision,reason,system_or_user,execution_time_sec
2026-09-11 10:30:15,REQ0012345,john.doe,CAD-WS-001,APPROVED,CAD compliant,system,12.3
```

---

## Documentation

- [README.md](README.md) - This file
- [USER_GUIDE.md](USER_GUIDE.md) - Detailed setup and usage guide

---

## License

MIT License - See [LICENSE](LICENSE) for details.
