from datetime import datetime
from dateutil import parser
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from pygooglenews import GoogleNews

class SearchGoogleNewsByTopicInput(BaseModel):
    """Input schema for tool."""
    topic_id: str = Field(..., description="The topic ID to find relevant news articles.")
    language: str = Field(default="en", description="The language code for the news articles (e.g., 'en' for English).")
    country: str = Field(default="KE", description="The country code for the news articles (e.g., 'US' for United States).")
    when: str = Field(default=None, description="Filter articles published within a specific time frame (e.g., '2h', '3d', '1m', '2w').")

class SearchGoogleNewsByTopicTool(BaseTool):
    name: str = "SearchGoogleNewsByTopic"
    description: str = "A tool to search for news articles using the Google News RSS feed based on a topic ID, language, country, and time frame. fetch news articles by category aka Topic ID e.g AI articles, Fitness articles, Business etc. using topic ID. Each request returns a maximum of 100 results."
    args_schema: Type[BaseModel] = SearchGoogleNewsByTopicInput

    def _run(self, topic_id: str, language: str = "en", country: str = "US", when: str = None) -> list:
        gn = GoogleNews(lang=language, country=country)
        topic_results = gn.topic_headlines(topic_id)
        articles = topic_results['entries']
        
        # Sort articles by publication date in descending order (most recent first)
        sorted_articles = sorted(articles, key=lambda x: parser.parse(x['published']), reverse=True)
        
        # Get the current time with the same timezone as published_date
        if sorted_articles:
            published_date = parser.parse(sorted_articles[0]['published'])
            now = datetime.now(published_date.tzinfo)
        else:
            now = datetime.now()
        
        # Parse the 'when' parameter into seconds
        time_filter_seconds = self._parse_when_to_seconds(when) if when else None
        
        # Format the results as a list of dictionaries, converting published to "ago" format
        formatted_results = []
        for article in sorted_articles:
            published_date = parser.parse(article['published'])
            time_difference = now - published_date
            
            # Filter articles based on the time_filter_seconds parameter
            if time_filter_seconds is None or time_difference.total_seconds() <= time_filter_seconds:
                ago_format = self._format_time_difference(time_difference)
                
                formatted_results.append({
                    "title": article['title'],
                    "link": article['link'],
                    "published": ago_format
                })
        
        return formatted_results

    def _parse_when_to_seconds(self, when: str) -> int:
        """Convert a human-readable time frame (e.g., '2h', '3d', '1m', '2w') into seconds."""
        if not when:
            return None
        
        if when[-1] == 'd':
            return int(when[:-1]) * 86400  # days to seconds
        elif when[-1] == 'h':
            return int(when[:-1]) * 3600  # hours to seconds
        elif when[-1] == 'm':
            return int(when[:-1]) * 2592000  # months to seconds (assuming 30 days per month)
        elif when[-1] == 'w':
            return int(when[:-1]) * 604800  # weeks to seconds
        else:
            raise ValueError("Invalid 'when' format. Use formats like '2h', '3d', '1m', or '2w'.")

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