from src.journalist.tools.pygooglenews import GoogleNewsTool
import json

def test_google_news_tool():
    # Initialize the tool
    tool = GoogleNewsTool()
    """
    # Test 1: Basic search
    print("Testing basic search...")
    basic_result = tool._run(query="sabina chege")
    print(f"Basic search results: {basic_result[:500]}...")  # Print first 500 chars
    """
    """
    # Test 2: Language and country filter
    print("\nTesting language and country filter...")
    lang_result = tool._run(query="sabina chege", lang="en", country="KE")
    print(f"English results: {lang_result[:500]}...")

     # Test 3: Time period filter
    print("\nTesting time period filter...")
    time_result = tool._run(query="sabina chege", when="2d")
    print(f"Last day results: {time_result[:500]}...")
    """
    # Test 4: Date range filter
    print("\nTesting date range filter...")
    date_result = tool._run(query="sabina chege", from_date="2025-03-15", to_date="2025-03-29")
    print(f"March 15-29, 2025 results: {date_result[:500]}...")
    """
    # Test 5: Complex query with multiple parameters
    print("\nTesting complex query...")
    complex_result = tool._run(
        query="sabina chege",
        lang="en",
        country="KE",
        when="1w",
        from_date="2025-03-15",
        to_date="2025-03-29"
    )
    print(f"Complex query results: {complex_result[:500]}...")
    """
if __name__ == "__main__":
    test_google_news_tool()
