from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from crewai_tools import ScrapeWebsiteTool

class URLScraperInput(BaseModel):
    """Input schema for URLScraper tool."""
    website_url: str = Field(..., description="The URL of the website to scrape content from.")

class URLScraper(BaseTool):
    name: str = "URL Scraper"
    description: str = (
        "Extracts and reads the content of a specified website. Useful for web scraping tasks and data collection."
    )
    args_schema: Type[BaseModel] = URLScraperInput

    def _run(self, website_url: str) -> str:
        """Scrape content from the specified website URL."""
        scraper = ScrapeWebsiteTool(website_url=website_url)
        return scraper.run()
