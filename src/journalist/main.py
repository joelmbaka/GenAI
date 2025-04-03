#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime
from journalist.crew import Journalist
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

MainCategory = ["News", "Business", "Lifestyle", "Sports", "Environment", "SpecialFeatures"]
SubCategory = ["Local News", "World News", "Enterprise", "Finance", "Technology", "Agriculture", "Health", "Food", "Travel", "Education", "Opinion"]
Authors = {
    "LocalNews": ["John Kamau"],
    "WorldNews": ["Mary Wambui"],
    "Enterprise": ["Brian Omondi"],
    "Finance": ["Dr. Lucy Wanjiru"],
    "Technology": ["Prof. Michael Ndung'u"],
    "Agriculture": ["Lilian Mueni"],
    "Health": ["Dr. Emily Chebet"],
    "Food": ["Anne Mwangi"],
    "Travel": ["Peter Kipchumba"],
    "Education": ["Dr. Emily Chebet"],
    "Opinion": ["Anne Mwangi"],
}

def run():
    """
    Run the crew and returns the results.
    """
    # Load environment variables
    
    inputs = {
        "google_query": os.getenv("GOOGLE_QUERY", ""),
        "twitter_query": os.getenv("TWITTER_QUERY", ""),
        "my_thoughts": os.getenv("MY_THOUGHTS", ""),
        "category": MainCategory,
        "subcategory": SubCategory,
        "story": os.getenv("STORY", ""),
        "breaking_news": os.getenv("BREAKING_NEWS", False),
        "trending": os.getenv("TRENDING", False),
        "authors": Authors,
        "timestamp": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")),
        "max_tweets": os.getenv("MAX_TWEETS", 10),
        "is_hashtag": os.getenv("IS_HASHTAG", False),
    }
    
    try:
        Journalist().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Journalist().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Journalist().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        Journalist().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
