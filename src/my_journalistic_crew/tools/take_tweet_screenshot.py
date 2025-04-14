from crewai.tools import BaseTool
from typing import Type, Dict, Any, Optional
from pydantic import BaseModel, Field
from my_journalistic_crew.utils.webdriver import WebDriverClient
from my_journalistic_crew.utils.pagenav import PageNavigator
import json
import os
import time
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO


class TweetScreenshotInput(BaseModel):
    """Input schema for TweetScreenshot."""
    tweet_id: str = Field(..., description="The ID of the tweet to screenshot.")
    headless: bool = Field(True, description="Run browser in headless mode.")
    device_type: str = Field("desktop", description="Device type to emulate.")
    wait_time: int = Field(10, description="Time to wait for tweet to load (seconds).")
    element_only: bool = Field(True, description="Take screenshot of just the tweet element instead of full page.")
    use_pil_crop: bool = Field(True, description="Use PIL to crop image if element screenshot fails.")


class TweetScreenshotTool(BaseTool):
    name: str = "Tweet Screenshot Tool"
    description: str = (
        "A tool that takes a tweet ID, navigates to the tweet URL on Twitter/X, "
        "and captures a screenshot of the tweet. The screenshot is saved to the "
        "z_output folder with a timestamp and the tweet ID in the filename. "
        "Can capture either the full page or just the tweet element."
    )
    args_schema: Type[BaseModel] = TweetScreenshotInput

    def get_specific_tweet(self, driver, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve details about a specific tweet.
        
        Args:
            driver: Selenium WebDriver instance
            tweet_id: The ID of the tweet to retrieve
            
        Returns:
            Dict with tweet details or None if not found
        """
        try:
            # Use selectors identified from our analysis
            selectors = [
                # Primary selectors (most specific)
                'article[data-testid="tweet"]',
                'div[data-testid="tweetDetail"]',
                
                # Content selectors (for just the text)
                'div[data-testid="tweetText"]',
                
                # Fallback selectors (less specific)
                'article[role="article"]',
                'div[data-testid="cellInnerDiv"]',
                'article'
            ]
            
            # Try selectors in priority order
            tweet_element = None
            successful_selector = None
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        tweet_element = elements[0]
                        successful_selector = selector
                        print(f"Found tweet using selector: {selector}")
                        break
                except Exception as e:
                    print(f"Error with selector {selector}: {str(e)}")
                    continue
            
            if not tweet_element:
                print("Could not find tweet element with any selector")
                return None
                
            # Extract user information
            user_handle = None
            try:
                # Try different user handle selectors
                user_selectors = [
                    'a[href*="/status/"] span',
                    'div[dir="ltr"] span',
                    'span[data-testid="tweetAuthor"]',
                    'span[class*="r-"]' # Twitter often uses class names starting with r-
                ]
                
                for selector in user_selectors:
                    try:
                        elements = tweet_element.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            text = element.text
                            if text and text.startswith('@'):
                                user_handle = text
                                break
                        if user_handle:
                            break
                    except Exception:
                        continue
            except Exception as e:
                print(f"Error extracting user handle: {str(e)}")
                user_handle = None
                
            # Extract tweet content
            content = None
            try:
                # Try content selectors
                content_selectors = [
                    '[data-testid="tweetText"]',
                    'div[lang]',
                    'div[dir="auto"]'
                ]
                
                for selector in content_selectors:
                    try:
                        elements = tweet_element.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            content = elements[0].text
                            break
                    except Exception:
                        continue
            except Exception as e:
                print(f"Error extracting content: {str(e)}")
                content = None
                
            return {
                'id': tweet_id,
                'element': tweet_element,
                'selector': successful_selector,
                'user': user_handle,
                'content': content
            }
        except Exception as e:
            print(f"Error retrieving tweet: {str(e)}")
            return None

    def take_element_screenshot(self, driver, element, filename) -> bool:
        """Take screenshot of just a specific element"""
        try:
            # Scroll to element and center it
            driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});
                window.scrollBy(0, -50); // Slight adjustment to avoid headers
            """, element)
            time.sleep(1)  # Wait for scroll to complete
            
            # Hide fixed position elements that might overlay
            try:
                driver.execute_script("""
                    // Hide all header, sidebar and fixed elements
                    var elements = document.querySelectorAll('header, [role="banner"], [data-testid="primaryColumn"], div[style*="position: fixed"]');
                    for (var i = 0; i < elements.length; i++) {
                        var style = window.getComputedStyle(elements[i]);
                        if (style.position === 'fixed' || style.position === 'sticky') {
                            elements[i].style.visibility = 'hidden';
                        }
                    }
                    
                    // Hide specific Twitter elements that might overlap
                    document.querySelectorAll('[data-testid="caret"], [aria-label="More"], [role="complementary"]').forEach(e => {
                        if (e) e.style.display = 'none';
                    });
                    
                    // Add a thin border to highlight the element
                    arguments[0].style.border = '1px solid #e1e8ed';
                """, element)
                time.sleep(0.5)  # Wait for visibility changes
            except Exception as e:
                print(f"Warning: Could not hide fixed elements: {str(e)}")
            
            # Add small margin by adding padding
            try:
                driver.execute_script("""
                    var originalPadding = window.getComputedStyle(arguments[0]).padding;
                    arguments[0].style.padding = '10px';
                """, element)
            except Exception as e:
                print(f"Warning: Could not add padding: {str(e)}")
            
            # Take element screenshot
            element.screenshot(filename)
            print(f"Element screenshot saved to {filename}")
            return True
        except Exception as e:
            print(f"Error taking element screenshot: {str(e)}")
            return False

    def take_text_element_screenshot(self, driver, element, filename) -> bool:
        """Take screenshot of the profile image and tweet text only"""
        try:
            # Find the tweet container element
            tweet_container = element.find_element(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            # Find the profile image element
            profile_image = tweet_container.find_element(By.CSS_SELECTOR, 'img[src*="profile_images"]')
            
            # Find the tweet text element
            tweet_text = tweet_container.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
            
            # Create a bounding box that includes the profile image and tweet text
            profile_image_location = profile_image.location
            profile_image_size = profile_image.size
            tweet_text_location = tweet_text.location
            tweet_text_size = tweet_text.size
            
            # Calculate the bounding box
            left = min(profile_image_location['x'], tweet_text_location['x'])
            top = min(profile_image_location['y'], tweet_text_location['y'])
            right = max(profile_image_location['x'] + profile_image_size['width'], 
                        tweet_text_location['x'] + tweet_text_size['width'])
            bottom = max(profile_image_location['y'] + profile_image_size['height'], 
                         tweet_text_location['y'] + tweet_text_size['height'])
            
            # Add a small margin (10px on each side)
            margin = 10
            left = max(0, left - margin)
            top = max(0, top - margin)
            right = right + margin
            bottom = bottom + margin
            
            # Take full page screenshot
            png_data = driver.get_screenshot_as_png()
            
            # Crop image to the bounding box
            im = Image.open(BytesIO(png_data))
            im = im.crop((left, top, right, bottom))
            
            # Save cropped image
            im.save(filename)
            print(f"Tweet screenshot (profile + text) saved to {filename}")
            return True
        except Exception as e:
            print(f"Error taking tweet screenshot: {str(e)}")
            return False

    def crop_screenshot_with_pil(self, driver, element, filename) -> bool:
        """Use PIL to take a full screenshot and crop to just the element"""
        try:
            # Take full page screenshot
            png_data = driver.get_screenshot_as_png()
            
            # Get element location and size
            location = element.location_once_scrolled_into_view
            size = element.size
            
            # Add small margin (10px on each side)
            margin = 10
            left = max(0, location['x'] - margin)
            top = max(0, location['y'] - margin)
            right = location['x'] + size['width'] + margin
            bottom = location['y'] + size['height'] + margin
            
            # Crop image
            im = Image.open(BytesIO(png_data))
            im = im.crop((left, top, right, bottom))
            
            # Save cropped image
            im.save(filename)
            print(f"PIL cropped screenshot saved to {filename}")
            return True
        except Exception as e:
            print(f"Error cropping with PIL: {str(e)}")
            return False

    def _run(self, tweet_id: str, headless: bool = False, device_type: str = "desktop", 
             wait_time: int = 10, element_only: bool = True, use_pil_crop: bool = True) -> str:
        """
        Navigate to a specific tweet URL and capture a screenshot.
        
        Args:
            tweet_id (str): The ID of the tweet to capture
            headless (bool): Run browser in headless mode
            device_type (str): Device type to emulate
            wait_time (int): Time to wait for tweet to load (seconds)
            element_only (bool): Take screenshot of just the tweet element instead of full page
            use_pil_crop (bool): Use PIL to crop image if element screenshot fails
        
        Returns:
            str: Path to the saved screenshot or error message
        """
        driver_client = None
        
        try:
            # Initialize webdriver with smaller width for better tweet capture
            driver_client = WebDriverClient(headless=headless, device_type=device_type)
            driver = driver_client.get_driver()
            
            # Set window size to emulate a narrower view (better for tweets)
            if device_type == "desktop":
                driver.set_window_size(800, 900)
            
            # Load cookies and navigate
            try:
                with open('auth.json') as f:
                    cookies = json.load(f)['cookies']
            except Exception as e:
                return f"Error loading cookies: {str(e)}"
            
            # Configure browser and set up navigator
            navigator = PageNavigator(driver)
            navigator.go_to_url("https://x.com")
            driver_client.add_cookies(cookies, ".x.com")
            navigator.refresh_page()
            
            # Navigate to the tweet - use direct status URL
            tweet_url = f"https://x.com/i/status/{tweet_id}"
            print(f"Navigating to tweet URL: {tweet_url}")
            navigator.go_to_url(tweet_url)
            
            # Wait for tweet to load
            try:
                print(f"Waiting up to {wait_time}s for tweet to load...")
                WebDriverWait(driver, wait_time).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')) > 0 or 
                              len(d.find_elements(By.CSS_SELECTOR, '[role="article"]')) > 0 or
                              len(d.find_elements(By.CSS_SELECTOR, '[data-testid="tweetDetail"]')) > 0
                )
                
                # Additional wait for page to stabilize
                time.sleep(3)
                
            except Exception as e:
                return f"Error waiting for tweet to load: {str(e)}"
            
            # Create output directory if it doesn't exist
            output_dir = "z_output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generate filename with timestamp and tweet ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/tweet_{tweet_id}_{timestamp}.png"
            
            # Get the specific tweet data
            tweet_data = self.get_specific_tweet(driver, tweet_id)
            
            if element_only and tweet_data and tweet_data['element']:
                # Take screenshot of the profile image and tweet text
                element = tweet_data['element']
                took_screenshot = self.take_text_element_screenshot(driver, element, filename)
                
                # If screenshot failed, fall back to full element screenshot
                if not took_screenshot:
                    took_screenshot = self.take_element_screenshot(driver, element, filename)
                    
                    # If element screenshot failed and PIL cropping is enabled, try that instead
                    if not took_screenshot and use_pil_crop:
                        took_screenshot = self.crop_screenshot_with_pil(driver, element, filename)
                    
                    # If both methods failed, fall back to full page
                    if not took_screenshot:
                        element_only = False
                        print("Element screenshot failed, falling back to full page")
            
            # Take full page screenshot if element screenshot failed or not requested
            if not element_only:
                try:
                    driver.save_screenshot(filename)
                    print(f"Full page screenshot saved to {filename}")
                except Exception as e:
                    return f"Error saving screenshot: {str(e)}"
            
            # Return success message with the path to the screenshot and tweet info
            if tweet_data and tweet_data['user']:
                return f"Screenshot captured and saved to {filename} (User: {tweet_data['user']})"
            else:
                return f"Screenshot captured and saved to {filename}"

        except Exception as e:
            return f"Error capturing screenshot: {str(e)}"
        
        finally:
            if driver_client:
                try:
                    driver_client.close()
                except Exception as e:
                    print(f"Error closing driver: {str(e)}")
                    pass 