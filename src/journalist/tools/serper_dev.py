from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field

class SerperDevToolInput(BaseModel):
    """Input schema for SerperDevTool."""
    q: str = Field(..., description="The search query.")
    type: Optional[str] = Field(
        default="search",
        description="Type of search. Options: 'news', 'search', 'images'"
    )
    gl: Optional[str] = Field(
        default="KE",
        description="Country code for search results (e.g., 'US' for United States, 'KE' for Kenya)."
    )
    location: Optional[str] = Field(
        default=None,
        description="Location for search results. Can be any city, region, or country."
    )
    hl: Optional[str] = Field(
        default="en",
        description="Language code for search results (e.g., 'en' for English)."
    )
    tbs: Optional[str] = Field(
        default="qdr:d",
        description="Date range for search results. Options: 'qdr:h' (past hour), 'qdr:d' (past 24h), 'qdr:w' (past week), 'qdr:m' (past month), 'qdr:y' (past year)"
    )
    num: Optional[int] = Field(
        default=10,
        description="Number of search results to return."
    )
    autocorrect: Optional[bool] = Field(
        default=True,
        description="Whether to automatically correct search query spelling."
    )

class SerperDevTool(BaseTool):
    name: str = "Google Search"
    description: str = (
        "Performs semantic search across the internet using Google Serper Dev API. "
        "Returns the most relevant search results based on the query."
    )
    args_schema: Type[BaseModel] = SerperDevToolInput

    def _is_valid_image_url(self, url: str) -> bool:
        """Check if an image URL is valid."""
        if not url or not url.startswith('http'):
            return False
        # Add more validation if needed (e.g., check domain, path, etc.)
        return True

    def _run(self, q: str, type: str = "search", gl: str = None, location: str = None,
             hl: str = None, tbs: str = None, num: int = 10, autocorrect: bool = True) -> str:
        """Execute a news search using the serper.dev API."""
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
        
        # Prepare API request - force type to 'news'
        url = "https://google.serper.dev/news"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': q,
            'type': 'news',
            'gl': gl,
            'hl': hl,
            'tbs': tbs,
            'num': num,
            'autocorrect': autocorrect
        }
        
        try:
            # Make API request
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            
            results = {
                "query": q,
                "type": "news",
                "results": []
            }
            
            # Only process news results
            if 'news' in data:
                for item in data['news']:
                    results["results"].append({
                        "title": item.get('title', ''),
                        "url": item.get('link', ''),
                        "summary": item.get('snippet', ''),
                        "date": item.get('date', ''),
                        "source": item.get('source', ''),
                        "imageUrl": item.get('imageUrl', '')
                    })
            
            return json.dumps(results)
            
        except requests.exceptions.RequestException as e:
            return json.dumps({
                "status": "error",
                "message": f"API request failed: {str(e)}"
            })
