from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field

class NewsSearchToolInput(BaseModel):
    """Input schema for NewsSearchTool."""
    q: str = Field(..., description="The search query for finding news articles.")
    gl: Optional[str] = Field(
        default=None,
        description="Country code for news results (e.g., 'US' for United States, 'KE' for Kenya, 'GB' for United Kingdom, etc)."
    )
    location: Optional[str] = Field(
        default=None,
        description="Location for news results. Can be any city, region, or country."
    )
    hl: Optional[str] = Field(
        default=None,
        description="Language code for news results (e.g., 'en' for English)."
    )
    tbs: Optional[str] = Field(
        default=None,
        description="Date range for news results. Options: 'qdr:h' (past hour), 'qdr:d' (past 24h), 'qdr:w' (past week), 'qdr:m' (past month), 'qdr:y' (past year)"
    )
    num: Optional[int] = Field(
        default=10,
        description="Number of news results to return (1-10)."
    )
    autocorrect: Optional[bool] = Field(
        default=True,
        description="Whether to automatically correct search query spelling."
    )

class NewsSearchTool(BaseTool):
    name: str = "Google News Search"
    description: str = (
        "Searches for recent news articles using Google News. "
        "Returns relevant news articles with titles, sources, summaries, "
        "dates, and links. Useful for finding current events, "
        "recent developments, and media coverage on specific topics."
    )
    args_schema: Type[BaseModel] = NewsSearchToolInput

    def _run(self, q: str, gl: Optional[str] = None, location: Optional[str] = None,
             hl: Optional[str] = None, tbs: Optional[str] = None, 
             num: Optional[int] = 10, autocorrect: Optional[bool] = True) -> str:
        """Execute a news search using the Google News API via Serper."""
        import os
        import requests
        import json
        
        # Get API key from environment
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return json.dumps({
                "status": "error",
                "message": "SERPER_API_KEY environment variable not set"
            })
        
        # Prepare API request
        url = "https://google.serper.dev/news"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        # Build payload with only the required query and defaults for optional params
        payload = {
            'q': q,
        }
        
        # Add optional parameters only if they're not None
        if num is not None:
            payload['num'] = min(max(1, num), 100)  # Ensure num is between 1 and 100
        if gl is not None:
            payload['gl'] = gl
        if hl is not None:
            payload['hl'] = hl
        if tbs is not None:
            payload['tbs'] = tbs
        if location is not None:
            payload['location'] = location
        if autocorrect is not None:
            payload['autocorrect'] = autocorrect
        
        try:
            # Make API request
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            api_data = response.json()
            
            # Format results to match expected structure
            results = {
                "searchParameters": {
                    "q": q,
                    "type": "news",
                    "engine": "google"
                },
                "news": []
            }
            
            if 'news' in api_data:
                for i, item in enumerate(api_data['news'], 1):
                    news_item = {
                        "title": item.get('title', ''),
                        "link": item.get('link', ''),
                        "snippet": item.get('snippet', ''),
                        "date": item.get('date', ''),
                        "source": item.get('source', ''),
                        "position": i
                    }
                    
                    results["news"].append(news_item)
                    
            return json.dumps(results, indent=2)
            
        except requests.exceptions.RequestException as e:
            return json.dumps({
                "status": "error",
                "message": f"News API request failed: {str(e)}"
            })
