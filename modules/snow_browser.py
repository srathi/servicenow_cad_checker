"""
ServiceNow Browser Automation Module
Handles SSO login and ticket management via Playwright
"""

import os
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
    
    def login_sso(self, username: str, password: str) -> bool:
        """
        Login to ServiceNow via SSO
        Note: SSO flow varies by organization
        This is a generic template - customize for your SSO
        """
        try:
            # Navigate to ServiceNow
            self.page.goto(self.instance_url)
            
            # Wait for SSO redirect (Microsoft ADFS/Azure AD)
            # This will vary based on your SSO provider
            self.page.wait_for_url("**/login**", timeout=10000)
            
            # Enter username
            self.page.fill('input[name="username"], input[id="username"]', username)
            self.page.click('button[type="submit"], input[type="submit"]')
            
            # Wait for password field
            self.page.wait_for_selector('input[name="password"], input[id="password"]', timeout=10000)
            self.page.fill('input[name="password"], input[id="password"]', password)
            self.page.click('button[type="submit"], input[type="submit"])
            
            # Handle MFA if present (placeholder)
            # self.page.wait_for_selector('#mfa-code', timeout=5000)
            # self.page.fill('#mfa-code', get_mfa_code())
            
            # Wait for ServiceNow homepage
            self.page.wait_for_selector('.navpage-main', timeout=30000)
            
            print("✅ SSO Login successful")
            return True
            
        except Exception as e:
            print(f"❌ SSO Login failed: {e}")
            return False
    
    def get_pending_approvals(self) -> List[Dict]:
        """Fetch pending approval tickets"""
        try:
            # Navigate to approvals
            approvals_url = f"{self.instance_url}{self.config['snow']['approvals_path']}"
            self.page.goto(approvals_url)
            
            # Wait for list to load
            self.page.wait_for_selector('.list_row', timeout=15000)
            
            # Extract tickets
            tickets = []
            rows = self.page.query_selector_all('.list_row')
            
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
