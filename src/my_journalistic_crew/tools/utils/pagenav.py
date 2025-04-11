from my_journalistic_crew.tools.utils.webdriver import WebDriverClient
from typing import Optional

class PageNavigator:
    """Utility class for page navigation"""
    
    def __init__(self, driver: WebDriverClient):
        self.driver = driver
    
    def go_to_url(self, url: str) -> bool:
        """Navigate to a URL with error handling"""
        try:
            self.driver.get(url)
            return True
        except:
            return False
    
    def refresh_page(self) -> bool:
        """Refresh the current page"""
        try:
            self.driver.refresh()
            return True
        except:
            return False
    
    def get_current_url(self) -> Optional[str]:
        """Get the current URL"""
        try:
            return self.driver.current_url
        except:
            return None
    
    def wait_for_page_load(self, timeout: int = 10) -> bool:
        """Wait for page to fully load"""
        try:
            return self.driver.execute_script(
                "return document.readyState"
            ) == "complete"
        except:
            return False 