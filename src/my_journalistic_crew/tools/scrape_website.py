from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
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
        "Extracts and reads the content of specified websites. Useful for web scraping tasks and data collection. Use this tool if you want to read more about an article published on the internet. It is not designed to read social media pages. Extracts 'text only' rendered inside HTML elements from static and javascript websites (except facebook, twitter etc). This tool is ineffective against 400s and 500s errors"
    )
    args_schema: Type[BaseModel] = ScrapeWebsiteInput

    def _run(self, website_urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape content from the specified website URLs."""
        results = []
        loaded_websites = []
        
        # Step 1: Load all websites first
        for website_url in website_urls:
            try:
                print(f"Checking URL: {website_url}")
                # Initial request
                response = requests.get(website_url, timeout=10)
                response.raise_for_status()
                
                if self._is_binary(response.content):
                    results.append({"url": website_url, "content": f"Skipped binary content at URL: {website_url}"})
                    continue
                
                print(f"Loading website from URL: {website_url}")
                loaded_websites.append((website_url, response.content))
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    results.append({"url": website_url, "content": f"403 error (forbidden) encountered for URL: {website_url}"})
                elif e.response.status_code == 404:
                    results.append({"url": website_url, "content": f"Website not found at URL: {website_url}"})
                elif e.response.status_code == 500:
                    results.append({"url": website_url, "content": f"Server error (500) encountered for URL: {website_url}"})
                else:
                    results.append({"url": website_url, "content": f"Failed to load website from {website_url}: {str(e)}"})
            except Exception as e:
                results.append({"url": website_url, "content": f"Error loading website from {website_url}: {str(e)}"})
        
        # Step 2: Scrape all successfully loaded websites
        for website_url, website_content in loaded_websites:
            try:
                # Standard static scraping
                scraper = ScrapeWebsiteTool(website_url=website_url)
                static_content = scraper.run()
                
                # Check if content is binary or compressed
                if isinstance(static_content, bytes):
                    try:
                        if static_content.startswith(b'\x1f\x8b'):  # gzip magic number
                            static_content = gzip.decompress(static_content).decode('utf-8')
                        elif static_content.startswith(b'\x78\x9c'):  # zlib magic number
                            static_content = zlib.decompress(static_content).decode('utf-8')
                        else:
                            results.append({"url": website_url, "content": f"Binary content detected (e.g., images). Unable to process: {website_url}"})
                            continue
                    except Exception as e:
                        results.append({"url": website_url, "content": f"Error decompressing content from {website_url}: {e}"})
                        continue
                
                # Check if content appears to be JavaScript-rendered
                if self._needs_js(static_content):
                    results.append({
                        "url": website_url,
                        "content": f"This page requires JavaScript rendering: {website_url}"
                    })
                else:
                    results.append({
                        "url": website_url,
                        "content": static_content
                    })
            
            except Exception as e:
                results.append({
                    "url": website_url, 
                    "content": f"Error scraping content from {website_url}: {e}"
                })
        
        return results        
    def _is_binary(self, content: bytes) -> bool:
        """Detect if content is binary."""
        # Common binary patterns
        binary_patterns = [
            b'\x00',  # Null byte
            b'\xff',  # Non-ASCII byte
            b'\x89PNG',  # PNG image
            b'\xff\xd8\xff',  # JPEG image
            b'GIF',  # GIF image
            b'%PDF',  # PDF document
        ]
        
        # If any of these patterns are found, assume content is binary
        return any(pattern in content for pattern in binary_patterns)
        
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
