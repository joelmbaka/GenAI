from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import os
import vercel_blob

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class BlobStorageToolInput(BaseModel):
    """Input schema for BlobStorageTool."""
    file_paths: List[str] = Field(
        ...,
        description="List of paths to the files to upload to Vercel Blob storage. Example: ['downloads\\B-2_Spirits_on_Deployment_to_Indo-Asia-Pacific.webp', 'downloads\\61767JbbT3L.webp']"
    )


class BlobStorageTool(BaseTool):
    name: str = "Vercel Blob Storage Tool"
    description: str = (
        "A tool that uploads files (particularly images) to Vercel Blob Storage and returns the public URIs of the uploaded files. This is useful for allowing public access to useful image resources using https. After an image is downloaded at the right dimensions, this tool pushes the image to Blob, making it accessible using Markdown. You will find the outputs of this tool used in the markdown 'content' field of a finalized article. "
    )
    args_schema: Type[BaseModel] = BlobStorageToolInput

    def _run(self, file_paths: List[str]) -> List[str]:
        """
        Upload multiple files from local disk to Vercel Blob using vercel_blob library
        
        Args:
            file_paths: List of paths to the local files
            
        Returns:
            List of URLs of the uploaded files or error messages if upload failed
        """
        results = []
        for file_path in file_paths:
            # Construct the full path
            full_path = os.path.join("E:\\journalist", file_path)
            
            # Verify the file exists
            if not os.path.exists(full_path):
                results.append(f"Error: File {full_path} does not exist")
                continue
            
            try:
                # Get the token from environment
                blob_token = os.environ.get("VERCEL_BLOB_TOKEN", "")
                if not blob_token:
                    results.append("Error: VERCEL_BLOB_TOKEN environment variable is not set")
                    continue
                
                # Set the token for vercel_blob library
                os.environ["BLOB_READ_WRITE_TOKEN"] = blob_token
                
                # Get the filename
                filename = os.path.basename(full_path)
                
                # Read the file content
                with open(full_path, 'rb') as f:
                    file_content = f.read()
                
                # Upload to Vercel Blob
                response = vercel_blob.put(filename, file_content)
                
                # Extract and return the URL
                blob_url = response.get("url")
                if blob_url:
                    results.append(f"File uploaded successfully to: {blob_url}")
                else:
                    results.append("Error: Upload succeeded but no URL was returned")
                
            except Exception as e:
                results.append(f"Error during upload: {str(e)}")
        
        return results 