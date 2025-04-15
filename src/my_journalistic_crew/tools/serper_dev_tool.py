from crewai.tools import BaseTool
from typing import Type, Literal, Union
from pydantic import BaseModel, Field
import os
import requests
import json
from my_journalistic_crew.models.outputs import SerperWebSearchResults, GoogleImageResults, SerperGoogleNewsResults

class SerperDevToolInput(BaseModel):
    """Input schema for SerperDevTool."""
    query: str = Field(..., description="The search query.")
    country: str = Field(default="", description="The country code for the search (e.g., 'us' for United States).")
    location: str = Field(default="", description="The location for the search.")
    language: str = Field(default="en", description="The language for the search (e.g., 'en' for English).")
    date_range: str = Field(default="", description="The date range for the search (e.g., 'any_time').")
    autocorrect: bool = Field(default=True, description="Whether to use autocorrect for the search.")
    results_num: int = Field(default=10, description="The number of results to return.")
    page: int = Field(default=1, description="The page number of the results.")
    search_type: Literal["search", "images", "videos", "places", "maps", "reviews", "news", "shopping", "scholar", "patent", "autocomplete"] = Field(default="search", description="The type of search to perform.")
    tbs: str = Field(default="", description="Time-based search parameter (e.g., 'qdr:d' for the past day).")

class SerperDevTool(BaseTool):
    name: str = "Serper Dev Tool"
    description: str = (
        "A tool for performing searches using the Serper API. Supports various search types including search, images, videos, places, maps, reviews, news, shopping, image search (lens), scholar, patent, and autocomplete. Use this tool effectively to separate areas of concerns or intricacies or speculations or to fill in missing information. You have no bounds. The world of today knows no limits! But is backed by Truth! And the Truth Shall Set You Free."
    )
    args_schema: Type[BaseModel] = SerperDevToolInput

    def _run(self, query: str, country: str = "", location: str = "", language: str = "en", date_range: str = "", autocorrect: bool = True, results_num: int = 10, page: int = 1, search_type: str = "search", tbs: str = "") -> Union[SerperWebSearchResults, GoogleImageResults, SerperGoogleNewsResults]:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            raise ValueError("Serper API key not found in environment variables.")

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "gl": country,
            "hl": language,
            "num": results_num,
            "page": page,
            "type": search_type,
            "location": location,
            "tbs": tbs
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        search_results = response.json()

        if search_type == "images":
            return GoogleImageResults(**search_results)
        elif search_type == "news":
            return SerperGoogleNewsResults(**search_results)
        else:
            return SerperWebSearchResults(**search_results)
