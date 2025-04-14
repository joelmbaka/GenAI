from seleniumwire2 import webdriver
from seleniumwire2.utils import decode
import json
import os

# Ensure the storage directory exists
storage_dir = os.path.expanduser('~/.seleniumwire')
os.makedirs(storage_dir, exist_ok=True)

# Configure selenium-wire to use the custom storage directory
options = {
    'request_storage': 'disk',  # Specify the storage type
    'storage_dir': storage_dir  # Specify the storage directory
}

driver = webdriver.Chrome(seleniumwire_options=options)

def intercept(request):
    if request.url.startswith("https://encrypted-tbn0.gstatic.com/images?q="):
        # request.abort()
        request.create_response(
            status_code=200,
            headers={'Content-Type': 'image/jpeg'},
            body=open('download.jpg', 'rb').read()
        )

driver.request_interceptor = intercept

driver.get('https://www.google.com/search?q=mountain&tbm=isch')

# Wait for the requests to complete dynamically
for request in driver.requests:
    if request.response:
        if request.url.startswith("https://www.google.com/log?format=json"):
            response = request.response
            body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
            decoded_body = body.decode('utf-8')
            json_data = json.loads(decoded_body)
            
            # Save JSON data to a file
            with open('output.json', 'w') as f:
                json.dump(json_data, f, indent=4)
            print("Results saved to 'output.json'")

# Close the driver after scraping is done
driver.quit()