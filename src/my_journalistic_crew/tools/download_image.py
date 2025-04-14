from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import requests
from PIL import Image
from io import BytesIO
import os


class DownloadImageInput(BaseModel):
    """Input schema for DownloadImage."""
    urls: List[str] = Field(..., description="List of URLs of the images to download.")

class DownloadImageTool(BaseTool):
    name: str = "Download Image"
    description: str = (
        "Downloads images from URLs and resizes them to 800x600. "
        "All images are saved in WebP format."
    )
    args_schema: Type[BaseModel] = DownloadImageInput

    def _run(self, urls: List[str]) -> List[str]:
        results = []
        for url in urls:
            try:
                # Download the image from URL
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                # Open the image with PIL
                img = Image.open(BytesIO(response.content))
                
                # Resize the image to 800x600
                new_size = (800, 600)
                resized_img = img.resize(new_size, Image.LANCZOS)
                
                # Generate filename from URL
                filename = url.split('/')[-1].split('?')[0]  # Handle query params
                base_name = os.path.splitext(filename)[0]
                
                # Create output directory if it doesn't exist
                os.makedirs('downloads', exist_ok=True)
                
                # Save the resized image in WebP format
                output_path = os.path.join('downloads', f"{base_name}.webp")
                resized_img.save(output_path, format="WebP", quality=90)
                
                results.append(f"Image downloaded and resized to {new_size[0]}x{new_size[1]}. Saved to {output_path} in WebP format")
                
            except requests.HTTPError as e:
                if e.response.status_code == 403:
                    results.append(f"Skipped URL due to 403 Forbidden error: {url}")
                else:
                    results.append(f"Failed to download image from {url}: {str(e)}")
            except Exception as e:
                results.append(f"Error processing image from {url}: {str(e)}")
        
        return results
