import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from journalist.tools.query_article_tool import QueryArticleTool, QueryArticleInput
import unittest
from dotenv import load_dotenv

load_dotenv()

class TestQueryArticleTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the tool
        cls.tool = QueryArticleTool()

    def test_query_trump_tariffs(self):
        # Test query related to Trump tariffs
        result = self.tool._run(QueryArticleInput(
            query="Trump's 'Liberation Day' tariffs"
        ))
        
        # Verify the response contains expected content
        self.assertIn("Trump", result)
        self.assertIn("tariffs", result)
        self.assertIn("Liberation Day", result)
        print("\nTrump Tariffs Query Results:\n", result)

    def test_query_middle_east_tensions(self):
        # Test query related to Middle East tensions
        result = self.tool._run(QueryArticleInput(
            query="US military presence in the Middle East"
        ))
        
        # Verify the response contains expected content
        self.assertIn("Middle East", result)
        self.assertIn("Warplanes", result)
        self.assertIn("Naval Ships", result)
        print("\nMiddle East Tensions Query Results:\n", result)

    def test_no_results(self):
        # Test a query that shouldn't match anything
        result = self.tool._run(QueryArticleInput(
            query="Ancient Roman architecture"
        ))
        
        # Verify the no results message
        self.assertEqual(result, "No similar articles found.")
        print("\nNo Results Test:\n", result)

if __name__ == "__main__":
    unittest.main() 