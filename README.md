# ServiceNow Ticket Approval Agent

> Automates ServiceNow approval workflow by checking assets against CAD compliance rules.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)](https://playwright.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

The ServiceNow Ticket Approval Agent automates the manual process of:

1. **Monitoring** ServiceNow for pending approval requests
2. **Searching** assets in IIS server
3. **Validating** CAD compliance rules
4. **Approving/Rejecting** tickets with comments
5. **Logging** all decisions for audit trail

### Key Features

- ✅ **SSO Authentication** - Handles Microsoft ADFS/Azure AD SSO
- ✅ **Browser Automation** - No API access required
- ✅ **CAD Compliance** - Configurable validation rules
- ✅ **Audit Logging** - Full decision trail with timestamps
- ✅ **System/User Tracking** - Know who made each decision
- ✅ **Configurable Schedule** - Run 2-3 times/day or more

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SERVICE NOW TICKET APPROVAL AGENT                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐                                                 │
│  │   SCHEDULE      │  Check every 5 minutes / 2-3 times per day    │
│  │   (APScheduler) │                                                 │
│  └────────┬────────┘                                                 │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐     ┌─────────────────┐                       │
│  │  SERVICENOW     │     │   IIS SERVER    │                       │
│  │  BROWSER        │────▶│   BROWSER       │                       │
│  │  AUTOMATION     │◀────│   AUTOMATION    │                       │
│  │                 │     │                 │                       │
│  │  - SSO Login    │     │  - Asset Search │                       │
│  │  - Fetch Tickets│     │  - CAD Status   │                       │
│  │  - Approve      │     │  - Compliance   │                       │
│  │  - Reject       │     │                 │                       │
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

## Project Structure

```
snow-agent/
│
├── config.yaml                 # Main configuration file
├── main.py                     # Main orchestrator script
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .env                        # Your credentials (DO NOT COMMIT)
│
├── modules/                    # Core modules
│   ├── __init__.py
│   ├── snow_browser.py        # ServiceNow browser automation
│   ├── iis_checker.py         # IIS server browser automation
│   ├── cad_validator.py       # CAD compliance validation
│   ├── decision_engine.py     # Accept/Reject decision logic
│   └── logger.py              # Decision logging to CSV
│
├── logs/                       # Audit trail
│   └── decisions.csv           # All decisions logged here
│
├── README.md                   # This file
├── USER_GUIDE.md               # Detailed user guide
└── LICENSE                     # MIT License
```

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional)

### 1. Clone or Download

```bash
cd /Users/sandesh/Desktop/myProjects
git clone <repository-url> snow-agent
# Or copy the folder manually
```

### 2. Install Dependencies

```bash
cd snow-agent
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Credentials

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 4. Update Configuration

Edit `config.yaml` with your server details:

```yaml
snow:
  instance_url: "https://yourcompany.service-now.com"
  
iis:
  base_url: "https://iis-server.company.com"
```

### 5. Run the Agent

```bash
python main.py
```

---

## Configuration

### config.yaml

```yaml
# ServiceNow Settings
snow:
  instance_url: "https://yourcompany.service-now.com"
  login_path: "/login.do"
  approvals_path: "/approvals.do"

# IIS Server Settings
iis:
  base_url: "https://iis-server.company.com"
  login_path: "/login"
  asset_search_path: "/asset-search"

# Browser Settings
browser:
  headless: false          # true = invisible browser
  slow_mo: 100             # delay between actions (ms)
  timeout: 30000           # timeout for operations (ms)

# Schedule Settings
schedule:
  interval_minutes: 5      # check frequency
  max_runs_per_day: 10     # safety limit

# Logging
logging:
  log_dir: "./logs"
  log_file: "decisions.csv"
```

### Environment Variables (.env)

```bash
# ServiceNow
SNOW_USERNAME=your.username
SNOW_PASSWORD=your.password

# IIS Server
IIS_USERNAME=your.username
IIS_PASSWORD=your.password
```

---

## CAD Compliance Rules

### Current Status

CAD rules are **configurable** but currently set as placeholder. When ready, edit `config.yaml`:

```yaml
cad_rules:
  enabled: true
  rules:
    - name: "license_check"
      field: "software_license"
      condition: "valid"
      failure_message: "License is not active"
    
    - name: "version_check"
      field: "version"
      condition: ">=2.0"
      expected: "2.0"
      failure_message: "Version too old"
    
    - name: "expiry_check"
      field: "expiry_date"
      condition: "not_expired"
      failure_message: "License expired"
    
    - name: "department_check"
      field: "department"
      condition: "in_allowed"
      allowed_values: ["Engineering", "IT", "Design"]
      failure_message: "Department not authorized"
```

---

## Logging

### Decision Log Format

All decisions are logged to `logs/decisions.csv`:

```csv
timestamp,ticket_id,requestor,asset_id,decision,reason,system_or_user,execution_time_sec,details
2026-09-11 10:30:15,REQ0012345,john.doe,CAD-WS-001,APPROVED,CAD compliant: All rules passed,system,12.3,
2026-09-11 10:31:22,REQ0012346,jane.smith,CAD-WS-002,REJECTED,Non-compliant: License expired,system,8.7,
2026-09-11 14:15:00,REQ0012347,bob.wilson,CAD-WS-003,APPROVED,Manual override,user,0,Manual approval by admin
```

### Log Fields

| Field | Description |
|-------|-------------|
| timestamp | When the decision was made |
| ticket_id | ServiceNow ticket ID |
| requestor | Who requested the ticket |
| asset_id | Asset being requested |
| decision | APPROVED or REJECTED |
| reason | Why the decision was made |
| system_or_user | "system" for auto, "user" for manual |
| execution_time_sec | How long the process took |
| details | Additional information |

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| SSO Login fails | Update login selectors in `snow_browser.py` |
| IIS connection error | Check IIS server URL and network |
| No tickets found | Verify ServiceNow approvals path |
| Browser crashes | Increase timeout in config.yaml |

### Debug Mode

Run with visible browser:

```yaml
# config.yaml
browser:
  headless: false
  slow_mo: 500  # Slower for debugging
```

### View Logs

```bash
# View recent decisions
tail -20 logs/decisions.csv

# View stats
python -c "from modules.logger import DecisionLogger; print(DecisionLogger().get_stats())"
```

---

## Future Enhancements

- [ ] **Docker Support** - Containerized deployment
- [ ] **ServiceNow API** - Direct API integration (if available)
- [ ] **Webhook Support** - Real-time ticket processing
- [ ] **Dashboard** - Web UI for monitoring
- [ ] **Email Notifications** - Alert on rejections
- [ ] **Multi-ticket Processing** - Parallel approval handling

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

For issues or questions:
- Check the [User Guide](USER_GUIDE.md)
- Review [Troubleshooting](#troubleshooting) section
- Create an issue in the repository

---

## Acknowledgments

- [Playwright](https://playwright.dev) - Browser automation
- [ServiceNow](https://servicenow.com) - Ticketing system
- Python community for amazing libraries
