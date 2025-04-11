from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import mimetypes

# Import vercel_blob library
import vercel_blob

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class BlobStorageToolInput(BaseModel):
    """Input schema for BlobStorageTool."""
    file_path: str = Field(..., description="Path to the file to upload to Vercel Blob storage.")
    blob_token: str = Field(
        default=os.environ.get("VERCEL_BLOB_TOKEN", ""),
        description="Your Vercel Blob read-write token for authentication. If not provided, will use VERCEL_BLOB_TOKEN from environment."
    )


class BlobStorageTool(BaseTool):
    name: str = "Vercel Blob Storage Tool"
    description: str = (
        "A tool that uploads files (particularly images) to Vercel Blob Storage "
        "and returns the public URL of the uploaded file. This is useful for "
        "storing and sharing files like screenshots from other tools."
    )
    args_schema: Type[BaseModel] = BlobStorageToolInput

    def _run(self, file_path: str, blob_token: str = "") -> str:
        """
        Upload a file from local disk to Vercel Blob using vercel_blob library
        
        Args:
            file_path: Path to the local file
            blob_token: Your Vercel Blob read-write token (optional if set in environment)
            
        Returns:
            The URL of the uploaded file or error message if upload failed
        """
        # Verify the file exists
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist"
        
        try:
            # Use provided token or get from environment
            if not blob_token:
                blob_token = os.environ.get("VERCEL_BLOB_TOKEN", "")
            
            # Set the token for vercel_blob library
            os.environ["BLOB_READ_WRITE_TOKEN"] = blob_token
            
            # Get the filename
            filename = os.path.basename(file_path)
            
            # Read the file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to Vercel Blob
            response = vercel_blob.put(filename, file_content)
            
            # Extract and return the URL
            blob_url = response.get("url")
            if blob_url:
                return f"File uploaded successfully to: {blob_url}"
            else:
                return "Error: Upload succeeded but no URL was returned"
            
        except Exception as e:
            return f"Error during upload: {str(e)}" 