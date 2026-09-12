"""
IIS Server Browser Automation Module
Handles asset search and CAD compliance checking - user logs in manually
"""

from playwright.sync_api import Page
from typing import Optional, Dict


class IISChecker:
    """Automates IIS server interactions for asset checking"""
    
    def __init__(self, config: dict):
        self.config = config
        self.base_url = config['iis']['base_url']
        self.page: Optional[Page] = None
    
    def set_page(self, page: Page):
        """Set the browser page to use"""
        self.page = page
    
    def open_iis_and_wait_for_login(self) -> bool:
        """
        Opens IIS server and waits for user to complete manual login
        Returns True when login is detected
        """
        try:
            # Navigate to IIS server
            print(f"\n🔑 Opening IIS Server: {self.base_url}")
            print("   👉 Please complete login in the browser window")
            self.page.goto(self.base_url)
            
            # Wait for user to complete login
            login_timeout = self.config.get('login', {}).get('login_timeout', 120000)
            
            print(f"   ⏳ Waiting for login (timeout: {login_timeout//1000}s)...")
            
            # Wait for dashboard/homepage elements
            self.page.wait_for_selector(
                '.dashboard, .main-content, #content, .home-page',
                timeout=login_timeout
            )
            
            # Additional wait to ensure page is fully loaded
            self.page.wait_for_load_state('networkidle')
            
            print("✅ IIS Login detected! Agent is now active.")
            return True
            
        except Exception as e:
            print(f"❌ IIS Login timeout or error: {e}")
            print("   Please ensure you completed login in the browser")
            return False
    
    def search_asset(self, asset_id: str) -> Optional[Dict]:
        """
        Search for asset in IIS server
        Returns asset details if found, None otherwise
        """
        try:
            # Navigate to asset search
            search_url = f"{self.base_url}{self.config['iis']['asset_search_path']}"
            self.page.goto(search_url)
            
            # Wait for search box
            self.page.wait_for_selector('input[type="search"], input[name="search"]', timeout=10000)
            
            # Enter asset ID
            self.page.fill('input[type="search"], input[name="search"]', asset_id)
            self.page.click('button[type="submit"], input[type="submit"]')
            
            # Wait for results
            self.page.wait_for_selector('.search-results, .asset-details', timeout=10000)
            
            # Extract asset details
            asset = {
                'asset_id': asset_id,
                'name': self._extract_text('.asset-name, .name'),
                'type': self._extract_text('.asset-type, .type'),
                'status': self._extract_text('.asset-status, .status'),
                'department': self._extract_text('.asset-department, .department'),
                'location': self._extract_text('.asset-location, .location'),
                'software_license': self._extract_text('.license, .software-license'),
                'version': self._extract_text('.version, .software-version'),
                'expiry_date': self._extract_text('.expiry, .license-expiry'),
                'compliance_status': self._extract_text('.compliance, .cad-status'),
                'raw_data': self.page.content()  # Full HTML for debugging
            }
            
            print(f"🔍 Found asset: {asset_id}")
            return asset
            
        except Exception as e:
            print(f"❌ Asset search failed: {e}")
            return None
    
    def _extract_text(self, selector: str) -> str:
        """Extract text from element using multiple possible selectors"""
        selectors = selector.split(', ')
        for sel in selectors:
            try:
                element = self.page.query_selector(sel.strip())
                if element:
                    return element.inner_text().strip()
            except:
                continue
        return ""
