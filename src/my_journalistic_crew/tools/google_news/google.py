from crewai.tools import BaseTool
from my_journalistic_crew.utils.webdriver import WebDriverClient
from my_journalistic_crew.utils.pagenav import PageNavigator
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from typing import List, Dict, Optional, Type
from pydantic import BaseModel, Field
import time
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random

class GoogleSearchToolInput(BaseModel):
    """Input schema for GoogleSearchTool."""
    query: str = Field(..., description="The search query to perform on Google.")
    scroll_times: int = Field(default=1, description="Number of times to scroll the page.")

class GoogleSearchTool(BaseTool):
    name: str = "Google Search Tool"
    description: str = "A tool to perform Google searches and return the results."
    args_schema: Type[BaseModel] = GoogleSearchToolInput

    def _run(self, query: str, scroll_times: int = 1) -> List[Dict[str, Optional[str]]]:
        """Perform a Google search and return the results"""
        driver_client = WebDriverClient(headless=True)
        driver = driver_client.get_driver()
        navigator = PageNavigator(driver)
        results = []

        # Navigate to Google
        if not navigator.go_to_url("https://www.google.com"):
            driver_client.close()
            return results

        # Wait for the page to load
        time.sleep(random.uniform(2, 5))  # Random delay

        # Locate the search input field
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Wait for the results to load
        time.sleep(random.uniform(2, 5))  # Random delay

        # Scroll the page multiple times
        for _ in range(scroll_times):
            navigator.scroll_page(random.randint(500, 1000))  # Random scroll amount
            time.sleep(random.uniform(1, 3))  # Random delay

        # Extract search results
        result_elements = driver.find_elements(By.CSS_SELECTOR, "div.g")
        for element in result_elements:
            title = element.find_element(By.CSS_SELECTOR, "h3").text
            link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            snippet = element.find_element(By.CSS_SELECTOR, "div.IsZvec").text if element.find_elements(By.CSS_SELECTOR, "div.IsZvec") else None
            results.append({
                "title": title,
                "link": link,
                "snippet": snippet
            })

        # Save results to a JSON file
        with open("google_search_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        driver_client.close()
        return results
