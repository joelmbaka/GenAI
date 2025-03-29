from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from pygooglenews import GoogleNews

class GoogleNewsToolInput(BaseModel):
    """Input schema for GoogleNewsTool."""
    query: str = Field(..., description="Search query for Google News")
    lang: Optional[str] = Field('en', description="Language for the search results")
    country: Optional[str] = Field('US', description="Country for the search results")
    when: Optional[str] = Field(None, description="Time period for the search (e.g., '1h', '1d', '1w', '1m', '1y')")
    from_date: Optional[str] = Field(None, description="Start date for search in YYYY-MM-DD format")
    to_date: Optional[str] = Field(None, description="End date for search in YYYY-MM-DD format")

class GoogleNewsTool(BaseTool):
    name: str = "Google News Search Tool"
    description: str = (
        "Searches Google News for articles based on given parameters. "
        "Can filter by language, country, time period, and date range."
    )
    args_schema: Type[BaseModel] = GoogleNewsToolInput

    def _run(self, query: str, lang: str = 'en', country: str = 'US', when: str = None,
             from_date: str = None, to_date: str = None) -> str:
        gn = GoogleNews(lang=lang, country=country)
        
        # Build the search query with optional parameters
        search_query = query
        if when:
            search_query += f" when:{when}"
        if from_date and to_date:
            search_query += f" after:{from_date} before:{to_date}"
        elif from_date:
            search_query += f" after:{from_date}"
        elif to_date:
            search_query += f" before:{to_date}"
        
        # Perform the search
        results = gn.search(search_query)
        return str(results)
