#!/usr/bin/env python
import os
import re
import sys
from src.my_journalistic_crew.tools.tweet_screenshot_tool import TweetScreenshotTool
from src.my_journalistic_crew.tools.blob_storage_tool import BlobStorageTool

# Tweet ID to capture (from the example data)
TWEET_ID = "1910641857882644907"

# Replace with your actual Vercel Blob token
BLOB_READ_WRITE_TOKEN = os.environ.get("VERCEL_BLOB_TOKEN", "your_blob_token_here")

def main():
    # Check if we should upload to blob storage
    upload_to_blob = len(sys.argv) > 1 and sys.argv[1] == "--upload"
    
    print(f"Taking blog-sized screenshot of tweet ID: {TWEET_ID}")
    print(f"Window size: 1200x1500 (as configured in the tool)")
    
    # Step 1: Create and use the tweet screenshot tool
    screenshot_tool = TweetScreenshotTool()
    
    # Configure screenshot tool parameters
    screenshot_result = screenshot_tool._run(
        tweet_id=TWEET_ID,
        headless=True,  # Run browser in headless mode
        device_type="desktop",  # Use desktop view
        wait_time=15,  # Wait up to 15 seconds for tweet to load
        element_only=True,  # Capture just the tweet element
        use_pil_crop=True  # Use PIL to crop if needed
    )
    
    print(f"Screenshot tool result: {screenshot_result}")
    
    # Extract the file path from the result using regex
    # Expected format: "Screenshot captured and saved to z_output/tweet_XXXX_TIMESTAMP.png"
    file_path_match = re.search(r"saved to (z_output/tweet_[^\s]+\.png)", screenshot_result)
    
    if not file_path_match:
        print("Error: Could not extract screenshot path from result")
        return
    
    screenshot_path = file_path_match.group(1)
    print(f"Extracted screenshot path: {screenshot_path}")
    
    # Verify the screenshot file exists
    if not os.path.exists(screenshot_path):
        print(f"Error: Screenshot file {screenshot_path} not found")
        return
    
    print(f"\nBlog-sized screenshot saved to: {screenshot_path}")
    
    # Step 2: Upload the screenshot to Vercel Blob Storage (if requested)
    if upload_to_blob:
        print(f"Uploading screenshot to Vercel Blob Storage...")
        
        blob_tool = BlobStorageTool()
        upload_result = blob_tool._run(
            file_path=screenshot_path,
            blob_token=BLOB_READ_WRITE_TOKEN
        )
        
        print(f"Blob upload result: {upload_result}")
        
        # Extract the URL from the upload result
        blob_url_match = re.search(r"successfully to: (https://[^\s]+)", upload_result)
        
        if blob_url_match:
            blob_url = blob_url_match.group(1)
            print(f"\nSUCCESS! Tweet screenshot is available at:")
            print(f"{blob_url}")
        else:
            print("Failed to extract blob URL from the upload result")
    else:
        print("\nSkipping upload to Vercel Blob Storage (use --upload flag to enable)")

if __name__ == "__main__":
    main() 