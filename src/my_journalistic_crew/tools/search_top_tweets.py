from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel
from my_journalistic_crew.utils.webdriver import WebDriverClient
from my_journalistic_crew.utils.pagenav import PageNavigator
from my_journalistic_crew.utils.x_elements import ScraperInput 
from my_journalistic_crew.utils.scroller import scroll_to_load_tweets
from my_journalistic_crew.utils.tweet_extractor import extract_tweet_data
from urllib.parse import quote
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
from datetime import datetime
# Load environment variables
load_dotenv()
MIN_LIKES = int(os.getenv('MIN_LIKES', 10))  
MIN_RETWEETS = int(os.getenv('MIN_RETWEETS', 5)) 

def format_cookies_error(error):
    return json.dumps({
        'status': 'error',
        'error': f"Error loading cookies: {str(error)}",
        'filename': f"error_cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        'tweets': []
    })

def format_empty_response():
    return json.dumps({'tweets': []})

class TwitterScraper(BaseTool):
    name: str = "Twitter Scraper"
    description: str = (
        "A tool that navigates to a specific trending topic's page on Twitter/X, "
        "scrolls down the page to load tweets, and scrapes tweet content. "
        "It can handle both regular trends and hashtags, runs in either "
        "headless or visible browser mode, and can collect metrics, media, and user information."
    )
    args_schema: Type[BaseModel] = ScraperInput

    def no_cache(self, arguments: dict, result: str) -> bool:
        """
        Custom cache function that always returns False to prevent caching
        """
        return False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_function = self.no_cache  # Assign the custom cache function

    def _run(self, trend: str, is_hashtag: bool, headless: bool, device_type: str, 
             scroll_count: int, scroll_delay: float, max_tweets: int) -> str:
        """
        Navigate to a specific trend's page on Twitter/X, scroll down to load tweets,
        and scrape the tweets.
        
        Args:
            trend (str): The trend to navigate to
            is_hashtag (bool): Whether the trend is a hashtag
            headless (bool): Run browser in headless mode
            device_type (str): Device type to emulate
            scroll_count (int): Number of times to scroll down the page
            scroll_delay (float): Delay in seconds between scrolls
            max_tweets (int): Maximum number of tweets to collect,
        
        Returns:
            str: JSON string containing a structured output with status, message, and tweet data
        """
        try:
            driver_client = None
            
            # Initialize webdriver
            driver_client = WebDriverClient(headless=headless, device_type=device_type)
            driver = driver_client.get_driver()
            
            # Load cookies and navigate (from TrendNavigatorTool)
            try:
                with open('auth.json') as f:
                    cookies = json.load(f)['cookies']
            except Exception as e:
                return format_cookies_error(e)
            
            navigator = PageNavigator(driver)
            navigator.go_to_url("https://x.com")
            driver_client.add_cookies(cookies, ".x.com")
            navigator.refresh_page()

            # Prepare the search query
            query = f'%23{trend[1:]}' if is_hashtag else quote(trend)
            url = f"https://x.com/search?q={query}&src=trend_click&vertical=trends"
            
            # Navigate to the trend page
            navigator.go_to_url(url)
            
            # Wait for tweets to load with more robust conditions
            try:
                WebDriverWait(driver, 30).until(  # Increased timeout to 30 seconds
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
                )
                # Additional check for tweet content
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, '[data-testid="tweetText"]')) > 0
                )
            except Exception as e:
                print(f"Error waiting for tweets: {str(e)}")
                return format_empty_response()
            
            # Add debug logging
            print("Initial tweets found, starting collection...")
            
            tweets_collected = []
            processed_ids = set()
            timeout = 300  # 5 minute timeout
            
            # Define a function to extrlact tweets that can be passed to scroll_to_load_tweets
            def extract_tweets_func(tweet_elements, processed_ids):
                new_tweets = []
                new_processed_ids = set()
                
                print(f"Processing {len(tweet_elements)} tweet elements on page")
                
                for tweet_element in tweet_elements:
                    try:
                        # Get real tweet ID - try multiple methods
                        tweet_id = None
                        
                        # Try data-tweet-id attribute first
                        tweet_id = tweet_element.get_attribute("data-tweet-id")
                        
                        # Try link to tweet - this is more reliable than article element
                        if not tweet_id:
                            tweet_links = tweet_element.find_elements(By.CSS_SELECTOR, 'a[href*="/status/"]')
                            for link in tweet_links:
                                href = link.get_attribute('href')
                                if href and '/status/' in href:
                                    tweet_id = href.split('/status/')[-1].split('?')[0]
                                    break
                        
                        # Try finding the tweet ID in the element's attributes
                        if not tweet_id:
                            for attr in tweet_element.get_property('attributes'):
                                if attr['name'] == 'data-tweet-id' or 'tweet' in attr['name'].lower():
                                    tweet_id = attr['value']
                                    break
                        
                        # If we still don't have an ID, create one based on content
                        if not tweet_id:
                            try:
                                # Try to get content from tweet text element
                                content_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                                content = content_element.text[:50]  # First 50 chars
                            except:
                                content = tweet_element.text[:50]  # Fallback to full element text
                            tweet_id = f"synthetic-id-{hash(content)}"
                        
                        # Skip if we've already processed this tweet
                        if tweet_id in processed_ids:
                            continue
                        
                        # Add to processed set
                        new_processed_ids.add(tweet_id)
                        processed_ids.add(tweet_id)  # Add to the main set immediately
                        
                        # Extract tweet data
                        tweet = extract_tweet_data(tweet_element, tweet_id, driver)
                        
                        # Modify tweet collection to strictly enforce thresholds
                        if (tweet.metrics.likes and tweet.metrics.likes >= MIN_LIKES) and \
                           (tweet.metrics.retweets and tweet.metrics.retweets >= MIN_RETWEETS):
                            new_tweets.append(tweet)
                            new_processed_ids.add(tweet_id)
                            processed_ids.add(tweet_id)
                            print(f"Collected tweet: {tweet_id} with {tweet.metrics.likes} likes and {tweet.metrics.retweets} retweets")
                        else:
                            print(f"Skipping tweet: {tweet_id}")
                            continue  # Skip this tweet
                    except Exception as e:
                        print(f"Error processing tweet element: {str(e)}")
                        continue
                
                print(f"Found {len(new_tweets)} new tweets meeting both criteria, total processed IDs: {len(processed_ids)}")
                return new_tweets, new_processed_ids
            
            # Use the enhanced scrolling utility to collect tweets while scrolling
            scroll_success, tweets_collected = scroll_to_load_tweets(
                driver, 
                scroll_count, 
                scroll_delay, 
                extract_tweets_func=extract_tweets_func, 
                max_tweets=max_tweets, 
                timeout=timeout
            )
            
            # If we haven't reached max_tweets yet, try scrolling more aggressively
            if len(tweets_collected) < max_tweets:
                print(f"Only collected {len(tweets_collected)} tweets. Trying additional scrolls...")
                
                # Try more scrolls with larger jumps
                for _ in range(3):  # Try up to 3 more aggressive scrolls
                    if len(tweets_collected) >= max_tweets:
                        break
                        
                    # Scroll more aggressively
                    driver.execute_script("window.scrollBy(0, 3000);")
                    time.sleep(scroll_delay + 1)
                    
                    # Extract tweets after this aggressive scroll
                    tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
                    new_tweets, new_processed_ids = extract_tweets_func(tweet_elements, processed_ids)
                    tweets_collected.extend(new_tweets)
                    processed_ids.update(new_processed_ids)
                    
                    if not new_tweets:  # If no new tweets found, try clicking "Show more"
                        try:
                            show_more = driver.find_elements(By.XPATH, "//span[contains(text(), 'Show more')]")
                            if show_more:
                                show_more[0].click()
                                time.sleep(2)
                                
                                # Try to extract tweets after clicking "Show more"
                                tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
                                new_tweets, new_processed_ids = extract_tweets_func(tweet_elements, processed_ids)
                                tweets_collected.extend(new_tweets)
                        except Exception as e:
                            print(f"Error clicking 'Show more': {str(e)}")
            
            # Return as JSON string 
            return json.dumps({
                "tweets": [{
                    "id": str(tweet.structure.id),
                    "content": str(tweet.content) if tweet.content else "",
                    "user": str(tweet.user.handle) if tweet.user.handle else "",
                    "timestamp": str(tweet.timestamp.datetime) if tweet.timestamp.datetime else "",
                    "likes": int(tweet.metrics.likes) if tweet.metrics.likes is not None else 0,
                    "retweets": int(tweet.metrics.retweets) if tweet.metrics.retweets is not None else 0,
                    "replies": int(tweet.metrics.replies) if tweet.metrics.replies is not None else 0,
                    "has_photos": bool(tweet.media.hasPhotos),
                    "photo_urls": tweet.media.photoUrls,
                    "has_videos": bool(tweet.media.hasVideos),
                    "video_urls": tweet.media.videoUrls
                } for tweet in tweets_collected[:max_tweets]],
                "trend": trend,
                "count": min(len(tweets_collected), max_tweets)
            })

        except Exception as e:
            # Return an empty tweets list as flat JSON structure
            return json.dumps({
                "tweets": [],
                "trend": trend,
                "count": 0
            })
        
        finally:
            if driver_client:
                try:
                    driver_client.close()
                except Exception as e:
                    pass