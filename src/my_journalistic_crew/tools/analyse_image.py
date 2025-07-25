from crewai.tools import BaseTool
from typing import Type, Optional, List
from pydantic import BaseModel, Field
import requests
import base64
import io
import os
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImageAnalysisInput(BaseModel):
    """Input schema for ImageAnalysisTool."""
    image_urls: List[str] = Field(..., description="List of URLs of the images to analyze.")

class ImageAnalysisTool(BaseTool):
    name: str = "Image Analysis Tool"
    description: str = (
        "Analyzes images from given URLs in batches and provides detailed descriptions of their contents. Images are a cornerstone of My Blogposts therefore this tool performs a High Level Analysis of what is in the Visual of the Image. The description should be detailed reflecting whats in the image including and not limited to text, colors, animals, people, roads, utensils, and everything you can imagine of that is in the Image. The tool first validates if a URL is Valid, then Batch Processes the valid urls, then Processes them by first resizing them to get the optimal token usage, and returns a Detailed Description(D.D) using LLAMA 4 Maverick LLM."
    )
    args_schema: Type[BaseModel] = ImageAnalysisInput

    def _run(self, image_urls: List[str]) -> List[str]:
        try:
            # Step 1: Validate all URLs first
            valid_urls = []
            for image_url in image_urls:
                try:
                    print(f"Checking URL: {image_url}")
                    response = requests.get(image_url)
                    response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
                    valid_urls.append(image_url)
                except requests.exceptions.HTTPError as e:
                    print(f"Failed to load image from {image_url}: {str(e)}")
                except Exception as e:
                    print(f"Error loading image from {image_url}: {str(e)}")
            
            # Step 2: Batch process all valid URLs
            loaded_images = []
            for image_url in valid_urls:
                try:
                    print(f"Loading image from URL: {image_url}")
                    response = requests.get(image_url)
                    response.raise_for_status()
                    image_data = response.content
                    loaded_images.append((image_url, image_data))
                except Exception as e:
                    print(f"Error loading image from {image_url}: {str(e)}")
            
            # Step 3: Process all successfully loaded images
            descriptions = []
            for image_url, image_data in loaded_images:
                try:
                    description = self._process_image(image_data)
                    descriptions.append(description)
                except Exception as e:
                    print(f"Error processing image from {image_url}: {str(e)}")
                    descriptions.append(f"Error processing image: {str(e)}")
            
            return descriptions
                
        except Exception as e:
            return [f"Error analyzing images: {str(e)}"]
    
    def _process_image(self, image_data: bytes) -> str:
        """Process a single image and return its description."""
        try:
            # Attempt to open the image
            img = Image.open(io.BytesIO(image_data))
            
            # Check if the image is valid
            img.verify()  # Verify that the file is not truncated or corrupted
            
            # Reopen the image after verification
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
            
            # Check base64 size
            if len(image_b64) >= 180_000:
                print(f"Warning: Base64 image size is large ({len(image_b64)} bytes). Consider further reducing the image.")
            
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
            
            print("Sending request to NVIDIA API...")
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
            return f"Error processing image: {str(e)}"
    
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