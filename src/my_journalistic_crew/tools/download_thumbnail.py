from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
from PIL import Image
from io import BytesIO
import os

class DownloadThumbnailInput(BaseModel):
    """Input schema for DownloadThumbnail."""
    url: str = Field(..., description="URL of the thumbnail image to download.")

class DownloadThumbnailTool(BaseTool):
    name: str = "Download Thumbnail"
    description: str = (
        "Downloads a single thumbnail image from a URL, resizes it to 300x168 pixels, optimal for mobile devices. A Thumbnail is important as it Increases the Chances of a user opening an article by 20%. The thumbnail is saved to Downloads folder and file starts with 'thumbnail_'."
    )
    args_schema: Type[BaseModel] = DownloadThumbnailInput

    def _run(self, url: str) -> str:
        try:
            # Download the image from URL
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Open the image with PIL
            img = Image.open(BytesIO(response.content))
            
            # Resize the image to 300x168
            new_size = (300, 168)
            resized_img = img.resize(new_size, Image.LANCZOS)
            
            # Generate filename from URL
            filename = url.split('/')[-1].split('?')[0]  # Handle query params
            base_name = os.path.splitext(filename)[0]
            
            # Create output directory if it doesn't exist
            os.makedirs('downloads', exist_ok=True)
            
            # Save the resized image in WebP format with 'thumbnail_' prefix
            output_path = os.path.join('downloads', f"thumbnail_{base_name}.webp")
            resized_img.save(output_path, format="WebP", quality=90)
            
            return f"Thumbnail downloaded and resized to {new_size[0]}x{new_size[1]}. Saved to {output_path} in WebP format"
            
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                return f"Skipped URL due to 403 Forbidden error: {url}"
            else:
                return f"Failed to download thumbnail from {url}: {str(e)}"
        except Exception as e:
            return f"Error processing thumbnail from {url}: {str(e)}" 