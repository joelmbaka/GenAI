from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
from PIL import Image
from io import BytesIO
import os


class DownloadImageInput(BaseModel):
    """Input schema for DownloadImage."""
    url: str = Field(..., description="URL of the image to download.")
    featured_image: bool = Field(False, description="Whether this is a featured image (1200x628) or regular image (800x600).")

class DownloadImageTool(BaseTool):
    name: str = "Download Image"
    description: str = (
        "Downloads an image from a URL and resizes it. "
        "Featured images are resized to 1200x628, regular images to 800x600. "
        "All images are saved in WebP format."
    )
    args_schema: Type[BaseModel] = DownloadImageInput

    def _run(self, url: str, featured_image: bool = False) -> str:
        try:
            # Download the image from URL
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Open the image with PIL
            img = Image.open(BytesIO(response.content))
            
            # Determine new size based on featured_image flag
            new_size = (1200, 628) if featured_image else (800, 600)
            
            # Resize the image
            resized_img = img.resize(new_size, Image.LANCZOS)
            
            # Generate filename from URL
            filename = url.split('/')[-1].split('?')[0]  # Handle query params
            base_name = os.path.splitext(filename)[0]
            
            # Create output directory if it doesn't exist
            os.makedirs('downloads', exist_ok=True)
            
            # Save the resized image in WebP format
            output_path = os.path.join('downloads', f"{base_name}_{'featured' if featured_image else 'regular'}.webp")
            resized_img.save(output_path, format="WebP", quality=90)
            
            return f"Image downloaded and resized to {new_size[0]}x{new_size[1]}. Saved to {output_path} in WebP format"
            
        except requests.RequestException as e:
            return f"Failed to download image: {str(e)}"
        except Exception as e:
            return f"Error processing image: {str(e)}"
