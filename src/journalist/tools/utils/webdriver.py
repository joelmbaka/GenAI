from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict, Optional
import random

class WebDriverClient:
    """Selenium WebDriver client with tablet emulation and detection avoidance"""
    
    def __init__(self, headless: bool = True, device_type: str = "desktop"):
        self.options = Options()
        
        # Define device configurations
        devices = {
            "desktop": {
                "size": "1920,1080",
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                ]
            },
            "tablet": {
                "size": "1024,768",
                "user_agents": [
                    "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (Linux; Android 13; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                ]
            }
        }
        
        # Get device configuration
        device_config = devices.get(device_type, devices["desktop"])
        
        # Basic anti-detection options
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        
        # Set device-specific configurations
        self.options.add_argument(f"--window-size={device_config['size']}")
        self.options.add_argument(f"user-agent={random.choice(device_config['user_agents'])}")
        
        # Add tablet-specific settings if tablet mode
        if device_type == "tablet":
            mobile_emulation = {
                "deviceMetrics": {
                    "width": 1024,
                    "height": 768,
                    "pixelRatio": 2.0,
                    "touch": True
                }
            }
            self.options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Remove webdriver flags
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        
        # Additional anti-detection measures
        self.options.add_argument("--disable-web-security")
        self.options.add_argument("--allow-running-insecure-content")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--disable-translate")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-default-apps")
        
        # Headless mode configuration
        if headless:
            self.options.add_argument("--headless=new")
            self.options.add_argument("--disable-software-rasterizer")
            self.options.add_argument("--remote-debugging-port=9222")
            self.options.add_argument("--disable-renderer-backgrounding")
        
        # Add this line to allow third-party cookies
        self.options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
        
        # Initialize driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        
        # Modify navigator properties
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                """
            }
        )
    
    def add_cookies(self, cookies: Dict[str, str], domain: str) -> None:
        """Add cookies to the current session"""
        for name, value in cookies.items():
            self.driver.add_cookie({
                'name': name,
                'value': value,
                'domain': domain
            })
    
    def get_driver(self):
        """Get the current driver instance"""
        return self.driver
    
    def close(self):
        """Close the driver"""
        self.driver.quit()
