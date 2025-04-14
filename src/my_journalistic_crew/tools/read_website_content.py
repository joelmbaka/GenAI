from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from crewai_tools import ScrapeWebsiteTool
import gzip
import zlib
import requests

class ScrapeWebsiteInput(BaseModel):
    """Input schema for URLScraper tool."""
    website_urls: List[str] = Field(..., description="List of URLs of the websites to scrape content from.")

class ScrapeWebsite(BaseTool):
    name: str = "Web Scraper"
    description: str = (
        "Extracts and reads the content of specified websites. Useful for web scraping tasks and data collection."
    )
    args_schema: Type[BaseModel] = ScrapeWebsiteInput

    def _run(self, website_urls: List[str]) -> List[str]:
        """Scrape content from the specified website URLs."""
        results = []
        loaded_websites = []
        
        # Step 1: Load all websites first
        for website_url in website_urls:
            try:
                print(f"Checking URL: {website_url}")
                response = requests.get(website_url)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
                print(f"Loading website from URL: {website_url}")
                loaded_websites.append((website_url, response.content))
            except requests.exceptions.HTTPError as e:
                print(f"Failed to load website from {website_url}: {str(e)}")
            except Exception as e:
                print(f"Error loading website from {website_url}: {str(e)}")
        
        # Step 2: Scrape all successfully loaded websites
        for website_url, website_content in loaded_websites:
            try:
                # First try static scraping
                scraper = ScrapeWebsiteTool(website_url=website_url)
                static_content = scraper.run()
                
                # Check if content is binary or compressed
                if isinstance(static_content, bytes):
                    # Try to decompress if it's gzip or zlib
                    try:
                        if static_content.startswith(b'\x1f\x8b'):  # gzip magic number
                            static_content = gzip.decompress(static_content).decode('utf-8')
                        elif static_content.startswith(b'\x78\x9c'):  # zlib magic number
                            static_content = zlib.decompress(static_content).decode('utf-8')
                        else:
                            # Assume it's raw binary data (e.g., images)
                            results.append(f"Binary content detected (e.g., images). Unable to process: {website_url}")
                            continue
                    except Exception as e:
                        results.append(f"Error decompressing content from {website_url}: {e}")
                        continue
                else:
                    # If it's already a string, assume it's uncompressed
                    static_content = static_content
                
                # Check if content appears to be JavaScript-rendered
                if self._needs_js(static_content):
                    # Fall back to Selenium for dynamic content
                    from my_journalistic_crew.utils.webdriver import WebDriverClient
                    from my_journalistic_crew.utils.pagenav import PageNavigator
                    
                    driver_client = WebDriverClient(headless=True)
                    driver = driver_client.get_driver()
                    navigator = PageNavigator(driver)
                    
                    try:
                        navigator.go_to_url(website_url)
                        driver.implicitly_wait(10)
                        dynamic_content = driver.page_source
                        content = dynamic_content
                    finally:
                        driver_client.close()
                else:
                    content = static_content
                
                results.append(content)
            
            except Exception as e:
                results.append(f"Error scraping content from {website_url}: {e}")
        
        return results
        
    def _needs_js(self, content: str) -> bool:
        """Detect if content appears to be JavaScript-rendered."""
        # Common patterns in JS-rendered pages
        js_patterns = [
            '<div id="root"></div>',  # Common in React apps
            '<div id="app"></div>',   # Common in Vue apps
            '<noscript>',             # Common in JS-required pages
            'window.__INITIAL_STATE__',  # Common in JS frameworks
            'window.__NEXT_DATA__',      # Next.js specific
            'window.__NUXT__',           # Nuxt.js specific
            'ng-app',                    # Angular specific
        ]
        
        # If any of these patterns are found, assume JS is needed
        return any(pattern in content for pattern in js_patterns)