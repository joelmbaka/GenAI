import os
import sys
import time
import base64
import requests
import io
from PIL import Image
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables
load_dotenv()

# Configuration for testing
TEST_IMAGE_URL = "https://cdn.radioafrica.digital/image/2025/04/9f82867e-e15f-47bc-970b-fe2434af7337.jpg"
API_KEY = os.getenv("NVIDIA_NIML_API_KEY")
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"

# Parameters to test
DIMENSIONS = [
    (400, 225),   # 16:9 small
    (800, 450),   # 16:9 medium (your min)
    (1200, 675),  # 16:9 large
    (400, 300),   # 4:3 small
    (800, 600),   # 4:3 medium  
    (1200, 900),  # 4:3 large
    (600, 600),   # 1:1 small
    (800, 800),   # 1:1 medium
    (1000, 1000), # 1:1 large
]

QUALITY_SETTINGS = [50, 70, 90]

def resize_image(img, width, height):
    """Resize image to specified dimensions"""
    return img.resize((width, height), Image.LANCZOS)

def get_image_base64(img, quality):
    """Convert image to base64 with specified quality"""
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=quality)
    return base64.b64encode(buffered.getvalue()).decode()

def analyze_image(image_b64):
    """Call the NVIDIA API and return results with token usage"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    
    payload = {
        "model": MODEL,
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
    
    start_time = time.time()
    response = requests.post(INVOKE_URL, headers=headers, json=payload)
    response_time = time.time() - start_time
    
    if response.status_code != 200:
        return {
            "success": False,
            "error": f"Error: {response.status_code} - {response.text}",
            "response_time": response_time
        }
    
    result = response.json()
    
    # Extract token usage
    prompt_tokens = result.get("usage", {}).get("prompt_tokens", 0)
    completion_tokens = result.get("usage", {}).get("completion_tokens", 0)
    total_tokens = result.get("usage", {}).get("total_tokens", 0)
    
    # Extract the first few words of the response for comparison
    content = ""
    if "choices" in result and len(result["choices"]) > 0:
        content = result["choices"][0]["message"]["content"]
        content_preview = " ".join(content.split()[:15]) + "..."
    
    return {
        "success": True,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens, 
        "total_tokens": total_tokens,
        "response_time": response_time,
        "content_preview": content_preview,
        "full_content": content
    }

def main():
    # Download the test image
    print(f"Downloading test image from {TEST_IMAGE_URL}")
    response = requests.get(TEST_IMAGE_URL)
    response.raise_for_status()
    original_img = Image.open(io.BytesIO(response.content))
    print(f"Original image dimensions: {original_img.size}")
    
    # Prepare results table
    results = []
    
    # Test each combination of dimensions and quality
    for width, height in DIMENSIONS:
        for quality in QUALITY_SETTINGS:
            print(f"Testing dimensions: {width}x{height}, quality: {quality}")
            
            # Resize image
            resized_img = resize_image(original_img, width, height)
            
            # Convert to base64
            image_b64 = get_image_base64(resized_img, quality)
            b64_size = len(image_b64)
            
            # Check if image is too large
            if b64_size > 180000:
                print(f"Image too large: {b64_size} bytes, skipping")
                results.append([
                    f"{width}x{height}",
                    quality,
                    b64_size,
                    "SKIPPED (too large)",
                    "-",
                    "-",
                    "-",
                    "-"
                ])
                continue
            
            # Analyze image
            result = analyze_image(image_b64)
            
            if result["success"]:
                results.append([
                    f"{width}x{height}",
                    quality,
                    b64_size,
                    result["prompt_tokens"],
                    result["completion_tokens"],
                    result["total_tokens"],
                    f"{result['response_time']:.2f}s",
                    result["content_preview"]
                ])
                
                # Save the full content to a file for comparison
                with open(f"result_{width}x{height}_q{quality}.txt", "w") as f:
                    f.write(result["full_content"])
            else:
                results.append([
                    f"{width}x{height}",
                    quality,
                    b64_size,
                    "ERROR",
                    "-",
                    "-",
                    result["response_time"],
                    result["error"]
                ])
    
    # Print results table
    print("\nResults:")
    headers = ["Dimensions", "Quality", "Base64 Size", "Prompt Tokens", "Completion Tokens", 
               "Total Tokens", "Response Time", "Content Preview"]
    print(tabulate(results, headers=headers, tablefmt="grid"))
    
    # Identify optimal settings
    valid_results = [r for r in results if r[3] != "ERROR" and r[3] != "SKIPPED (too large)"]
    if valid_results:
        # Sort by total tokens (lowest first)
        by_tokens = sorted(valid_results, key=lambda x: x[5])
        best_token_usage = by_tokens[0]
        
        # Sort by response time (fastest first)
        by_time = sorted(valid_results, key=lambda x: float(x[6][:-1]))
        fastest_response = by_time[0]
        
        print("\nMost Token-Efficient:")
        print(f"Dimensions: {best_token_usage[0]}, Quality: {best_token_usage[1]}")
        print(f"Base64 Size: {best_token_usage[2]} bytes")
        print(f"Total Tokens: {best_token_usage[5]}")
        
        print("\nFastest Response:")
        print(f"Dimensions: {fastest_response[0]}, Quality: {fastest_response[1]}")
        print(f"Base64 Size: {fastest_response[2]} bytes")
        print(f"Response Time: {fastest_response[6]}")

if __name__ == "__main__":
    main()