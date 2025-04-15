from crewai.tools import BaseTool
from typing import Type, List, Dict, Optional
from pydantic import BaseModel, Field
import requests
from enum import Enum

class SearchType(str, Enum):
    WEB = "web"
    IMAGE = "image"

class GoogleCustomSearchToolInput(BaseModel):
    """Input schema for CustomSearchTool."""
    query: str = Field(..., description="The search query to be performed.")
    cx: str = Field(..., description="The Custom Search Engine ID.")
    api_key: str = Field(..., description="The API key for accessing the Custom Search API.")
    num: int = Field(default=10, description="Number of search results to return. Default is 10.")
    search_type: Optional[SearchType] = Field(default=None, description="Specifies the search type: 'image'. If unspecified, results are limited to webpages.")

class GoogleCustomSearchTool(BaseTool):
    name: str = "Google Custom Search Tool"
    description: str = (
        "Performs a search using the Google Custom Search JSON API and returns the results. Only used as fallback when serper api is unreachable."
    )
    args_schema: Type[BaseModel] = GoogleCustomSearchToolInput

    def _run(self, query: str, cx: str, api_key: str, num: int = 10, search_type: Optional[SearchType] = None) -> List[Dict[str, str]]:
        url = "https://customsearch.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "cx": cx,
            "key": api_key,
            "num": num
        }
        if search_type == SearchType.IMAGE:
            params["searchType"] = search_type.value
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json()
            formatted_results = []
            for item in results.get('items', []):
                formatted_results.append({
                    'title': item.get('title', 'N/A'),
                    'link': item.get('link', 'N/A'),
                    'snippet': item.get('snippet', 'N/A')
                })
            return formatted_results
        else:
            return [{'error': f"Error: {response.status_code} - {response.text}"}] 