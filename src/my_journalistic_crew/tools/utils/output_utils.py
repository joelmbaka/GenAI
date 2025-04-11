import json
from datetime import datetime

def format_error_response(error_message="", filename=""):
    """
    Format an error response as a JSON string
    
    Args:
        error_message: Optional error message
        filename: Optional filename where error details were saved
        
    Returns:
        str: JSON string with error status
    """
    response = {
        'status': 'error',
        'tweets': []
    }
    
    if error_message:
        response['error'] = error_message
    
    if filename:
        response['filename'] = filename
    
    return json.dumps(response)

def format_cookies_error(error):
    """
    Format an error response for cookie loading failure
    
    Args:
        error: The exception that occurred
        
    Returns:
        str: JSON string with error details
    """
    filename = f"error_cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return format_error_response(
        error_message=f"Error loading cookies: {str(error)}", 
        filename=filename
    )

def format_empty_response():
    """
    Format a response for when no tweets were found
    
    Returns:
        str: JSON string with empty tweets list
    """
    return json.dumps({
        'tweets': []
    }) 