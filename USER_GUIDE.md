# ServiceNow Ticket Approval Agent - User Guide

> Complete guide for setting up and running the ServiceNow Ticket Approval Agent

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Agent](#running-the-agent)
6. [Understanding the Output](#understanding-the-output)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)
9. [FAQ](#faq)

---

## Introduction

### What is this Agent?

The ServiceNow Ticket Approval Agent is an automated tool that:

- Monitors ServiceNow for pending approval requests
- Checks assets in your IIS server
- Validates CAD compliance rules
- Automatically approves or rejects tickets
- Logs all decisions for audit purposes

### Who should use this?

- IT administrators handling ServiceNow approvals
- Teams with repeated approval workflows
- Organizations with CAD compliance requirements

### Benefits

| Manual Process | With Agent |
|----------------|------------|
| 2-3 times/day manual checking | Automatic monitoring |
| Human error possible | Consistent rule application |
| No audit trail | Full logging with timestamps |
| Time-consuming | Saves hours per week |

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | macOS, Linux, or Windows |
| Python | 3.10 or higher |
| RAM | 4 GB minimum |
| Disk Space | 500 MB |
| Network | Access to ServiceNow and IIS server |

### Software Dependencies

- Python 3.10+
- pip (Python package manager)
- Chromium browser (installed by Playwright)

---

## Installation

### Step 1: Navigate to Project Directory

```bash
cd /Users/sandesh/Desktop/myProjects/snow-agent
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `playwright` - Browser automation
- `pyyaml` - Configuration file handling
- `python-dotenv` - Environment variable management

### Step 3: Install Chromium Browser

```bash
playwright install chromium
```

This downloads Chromium browser (required for automation).

### Step 4: Verify Installation

```bash
python -c "import playwright; print('Playwright installed successfully')"
```

---

## Configuration

### Step 1: Create Environment File

```bash
cp .env.example .env
```

### Step 2: Edit Environment File

Open `.env` in any text editor:

```bash
nano .env
# Or use VS Code, Vim, etc.
```

Add your credentials:

```bash
# ServiceNow Credentials
SNOW_USERNAME=your.snow.username
SNOW_PASSWORD=your.snow.password

# IIS Server Credentials
IIS_USERNAME=your.iis.username
IIS_PASSWORD=your.iis.password
```

**IMPORTANT:** Never commit `.env` to version control!

### Step 3: Edit Configuration File

Open `config.yaml`:

```bash
nano config.yaml
```

#### ServiceNow Configuration

```yaml
snow:
  instance_url: "https://yourcompany.service-now.com"  # Your instance URL
  login_path: "/login.do"                              # Login page path
  approvals_path: "/approvals.do"                      # Approvals list path
```

**How to find your ServiceNow URL:**
1. Open your browser
2. Go to your ServiceNow portal
3. Copy the URL (e.g., `https://mycompany.service-now.com`)

#### IIS Server Configuration

```yaml
iis:
  base_url: "https://iis-server.company.com"  # Your IIS server URL
  login_path: "/login"                         # Login page path
  asset_search_path: "/asset-search"           # Asset search page path
```

#### Browser Settings

```yaml
browser:
  headless: false      # false = visible browser, true = invisible
  slow_mo: 100         # Milliseconds between actions (increase if unstable)
  timeout: 30000       # Timeout in milliseconds (30 seconds)
```

**Recommendation for first run:**
```yaml
browser:
  headless: false      # Keep visible to see what's happening
  slow_mo: 500         # Slower for debugging
  timeout: 60000       # Longer timeout
```

#### Schedule Settings

```yaml
schedule:
  enabled: true
  interval_minutes: 5  # Check every 5 minutes
  max_runs_per_day: 10 # Stop after 10 runs (safety limit)
```

### Step 4: Configure CAD Rules (Optional)

When ready to enable CAD validation:

```yaml
cad_rules:
  enabled: true  # Change from false to true
  rules:
    - name: "license_check"
      field: "software_license"
      condition: "valid"
      failure_message: "Software license is not active"
    
    - name: "version_check"
      field: "version"
      condition: ">=2.0"
      expected: "2.0"
      failure_message: "Software version is outdated"
```

---

## Running the Agent

### First Run (Testing)

1. **Open Terminal**

2. **Navigate to project:**
   ```bash
   cd /Users/sandesh/Desktop/myProjects/snow-agent
   ```

3. **Run the agent:**
   ```bash
   python main.py
   ```

4. **Watch the output:**
   ```
   ============================================================
   🚀 ServiceNow Ticket Approval Agent
   ============================================================
   
   📋 CAD Validation: CAD rules are DISABLED
   
   🌐 Starting browser...
   
   🔑 Logging into ServiceNow...
   ✅ SSO Login successful
   
   🔑 Logging into IIS server...
   ✅ IIS Login successful
   
   ============================================================
   📋 Check #1 at 2026-09-11 10:30:15
   ============================================================
   📋 Found 3 pending approvals
   
   🔄 Processing ticket: REQ0012345
      Asset: CAD-WS-001
      🔍 Found asset: CAD-WS-001
      ✅ Completed in 12.3s - Decision: APPROVED
   
   🔄 Processing ticket: REQ0012346
      Asset: CAD-WS-002
      🔍 Found asset: CAD-WS-002
      ✅ Completed in 8.7s - Decision: REJECTED
   
   📊 Stats: 2 total | 1 approved | 1 rejected
   
   ⏰ Waiting 5 minutes until next check...
   ```

### Production Run

For unattended operation:

1. **Edit config.yaml:**
   ```yaml
   browser:
     headless: true       # Invisible browser
     slow_mo: 100         # Normal speed
   ```

2. **Run in background:**
   ```bash
   # macOS/Linux
   nohup python main.py > agent.log 2>&1 &
   
   # Or use screen/tmux
   screen -S snow-agent
   python main.py
   # Detach: Ctrl+A, D
   ```

3. **Stop the agent:**
   ```bash
   # Find process
   ps aux | grep main.py
   
   # Kill process
   kill <PID>
   ```

---

## Understanding the Output

### Console Output

| Symbol | Meaning |
|--------|---------|
| ✅ | Success |
| ❌ | Error |
| 🔄 | Processing |
| 📋 | Information |
| ⏰ | Waiting |
| 🔍 | Found |
| 🔑 | Authentication |
| 🌐 | Browser |

### Decision Log (CSV)

Located at: `logs/decisions.csv`

```csv
timestamp,ticket_id,requestor,asset_id,decision,reason,system_or_user,execution_time_sec
2026-09-11 10:30:15,REQ0012345,john.doe,CAD-WS-001,APPROVED,CAD compliant,system,12.3
```

**Reading the log:**
- `timestamp`: When the decision was made
- `ticket_id`: ServiceNow ticket number
- `requestor`: Person who requested
- `asset_id`: Asset being requested
- `decision`: APPROVED or REJECTED
- `reason`: Why this decision was made
- `system_or_user`: "system" = auto, "user" = manual override
- `execution_time_sec`: How long it took

### Viewing Statistics

```python
from modules.logger import DecisionLogger

logger = DecisionLogger()
stats = logger.get_stats()
print(stats)
# Output: {'total': 25, 'approved': 20, 'rejected': 5, 'approval_rate': '80.0%'}
```

---

## Troubleshooting

### Issue: SSO Login Fails

**Symptoms:**
```
❌ SSO Login failed: Timeout waiting for selector
```

**Solutions:**
1. Check your SSO login URL in config.yaml
2. Update the login selectors in `modules/snow_browser.py`:
   ```python
   # Find this line and update the selector
   self.page.fill('input[name="username"]', username)  # Update selector
   ```
3. Take a screenshot to debug:
   ```python
   self.page.screenshot(path="debug_sso.png")
   ```

### Issue: IIS Connection Error

**Symptoms:**
```
❌ IIS Login failed: net::ERR_CONNECTION_REFUSED
```

**Solutions:**
1. Verify IIS server URL is correct
2. Check if you're on VPN/network
3. Test manually in browser first

### Issue: No Tickets Found

**Symptoms:**
```
📋 Found 0 pending approvals
```

**Solutions:**
1. Verify ServiceNow approvals path
2. Check if you have approval permissions
3. Look for tickets manually in ServiceNow

### Issue: Browser Crashes

**Symptoms:**
```
❌ Agent error: Browser closed unexpectedly
```

**Solutions:**
1. Increase timeout in config.yaml:
   ```yaml
   browser:
     timeout: 60000  # Increase to 60 seconds
   ```
2. Check available memory
3. Reduce slow_mo value

### Debug Mode

1. **Enable screenshots:**
   ```python
   # In any module, add:
   self.page.screenshot(path="debug.png")
   ```

2. **Enable verbose logging:**
   ```yaml
   # config.yaml
   logging:
     log_level: "DEBUG"
   ```

3. **Run with visible browser:**
   ```yaml
   browser:
     headless: false
     slow_mo: 1000  # Very slow
   ```

---

## Maintenance

### Daily Checks

1. **Review decision log:**
   ```bash
   tail -20 logs/decisions.csv
   ```

2. **Check agent status:**
   ```bash
   ps aux | grep main.py
   ```

### Weekly Maintenance

1. **Archive old logs:**
   ```bash
   mv logs/decisions.csv logs/decisions_$(date +%Y%m%d).csv
   ```

2. **Check for errors:**
   ```bash
   grep "REJECTED" logs/decisions.csv | wc -l
   ```

### Updating the Agent

1. **Backup config:**
   ```bash
   cp config.yaml config.yaml.backup
   cp .env .env.backup
   ```

2. **Pull updates:**
   ```bash
   git pull
   ```

3. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test changes:**
   ```bash
   python main.py
   ```

---

## FAQ

### Q: Can I run this on a server?

**A:** Yes, but you'll need:
- Display server (X11) or use headless mode
- Network access to ServiceNow and IIS
- Consider Docker for easier deployment

### Q: What if my password changes?

**A:** Update `.env` file:
```bash
SNOW_PASSWORD=new_password
```

### Q: Can I approve tickets manually?

**A:** Yes, the agent logs both system and user decisions. Manual approvals show as "user" in the log.

### Q: How do I add new CAD rules?

**A:** Edit `config.yaml` under `cad_rules.rules`. See [CAD Rules Configuration](#step-4-configure-cad-rules-optional).

### Q: Can I customize the approval comment?

**A:** Yes, edit `modules/decision_engine.py`:
```python
def get_comment_for_approval(self, asset):
    return f"Custom comment: Asset {asset.get('asset_id')}"
```

### Q: What happens if the agent crashes?

**A:** Check `logs/decisions.csv` for the last successful operation. Restart the agent:
```bash
python main.py
```

### Q: Can I run multiple instances?

**A:** Not recommended. Use one instance with appropriate schedule settings.

### Q: How do I know if the agent is running?

**A:** Check process:
```bash
ps aux | grep main.py
```

Or check logs:
```bash
tail -f logs/decisions.csv
```

---

## Support

For issues or questions:

1. Check this User Guide
2. Review [Troubleshooting](#troubleshooting) section
3. Check the [README.md](README.md)
4. Create an issue in the repository

---

## Changelog

### Version 1.0.0 (2026-09-11)

- Initial release
- ServiceNow browser automation
- IIS server integration
- CAD compliance validation (placeholder)
- Decision logging
- Configurable schedule

---

*Last updated: September 11, 2026*
