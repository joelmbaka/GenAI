from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field

class SerperDevToolInput(BaseModel):
    """Input schema for SerperDevTool."""
    q: str = Field(..., description="The search query.")
    type: Optional[str] = Field(
        default="search",
        description="Type of search. Options: 'search', 'images', 'videos', 'places', 'maps', 'reviews', 'news', 'shopping', 'lens', 'scholar', 'patents'"
    )
    gl: Optional[str] = Field(
        default=None,
        description="Country code for search results (e.g., 'US' for United States)."
    )
    location: Optional[str] = Field(
        default=None,
        description="Location for search results. Can be any city, region, or country."
    )
    hl: Optional[str] = Field(
        default=None,
        description="Language code for search results (e.g., 'en' for English)."
    )
    tbs: Optional[str] = Field(
        default=None,
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
    name: str = "Serper Dev Search"
    description: str = (
        "Performs semantic search across the internet using serper.dev API. "
        "Returns the most relevant search results based on the query."
    )
    args_schema: Type[BaseModel] = SerperDevToolInput

    def _run(self, q: str, type: str = "search", gl: str = None, location: str = None,
             hl: str = None, tbs: str = None, num: int = 10, autocorrect: bool = True) -> str:
        """Execute a search using the serper.dev API."""
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
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': q,
            'type': type,
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
            
            # Format results in consistent JSON structure
            results = {
                "status": "success",
                "query": q,
                "results": []
            }
            
            # Handle image search results
            if type == "images" and 'images' in data:
                for item in data['images']:
                    results["results"].append({
                        "type": "image",
                        "title": item.get('title', ''),
                        "imageUrl": item.get('imageUrl', ''),
                        "thumbnailUrl": item.get('thumbnailUrl', ''),
                        "source": item.get('source', ''),
                        "domain": item.get('domain', ''),
                        "link": item.get('link', ''),
                        "width": item.get('imageWidth', 0),
                        "height": item.get('imageHeight', 0)
                    })
            # Handle news search results
            elif type == "news" and 'news' in data:
                for item in data['news']:
                    results["results"].append({
                        "type": "news",
                        "title": item.get('title', ''),
                        "link": item.get('link', ''),
                        "snippet": item.get('snippet', ''),
                        "source": item.get('source', ''),
                        "date": item.get('date', ''),
                        "imageUrl": item.get('imageUrl', '')
                    })
            # Handle regular search results
            elif 'organic' in data:
                for item in data['organic']:
                    result = {
                        "type": "organic",
                        "title": item.get('title', ''),
                        "link": item.get('link', ''),
                        "snippet": item.get('snippet', ''),
                        "date": item.get('date', '')
                    }
                    # Handle sitelinks if present
                    if 'sitelinks' in item:
                        result['sitelinks'] = [
                            {
                                "title": sl.get('title', ''),
                                "link": sl.get('link', '')
                            } for sl in item['sitelinks']
                        ]
                    results["results"].append(result)
            
            # Add top stories if present
            if 'topStories' in data:
                for story in data['topStories']:
                    results["results"].append({
                        "type": "top_story",
                        "title": story.get('title', ''),
                        "source": story.get('source', ''),
                        "link": story.get('link', ''),
                        "date": story.get('date', ''),
                        "imageUrl": story.get('imageUrl', '')
                    })
            
            # Add people also ask if present
            if 'peopleAlsoAsk' in data:
                for question in data['peopleAlsoAsk']:
                    results["results"].append({
                        "type": "question",
                        "question": question.get('question', ''),
                        "answer": question.get('snippet', ''),
                        "source": question.get('link', '')
                    })
            
            # Add related searches if present
            if 'relatedSearches' in data:
                results["related_searches"] = [
                    {"query": rs.get('query', '')} for rs in data['relatedSearches']
                ]
            
            return json.dumps(results)
            
        except requests.exceptions.RequestException as e:
            return json.dumps({
                "status": "error",
                "message": f"API request failed: {str(e)}"
            })
