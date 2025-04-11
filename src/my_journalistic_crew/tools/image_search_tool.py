from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import json
import os
import requests

class ImageSearchToolInput(BaseModel):
    """Input schema for ImageSearchTool."""
    q: str = Field(..., description="The search query.")
    gl: Optional[str] = Field(
        default="us", 
        description="Country code for search results (e.g., 'US' for United States, 'KE' for Kenya, 'GB' for United Kingdom, etc)."
    )
    hl: Optional[str] = Field(
        default="en",
        description="Language code for search results (e.g., 'en' for English)."
    )
    autocorrect: Optional[bool] = Field(
        default=True,
        description="Whether to automatically correct search query spelling."
    )
    safe_search: Optional[bool] = Field(
        default=True, 
        description="Whether to filter explicit content."
    )
    page: Optional[int] = Field(
        default=1,
        description="Page number for pagination."
    )
    num: Optional[int] = Field(
        default=5,
        description="Number of image results to return."
    )

class ImageSearchTool(BaseTool):
    name: str = "Image Search"
    description: str = (
        "Searches for images related to a query using Google Images. "
        "Returns images with details including URLs, titles, and sources."
    )
    args_schema: Type[BaseModel] = ImageSearchToolInput

    def _run(self, q: str, gl: str = "us", hl: str = "en", 
             autocorrect: bool = True, safe_search: bool = True, 
             page: int = 1, num: int = 5) -> str:
        """Execute an image search and return the results."""
        # Get API key from environment
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return json.dumps({
                "status": "error",
                "message": "SERPER_API_KEY environment variable not set"
            })
        
        # Prepare API request
        url = "https://google.serper.dev/images"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': q,
            'gl': gl,
            'hl': hl,
            'autocorrect': autocorrect,
            'safe': safe_search,
            'page': page,
            'num': num
        }
        
        try:
            # Make API request
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()
            
            # Format the results
            results = {
                "searchParameters": {
                    "q": q,
                    "type": "images",
                    "engine": "google",
                    "num": num
                },
                "images": []
            }
            
            if 'images' in data:
                for i, item in enumerate(data['images'], 1):
                    image_data = {
                        "title": item.get('title', ''),
                        "imageUrl": item.get('imageUrl', ''),
                        "imageWidth": item.get('imageWidth', 0),
                        "imageHeight": item.get('imageHeight', 0),
                        "thumbnailUrl": item.get('thumbnailUrl', ''),
                        "thumbnailWidth": item.get('thumbnailWidth', 0),
                        "thumbnailHeight": item.get('thumbnailHeight', 0),
                        "source": item.get('source', '')
                    }
                    
                    results["images"].append(image_data)
            
            return json.dumps(results, indent=2)
            
        except requests.exceptions.RequestException as e:
            return json.dumps({
                "status": "error",
                "message": f"API request failed: {str(e)}"
            })
