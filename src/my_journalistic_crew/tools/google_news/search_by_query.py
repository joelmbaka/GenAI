from datetime import datetime
from dateutil import parser
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from pygooglenews import GoogleNews

class SearchGoogleNewsByQueryInput(BaseModel):
    """Input schema for tool."""
    query: str = Field(..., description="The search query to find relevant news articles. Supports special query terms like Boolean OR (e.g., 'boeing OR airbus'), Exclude Query Term (e.g., 'boeing -airbus'), Include Query Term (e.g., 'boeing +airbus'), Phrase Search (e.g., '\"New York metro opening\"'), allintext, intitle, allintitle, inurl, allinurl.")
    when: str = Field(None, description="Time range for the published datetime. Valid formats include:\n"
                                      "- 'h' for hours (e.g., '12h' for articles published in the last 12 hours, works up to 101h).\n"
                                      "- 'd' for days (e.g., '7d' for articles published in the last 7 days).\n"
                                      "- 'm' for months (e.g., '6m' for articles published in the last 6 months, works up to 48m).\n"
                                      "Note: Incorrect inputs will not result in an error; the 'when' parameter will be ignored by Google.")
    helper: bool = Field(True, description="Whether to use URL-escaping for the query. Defaults to True.")

class SearchGoogleNewsByQueryTool(BaseTool):
    name: str = "SearchGoogleNewsByQuery"
    description: str = "A tool to search for news articles using the Google News RSS feed based on a query. Supports special query terms like Boolean OR, Exclude Query Term, Include Query Term, Phrase Search, allintext, intitle, allintitle, inurl, allinurl."
    args_schema: Type[BaseModel] = SearchGoogleNewsByQueryInput

    def _run(self, query: str, when: str = None, helper: bool = True) -> list:
        gn = GoogleNews()
        search_results = gn.search(query, when=when, helper=helper)
        articles = search_results['entries']
        
        # Format the results as a list of dictionaries, converting published to "ago" format
        formatted_results = []
        for article in articles:
            published_date = parser.parse(article['published'])
            time_difference = datetime.now(published_date.tzinfo) - published_date
            ago_format = self._format_time_difference(time_difference)
            
            formatted_results.append({
                "title": article['title'],
                "link": article['link'],
                "published": ago_format
            })
        
        return formatted_results

    def _format_time_difference(self, time_difference):
        """Convert a timedelta to a human-readable 'ago' format."""
        seconds = int(time_difference.total_seconds())
        if seconds < 60:
            return f"{seconds} seconds ago"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = seconds // 86400
            return f"{days} day{'s' if days > 1 else ''} ago"