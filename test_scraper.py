import json
import os
import time
from src.my_journalistic_crew.tools.scrape_website import ScrapeWebsite
from src.my_journalistic_crew.models.outputs import WebScrapeResults

# Define the specific URL to test-fallout
# "
# Initialize the scraper
specific_url = "https://nation.africa/kenya/counties/kiambu/senator-wamatangi-tells-governors-in-corruption-list-to-clear-their-names-1082620"
scraper = ScrapeWebsite()

# Time the scraping process
start_time = time.time()

# Run the scraper with the specific URL
results = scraper._run([specific_url])  # Pass the URL as a list

# Calculate total time
end_time = time.time()
total_time = end_time - start_time
avg_time_per_url = total_time / 1  # Since we are testing only one URL

# Calculate success rate
successful = sum(1 for r in results if not r["content"].startswith("Error") and 
                                     not r["content"].startswith("Skipped") and
                                     not r["content"].startswith("Failed") and
                                     not r["content"].startswith("Website not found") and
                                     not r["content"].startswith("Server error"))
success_rate = (successful / 1) * 100  # Since we are testing only one URL

# Create a WebScrapeResults object
scrape_results = {
    "websites": [
        {
            "url": r["url"],
            "content": r["content"][:5000] + "..." if len(r["content"]) > 5000 else r["content"]  # Truncate content for readability
        } for r in results
    ],
    "count": successful,
    "success_rate": success_rate,
    "timing_stats": {
        "total_time_seconds": total_time,
        "average_time_per_url_seconds": avg_time_per_url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
}

# Print the results summary with timing statistics
print("\nBATCH SCRAPING RESULTS SUMMARY:")
print("-" * 80)
print(f"Total URLs processed: 1")
print(f"Successfully scraped: {successful}")
print(f"Success rate: {success_rate:.1f}%")
print(f"Total scraping time: {total_time:.2f} seconds")
print(f"Average time per URL: {avg_time_per_url:.2f} seconds")
print("-" * 80)

# Print content details for the URL
for i, result in enumerate(results):
    print(f"URL {i+1}: {result['url']}")
    content_length = len(result['content']) if isinstance(result['content'], str) else 'ERROR'
    print(f"Content length: {content_length}")
    
    # Print a small sample of the content
    if isinstance(result['content'], str) and len(result['content']) > 100:
        print(f"Content preview: {result['content'][:100].strip()}...")
    
    print("-" * 80)

# Save detailed results to a file
output_dir = "z_output"
os.makedirs(output_dir, exist_ok=True)

# Save raw results
with open(os.path.join(output_dir, "test_scraper_output.json"), "w") as f:
    json.dump(results, f, indent=2)

# Save in WebScrapeResults format
with open(os.path.join(output_dir, "test_webscrape_results.json"), "w") as f:
    json.dump(scrape_results, f, indent=2)

print(f"Detailed results saved to {os.path.join(output_dir, 'test_scraper_output.json')}")
print(f"WebScrapeResults format saved to {os.path.join(output_dir, 'test_webscrape_results.json')}")