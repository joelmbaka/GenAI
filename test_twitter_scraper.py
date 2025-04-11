#!/usr/bin/env python3

import json
import os
from dotenv import load_dotenv
from src.my_journalistic_crew.tools.twitter_scraper import TwitterScraper

# Load environment variables
load_dotenv()

# Ensure required environment variables exist
if "MIN_LIKES" not in os.environ:
    os.environ["MIN_LIKES"] = "10"  # Default minimum likes
if "MIN_RETWEETS" not in os.environ:
    os.environ["MIN_RETWEETS"] = "5"  # Default minimum retweets

def main():
    # Initialize the Twitter scraper
    scraper = TwitterScraper()
    
    # Define parameters
    trend = "sha ceo"
    is_hashtag = False
    headless = False  # Set to True for headless mode
    device_type = "desktop"
    scroll_count = 5
    scroll_delay = 1.0
    max_tweets = 10
    
    print(f"Starting Twitter scraper test with trend: '{trend}'")
    
    # Run the scraper
    try:
        result = scraper._run(
            trend=trend,
            is_hashtag=is_hashtag,
            headless=headless,
            device_type=device_type,
            scroll_count=scroll_count,
            scroll_delay=scroll_delay,
            max_tweets=max_tweets
        )
        
        # Parse and display results
        data = json.loads(result)
        print(f"\nResults summary:")
        print(f"- Trend: {data.get('trend')}")
        print(f"- Tweets found: {data.get('count')}")
        
        # Print tweet details
        print("\nTweet details:")
        for i, tweet in enumerate(data.get('tweets', []), 1):
            print(f"\n--- Tweet {i} ---")
            print(f"ID: {tweet.get('id')}")
            print(f"User: {tweet.get('user')}")
            print(f"Content: {tweet.get('content')[:100]}..." if len(tweet.get('content', '')) > 100 else tweet.get('content'))
            print(f"Likes: {tweet.get('likes')}")
            print(f"Retweets: {tweet.get('retweets')}")
            print(f"Has photos: {tweet.get('has_photos')}")
            print(f"Timestamp: {tweet.get('timestamp')}")
    
    except Exception as e:
        print(f"Error running Twitter scraper: {str(e)}")

if __name__ == "__main__":
    main() 