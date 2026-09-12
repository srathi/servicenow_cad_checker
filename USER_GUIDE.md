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
8. [FAQ](#faq)

---

## Introduction

### What is this Agent?

The ServiceNow Ticket Approval Agent is an automated tool that:

- Monitors ServiceNow for pending approval requests
- Checks assets in your IIS server
- Validates CAD compliance rules
- Automatically approves or rejects tickets
- Logs all decisions for audit purposes

### How It Works (No Credentials Needed!)

```
1. You run the agent
2. Agent opens browser windows
3. YOU login manually using your existing credentials/SSO
4. Agent detects login is complete
5. Agent takes over and processes tickets automatically
6. Agent logs all decisions for audit
```

**Key Point:** The agent never sees or stores your passwords. You login manually, and the agent uses the active browser session.

---

## System Requirements

| Component | Requirement |
|-----------|-------------|
| Operating System | macOS, Linux, or Windows |
| Python | 3.10 or higher |
| RAM | 4 GB minimum |
| Disk Space | 500 MB |
| Network | Access to ServiceNow and IIS server |

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/srathi/servicenow_cad_checker.git
cd servicenow_cad_checker
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Chromium Browser

```bash
playwright install chromium
```

### Step 4: Verify Installation

```bash
python -c "import playwright; print('Installation successful')"
```

---

## Configuration

### Edit config.yaml

Open `config.yaml` in any text editor:

```bash
nano config.yaml
```

#### ServiceNow Configuration

```yaml
snow:
  instance_url: "https://yourcompany.service-now.com"  # Your instance URL
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
  asset_search_path: "/asset-search"           # Asset search page path
```

#### Browser Settings

```yaml
browser:
  headless: false      # false = visible browser, true = invisible
  slow_mo: 100         # Milliseconds between actions
  timeout: 30000       # Timeout in milliseconds
```

**Recommendation for first run:**
```yaml
browser:
  headless: false      # Keep visible to see what's happening
  slow_mo: 500         # Slower for debugging
  timeout: 60000       # Longer timeout
```

#### Login Settings

```yaml
login:
  wait_for_login: true
  login_timeout: 120000  # 2 minutes to complete manual login
```

#### Schedule Settings

```yaml
schedule:
  interval_minutes: 5  # Check every 5 minutes
  max_runs_per_day: 10 # Stop after 10 runs
```

---

## Running the Agent

### First Run (Testing)

1. **Open Terminal**

2. **Navigate to project:**
   ```bash
   cd /path/to/servicenow_cad_checker
   ```

3. **Run the agent:**
   ```bash
   python main.py
   ```

4. **Follow the prompts:**
   ```
   ============================================================
   🚀 ServiceNow Ticket Approval Agent
   ============================================================
   
   📌 Agent will open browser windows.
      Please complete login manually when prompted.
      Agent will take over after login is detected.
   
   📋 CAD Validation: CAD rules are DISABLED
   
   🌐 Starting browser...
   
   🔑 Step 1: Login to ServiceNow
   
   🔑 Opening ServiceNow: https://yourcompany.service-now.com
      👉 Please complete login in the browser window
      ⏳ Waiting for login (timeout: 120s)...
   ```

5. **Complete login in browser:**
   - The browser window will open
   - Login using your normal credentials/SSO
   - The agent will detect when login is complete

6. **Agent takes over:**
   ```
   ✅ Login detected! Agent is now active.
   
   🔑 Step 2: Login to IIS Server
   
   🔑 Opening IIS Server: https://iis-server.company.com
      👉 Please complete login in the browser window
      ⏳ Waiting for login (timeout: 120s)...
   
   ✅ IIS Login detected! Agent is now active.
   
   ============================================================
   ✅ Agent is now ACTIVE and monitoring tickets
   ============================================================
   
   ============================================================
   📋 Check #1 at 2026-09-11 10:30:15
   ============================================================
   📋 Found 3 pending approvals
   
   🔄 Processing ticket: REQ0012345
      Asset: CAD-WS-001
      🔍 Found asset: CAD-WS-001
      ✅ Completed in 12.3s - Decision: APPROVED
   
   📊 Stats: 1 total | 1 approved | 0 rejected
   
   ⏰ Waiting 5 minutes until next check...
   ```

### Stopping the Agent

Press `Ctrl+C` in the terminal to stop the agent.

---

## Understanding the Output

### Console Symbols

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
| 👉 | Action required from user |

### Decision Log

Located at: `logs/decisions.csv`

```csv
timestamp,ticket_id,requestor,asset_id,decision,reason,system_or_user,execution_time_sec
2026-09-11 10:30:15,REQ0012345,john.doe,CAD-WS-001,APPROVED,CAD compliant,system,12.3
```

**Log Fields:**

| Field | Description |
|-------|-------------|
| timestamp | When the decision was made |
| ticket_id | ServiceNow ticket ID |
| requestor | Who requested the ticket |
| asset_id | Asset being requested |
| decision | APPROVED or REJECTED |
| reason | Why the decision was made |
| system_or_user | "system" for auto, "user" for manual |
| execution_time_sec | How long it took |

---

## Troubleshooting

### Issue: Agent doesn't detect login

**Symptoms:**
```
❌ Login timeout or error
```

**Solutions:**
1. Ensure you completed login in the browser
2. Increase login timeout in config.yaml:
   ```yaml
   login:
     login_timeout: 180000  # 3 minutes
   ```
3. Check if SSO requires additional steps

### Issue: No tickets found

**Symptoms:**
```
📋 Found 0 pending approvals
```

**Solutions:**
1. Verify ServiceNow approvals path in config.yaml
2. Check if you have approval permissions
3. Look for tickets manually in ServiceNow

### Issue: Browser doesn't open

**Symptoms:**
```
❌ Agent error: Browser failed to start
```

**Solutions:**
1. Reinstall Chromium:
   ```bash
   playwright install chromium
   ```
2. Check available memory
3. Try running with headless: false

### Issue: IIS server not found

**Symptoms:**
```
❌ IIS Login timeout or error
```

**Solutions:**
1. Verify IIS server URL in config.yaml
2. Check if you're on VPN/network
3. Test manually in browser first

### Debug Mode

1. **Run with visible browser:**
   ```yaml
   browser:
     headless: false
     slow_mo: 1000  # Very slow
   ```

2. **Check logs:**
   ```bash
   tail -20 logs/decisions.csv
   ```

---

## FAQ

### Q: Do I need to store my password?

**A:** No! The agent uses manual login. You login in the browser, and the agent uses the active session. Your credentials are never stored.

### Q: Can I run this on a server?

**A:** Yes, but you'll need:
- Display server (X11) or use headless mode
- Network access to ServiceNow and IIS
- Consider Docker for easier deployment

### Q: What happens if my session expires?

**A:** The agent will fail to fetch tickets. Stop the agent (Ctrl+C), restart it, and login again.

### Q: Can I approve tickets manually?

**A:** Yes, the agent logs both system and user decisions. Manual approvals show as "user" in the log.

### Q: How do I add CAD rules?

**A:** Edit `config.yaml` under `cad_rules`. See [Configuration](#configuration) section.

### Q: Can I customize the approval comment?

**A:** Yes, edit `modules/decision_engine.py`:
```python
def get_comment_for_approval(self, asset):
    return f"Custom comment: Asset {asset.get('asset_id')}"
```

### Q: What happens if the agent crashes?

**A:** Check `logs/decisions.csv` for the last successful operation. Restart the agent and login again.

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

*Last updated: September 11, 2026*
