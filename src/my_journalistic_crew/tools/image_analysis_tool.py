from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import base64
import io
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImageAnalysisInput(BaseModel):
    """Input schema for ImageAnalysisTool."""
    image_url: str = Field(..., description="URL of the image to analyze.")

class ImageAnalysisTool(BaseTool):
    name: str = "Image Analysis Tool"
    description: str = (
        "Analyzes an image from a given URL and provides a detailed description of its contents."
    )
    args_schema: Type[BaseModel] = ImageAnalysisInput

    def _run(self, image_url: str) -> str:
        try:
            # Download the image from the URL
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Convert to base64
            image_data = response.content
            
            # Always resize image to 600x600
            img = Image.open(io.BytesIO(image_data))
            
            # Convert RGBA to RGB if necessary (handle transparent PNGs)
            if img.mode == 'RGBA':
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Paste the image with transparency on the background
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            elif img.mode != 'RGB':
                # Convert any other mode to RGB
                img = img.convert('RGB')
                
            img_resized = self._resize_image(img)
            buffered = io.BytesIO()
            img_resized.save(buffered, format="JPEG", quality=70)  # Using 70% quality
            image_b64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Call the NVIDIA API
            invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self._get_api_key()}",
                "Accept": "application/json"
            }
            
            payload = {
                "model": 'meta/llama-4-maverick-17b-128e-instruct',
                "messages": [
                    {
                        "role": "user",
                        "content": f'What is in this image? <img src="data:image/jpeg;base64,{image_b64}" />'
                    }
                ],
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.95,
                "stream": False
            }
            
            api_response = requests.post(invoke_url, headers=headers, json=payload)
            api_response.raise_for_status()
            result = api_response.json()
            
            # Extract the image description from the response
            if 'choices' in result and len(result['choices']) > 0:
                image_description = result['choices'][0]['message']['content']
                return image_description
            else:
                return "Failed to get a description from the API."
                
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def _get_api_key(self):
        # Try to get the API key from different environment variables
        import os
        
        # First try the NVIDIA_NIML_API_KEY (from .env)
        api_key = os.getenv("NVIDIA_NIML_API_KEY")
        if api_key:
            return api_key
            
        # Fall back to NVIDIA_API_KEY if the first one isn't available
        api_key = os.getenv("NVIDIA_API_KEY")
        if api_key:
            return api_key
            
        # Default placeholder if no key is found
        return "YOUR_API_KEY_REQUIRED_IF_EXECUTING_OUTSIDE_NGC"
    
    def _resize_image(self, img):
        """Resize image to 600x600 while preserving aspect ratio and cropping if necessary."""
        # Target size
        target_size = (600, 600)
        
        # Get original dimensions
        width, height = img.size
        
        # Determine which dimension to fit to the target
        if width > height:
            # Landscape orientation - fit to height first
            new_height = target_size[1]
            new_width = int(width * (new_height / height))
        else:
            # Portrait orientation - fit to width first
            new_width = target_size[0]
            new_height = int(height * (new_width / width))
        
        # Resize while maintaining aspect ratio
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Create a square image by cropping the center
        left = (new_width - target_size[0]) // 2
        top = (new_height - target_size[1]) // 2
        right = left + target_size[0]
        bottom = top + target_size[1]
        
        # If the image is smaller than target in one dimension, 
        # create a new blank image and paste the resized image centered
        if new_width < target_size[0] or new_height < target_size[1]:
            # Create new blank white image
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            
            # Calculate position to paste (center)
            paste_x = max(0, (target_size[0] - new_width) // 2)
            paste_y = max(0, (target_size[1] - new_height) // 2)
            
            # Paste resized image onto blank image
            new_img.paste(img_resized, (paste_x, paste_y))
            return new_img
        
        # Otherwise, crop to the target size
        return img_resized.crop((left, top, right, bottom))