import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from journalist.tools.utils.models import ArticleModel
from journalist.tools.neo4j_article_tool import Neo4jArticleTool, Neo4jArticleInput

def test_neo4j_tool():
    # Create a sample article based on the WSJ story
    article = ArticleModel(
        title="U.S. Sends Warplanes, Ships to the Middle East in Warning to Iran",
        content="""The United States has deployed additional warplanes and naval assets to the Middle East as a show of force and warning to Iran. This military buildup comes amid escalating tensions in the region and concerns about Iran's nuclear program. The deployment includes advanced fighter jets and destroyers, significantly bolstering U.S. military presence in the area. Pentagon officials stated that these moves are defensive in nature and meant to deter potential aggression. The situation remains fluid as diplomatic efforts continue alongside the military buildup.""",
        source="Wall Street Journal",
        category="International, Military",  # Updated categories
        story="Middle East Tensions",  # New story field
        author="Joel Mbaka",  # Specified author
        featured_image="https://images.wsj.net/im-1234567/social",  # Placeholder image URL
        summary="Analysis of U.S. military deployments to the Middle East and their implications for regional security",
        keywords=["US Military", "Middle East", "Iran", "Warplanes", "Naval Ships"],
        entities=[
            "Country:United States",
            "Country:Iran",
            "Organization:Pentagon",
            "Region:Middle East",
            "MilitaryAsset:Warplanes",
            "MilitaryAsset:Naval Ships"
        ],
        metadata=json.dumps({
            "word_count": 1200,
            "reading_time": "5 minutes",
            "original_url": "https://www.wsj.com/world/middle-east/u-s-sends-warplanes-ships-to-the-middle-east-in-warning-to-iran-f72fcaff"
        })
    )

    # Create the tool instance
    tool = Neo4jArticleTool()

    # Create the input
    tool_input = Neo4jArticleInput(article=article)

    # Test the tool
    try:
        result = tool._run(tool_input.article)
        print("Test successful!")
        print("Result:", result)
        
        # Verify embedding was created
        if "embedding" in result.lower():
            print("Embedding successfully stored!")
        else:
            print("Warning: Embedding storage not confirmed")
            
    except Exception as e:
        print("Test failed!")
        print("Error:", str(e))

if __name__ == "__main__":
    test_neo4j_tool() 