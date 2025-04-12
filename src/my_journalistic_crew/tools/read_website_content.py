from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from crewai_tools import ScrapeWebsiteTool
import gzip
import zlib
from bs4 import BeautifulSoup

class ScrapeWebsiteInput(BaseModel):
    """Input schema for URLScraper tool."""
    website_url: str = Field(..., description="The URL of the website to scrape content from.")

class ScrapeWebsite(BaseTool):
    name: str = "Web Scraper"
    description: str = (
        "Extracts and reads the content of a specified website. Useful for web scraping tasks and data collection."
    )
    args_schema: Type[BaseModel] = ScrapeWebsiteInput

    def _run(self, website_url: str) -> str:
        """Scrape content from the specified website URL."""
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
                    return "Binary content detected (e.g., images). Unable to process."
            except Exception as e:
                return f"Error decompressing content: {e}"
        else:
            # If it's already a string, assume it's uncompressed
            static_content = static_content
        
        # Check if content appears to be JavaScript-rendered
        if self._needs_js(static_content):
            # Fall back to Selenium for dynamic content
            from my_journalistic_crew.tools.utils.webdriver import WebDriverClient
            from my_journalistic_crew.tools.utils.pagenav import PageNavigator
            
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
        """
        # Limit output to 1000 words
        words = content.split()
        if len(words) > 1000:
            content = ' '.join(words[:1000])
        """
        return content
        
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