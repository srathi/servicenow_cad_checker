"""
ServiceNow Ticket Approval Agent
Main orchestrator script - User logs in manually, agent takes over
"""

import time
import yaml
from pathlib import Path

from modules.snow_browser import SnowBrowser
from modules.iis_checker import IISChecker
from modules.decision_engine import DecisionEngine
from modules.logger import DecisionLogger
from modules.cad_validator import CADValidator


def load_config() -> dict:
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def process_ticket(
    ticket: dict,
    iis_checker: IISChecker,
    decision_engine: DecisionEngine,
    snow_browser: SnowBrowser
) -> bool:
    """Process a single ticket"""
    start_time = time.time()
    
    try:
        # Step 1: Extract ticket details
        ticket_id = ticket.get('ticket_id', 'UNKNOWN')
        asset_id = ticket.get('asset_id', 'UNKNOWN')
        
        print(f"\n🔄 Processing ticket: {ticket_id}")
        print(f"   Asset: {asset_id}")
        
        # Step 2: Search asset in IIS server
        asset = iis_checker.search_asset(asset_id)
        
        if not asset:
            print(f"   ⚠️  Asset not found in IIS: {asset_id}")
            # Log as rejected
            decision_engine.logger.log_decision(
                ticket_id=ticket_id,
                requestor=ticket.get('requestor', 'UNKNOWN'),
                asset_id=asset_id,
                decision="REJECTED",
                reason="Asset not found in IIS server",
                system_or_user="system",
                execution_time=time.time() - start_time
            )
            return False
        
        # Step 3: Make decision
        decision, reason = decision_engine.make_decision(ticket, asset)
        
        # Step 4: Execute decision
        if decision == "APPROVED":
            comment = decision_engine.get_comment_for_approval(asset)
            success = snow_browser.approve_ticket(ticket, comment)
        else:
            reason_text = decision_engine.get_reason_for_rejection(asset, reason)
            success = snow_browser.reject_ticket(ticket, reason_text)
        
        # Step 5: Log execution time
        execution_time = time.time() - start_time
        print(f"   ✅ Completed in {execution_time:.1f}s - Decision: {decision}")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Error processing ticket: {e}")
        return False


def run_agent():
    """Main agent loop"""
    print("=" * 60)
    print("🚀 ServiceNow Ticket Approval Agent")
    print("=" * 60)
    print("\n📌 Agent will open browser windows.")
    print("   Please complete login manually when prompted.")
    print("   Agent will take over after login is detected.\n")
    
    # Load configuration
    config = load_config()
    
    # Initialize logger
    logger = DecisionLogger(
        log_dir=config['logging']['log_dir'],
        log_file=config['logging']['log_file']
    )
    
    # Print CAD rule summary
    print(f"📋 CAD Validation: {CADValidator(config).get_rule_summary()}")
    
    # Initialize browser modules
    snow_browser = SnowBrowser(config)
    iis_checker = IISChecker(config)
    decision_engine = DecisionEngine(config, logger)
    
    try:
        # Start browser
        print("\n🌐 Starting browser...")
        snow_browser.start(headless=config['browser'].get('headless', False))
        
        # Open ServiceNow and wait for manual login
        print("\n🔑 Step 1: Login to ServiceNow")
        if not snow_browser.open_snow_and_wait_for_login():
            print("❌ Failed to detect ServiceNow login. Exiting.")
            return
        
        # Share browser page with IIS checker
        iis_checker.set_page(snow_browser.page)
        
        # Open IIS server and wait for manual login
        print("\n🔑 Step 2: Login to IIS Server")
        if not iis_checker.open_iis_and_wait_for_login():
            print("❌ Failed to detect IIS login. Exiting.")
            return
        
        # Main loop
        check_interval = config['schedule']['interval_minutes'] * 60
        max_runs = config['schedule']['max_runs_per_day']
        run_count = 0
        
        print("\n" + "=" * 60)
        print("✅ Agent is now ACTIVE and monitoring tickets")
        print("=" * 60)
        
        while run_count < max_runs:
            print(f"\n{'='*60}")
            print(f"📋 Check #{run_count + 1} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print('='*60)
            
            # Fetch pending approvals
            tickets = snow_browser.get_pending_approvals()
            
            if not tickets:
                print("   No pending tickets found")
            else:
                # Process each ticket
                for ticket in tickets:
                    process_ticket(ticket, iis_checker, decision_engine, snow_browser)
            
            run_count += 1
            
            # Print stats
            stats = logger.get_stats()
            print(f"\n📊 Stats: {stats['total']} total | {stats['approved']} approved | {stats['rejected']} rejected")
            
            # Wait for next check
            if run_count < max_runs:
                print(f"\n⏰ Waiting {config['schedule']['interval_minutes']} minutes until next check...")
                time.sleep(check_interval)
        
        print("\n✅ Agent completed daily run limit")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Agent stopped by user")
    except Exception as e:
        print(f"\n❌ Agent error: {e}")
    finally:
        print("\n🔒 Closing browser...")
        snow_browser.stop()
        print("👋 Goodbye!")


if __name__ == "__main__":
    run_agent()
