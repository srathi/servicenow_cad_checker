"""
ServiceNow Browser Automation Module
Handles ticket management via Playwright - user logs in manually
"""

from playwright.sync_api import sync_playwright, Page, Browser
from typing import Optional, List, Dict


class SnowBrowser:
    """Automates ServiceNow browser interactions"""
    
    def __init__(self, config: dict):
        self.config = config
        self.instance_url = config['snow']['instance_url']
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def start(self, headless: bool = False):
        """Start browser instance"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            slow_mo=self.config['browser'].get('slow_mo', 100)
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.config['browser'].get('timeout', 30000))
    
    def stop(self):
        """Stop browser instance"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def open_snow_and_wait_for_login(self) -> bool:
        """
        Opens ServiceNow and waits for user to complete manual login
        Returns True when login is detected
        """
        try:
            # Navigate to ServiceNow
            print(f"\n🔑 Opening ServiceNow: {self.instance_url}")
            print("   👉 Please complete login in the browser window")
            self.page.goto(self.instance_url)
            
            # Wait for user to complete login
            # We detect login by waiting for the main dashboard/nav
            login_timeout = self.config.get('login', {}).get('login_timeout', 120000)
            
            print(f"   ⏳ Waiting for login (timeout: {login_timeout//1000}s)...")
            
            # Wait for ServiceNow homepage elements
            self.page.wait_for_selector(
                '.navpage-main, .nav-header, #sysverb_home, .page_loading',
                timeout=login_timeout
            )
            
            # Additional wait to ensure page is fully loaded
            self.page.wait_for_load_state('networkidle')
            
            print("✅ Login detected! Agent is now active.")
            return True
            
        except Exception as e:
            print(f"❌ Login timeout or error: {e}")
            print("   Please ensure you completed login in the browser")
            return False
    
    def get_pending_approvals(self) -> List[Dict]:
        """Fetch pending approval tickets"""
        try:
            # Navigate to approvals
            approvals_url = f"{self.instance_url}{self.config['snow']['approvals_path']}"
            self.page.goto(approvals_url)
            
            # Wait for list to load
            self.page.wait_for_selector('.list_row, .data_row', timeout=15000)
            
            # Extract tickets
            tickets = []
            rows = self.page.query_selector_all('.list_row, .data_row')
            
            for row in rows:
                ticket = {
                    'ticket_id': self._extract_text(row, '.list_cell:nth-child(2)'),
                    'requestor': self._extract_text(row, '.list_cell:nth-child(3)'),
                    'asset_id': self._extract_text(row, '.list_cell:nth-child(4)'),
                    'description': self._extract_text(row, '.list_cell:nth-child(5)'),
                    'state': self._extract_text(row, '.list_cell:nth-child(6)'),
                    'row_element': row  # Keep reference for actions
                }
                tickets.append(ticket)
            
            print(f"📋 Found {len(tickets)} pending approvals")
            return tickets
            
        except Exception as e:
            print(f"❌ Failed to fetch approvals: {e}")
            return []
    
    def approve_ticket(self, ticket: Dict, comment: str = "Approved - CAD compliant") -> bool:
        """Approve a ticket and add comment"""
        try:
            row = ticket['row_element']
            
            # Click approve button/link
            approve_btn = row.query_selector('button[title="Approve"], a[title="Approve"]')
            if approve_btn:
                approve_btn.click()
                
                # Wait for comment dialog
                self.page.wait_for_selector('#comment', timeout=5000)
                self.page.fill('#comment', comment)
                self.page.click('#approve_submit, button[type="submit"]')
                
                print(f"✅ Approved ticket: {ticket['ticket_id']}")
                return True
            
            print(f"❌ Approve button not found for: {ticket['ticket_id']}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to approve: {e}")
            return False
    
    def reject_ticket(self, ticket: Dict, reason: str) -> bool:
        """Reject a ticket with reason"""
        try:
            row = ticket['row_element']
            
            # Click reject button/link
            reject_btn = row.query_selector('button[title="Reject"], a[title="Reject"]')
            if reject_btn:
                reject_btn.click()
                
                # Wait for comment dialog
                self.page.wait_for_selector('#comment', timeout=5000)
                self.page.fill('#comment', reason)
                self.page.click('#reject_submit, button[type="submit"]')
                
                print(f"✅ Rejected ticket: {ticket['ticket_id']}")
                return True
            
            print(f"❌ Reject button not found for: {ticket['ticket_id']}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to reject: {e}")
            return False
    
    def _extract_text(self, parent, selector: str) -> str:
        """Extract text from element"""
        element = parent.query_selector(selector)
        return element.inner_text().strip() if element else ""
