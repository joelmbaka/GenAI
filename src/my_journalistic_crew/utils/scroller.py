from my_journalistic_crew.utils.webdriver import WebDriverClient
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

def scroll_to_load_tweets(driver: WebDriverClient, scroll_count: int, scroll_delay: float, extract_tweets_func=None, max_tweets: int = None, timeout: int = 300):
    """
    Scroll down the page to load more tweets, extracting tweets during scrolling.
    
    Args:
        driver: Selenium WebDriver instance
        scroll_count: Number of times to scroll; each scroll fetches roughly 10 tweets
        scroll_delay: Delay between scrolls
        extract_tweets_func: Function to extract tweets from the page
        max_tweets: Maximum number of tweets to collect
        timeout: Maximum time to spend scrolling
        
    Returns:
        tuple: (bool, list) - Success status and collected tweets
    """
    start_time = time.time()
    tweets_collected = []
    processed_ids = set()
    last_height = 0
    consecutive_no_change = 0
    
    for i in range(scroll_count):
        # Check timeout
        if time.time() - start_time > timeout:
            return False, tweets_collected
            
        # Check if we've reached max tweets
        if max_tweets and len(tweets_collected) >= max_tweets:
            return True, tweets_collected

        # Extract tweets after this scroll if extract function provided
        if extract_tweets_func:
            tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
            print(f"Found {len(tweet_elements)} tweet elements on scroll {i+1}")
            
            # Call the extract function with the tweet elements
            new_tweets, new_processed_ids = extract_tweets_func(tweet_elements, processed_ids)
            tweets_collected.extend(new_tweets)
            processed_ids.update(new_processed_ids)
            
            print(f"Collected {len(new_tweets)} new tweets on scroll {i+1}, total: {len(tweets_collected)}")
            
            # Check if we've reached the maximum
            if max_tweets and len(tweets_collected) >= max_tweets:
                return True, tweets_collected

        # Get current scroll height
        current_height = driver.execute_script("return document.body.scrollHeight")
        
        # If height hasn't changed, try more aggressive scrolling
        if current_height == last_height:
            consecutive_no_change += 1
            if consecutive_no_change >= 2:
                # Try scrolling more aggressively
                driver.execute_script("window.scrollBy(0, 2000);")
                time.sleep(scroll_delay)
                
                # Try clicking "Show more" if available
                try:
                    show_more = driver.find_elements(By.XPATH, "//span[contains(text(), 'Show more')]")
                    if show_more:
                        show_more[0].click()
                        time.sleep(2)
                except:
                    pass
        else:
            consecutive_no_change = 0
        
        # Remember the height for next comparison
        last_height = current_height
        
        # Scroll down - use a larger scroll distance to ensure new tweets load
        scroll_distance = min(1500, current_height // 3)  # Scroll by 1/3 of page or 1500px max
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        
        # Wait between scrolls
        time.sleep(scroll_delay + 0.5)
        
        # Wait for new content to load after scrolling
        try:
            WebDriverWait(driver, 5).until(
                lambda d: d.execute_script("return document.body.scrollHeight") > current_height
            )
        except:
            # If no new content loaded, try again with a different approach
            driver.execute_script("window.scrollBy(0, 2000);")
            time.sleep(scroll_delay)
    
    return True, tweets_collected 