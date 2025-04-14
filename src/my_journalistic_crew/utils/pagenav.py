from my_journalistic_crew.utils.webdriver import WebDriverClient
from typing import Optional
import time
import random

class PageNavigator:
    """Utility class for page navigation"""
    
    def __init__(self, driver: WebDriverClient):
        self.driver = driver
    
    def go_to_url(self, url: str) -> bool:
        """Navigate to a URL with error handling"""
        try:
            self.driver.get(url)
            time.sleep(random.uniform(1, 3))  # Random delay
            return True
        except:
            return False
    
    def refresh_page(self) -> bool:
        """Refresh the current page"""
        try:
            self.driver.refresh()
            time.sleep(random.uniform(1, 3))  # Random delay
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
    
    def scroll_page(self, pixels: int) -> bool:
        """Scroll the page by a specified number of pixels"""
        try:
            self.driver.execute_script(f"window.scrollBy(0, {pixels});")
            time.sleep(random.uniform(1, 3))  # Random delay
            return True
        except:
            return False 