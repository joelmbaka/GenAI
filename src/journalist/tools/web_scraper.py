from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from crewai_tools import ScrapeWebsiteTool

class WebScraperInput(BaseModel):
    """Input schema for URLScraper tool."""
    website_url: str = Field(..., description="The URL of the website to scrape content from.")

class WebScraper(BaseTool):
    name: str = "Web Scraper"
    description: str = (
        "Extracts and reads the content of a specified website. Useful for web scraping tasks and data collection."
    )
    args_schema: Type[BaseModel] = WebScraperInput

    def _run(self, website_url: str) -> str:
        """Scrape content from the specified website URL."""
        scraper = ScrapeWebsiteTool(website_url=website_url)
        return scraper.run()
