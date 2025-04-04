#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime
from journalist.crew import Journalist
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

Category = {
    "News": {
        "subcategories": {
            "Kenya": {"author": "John Kamau"},
            "Africa": {"author": "Kwame Nkrumah"},
            "U.S.A": {"author": "John Smith"},
            "Europe": {"author": "James Wilson"},
            "Asia": {
                "authors": ["Li Wei", "Priya Patel"]
            },
            "Middle East": {"author": "David Cohen"}
        }
    },
    "Business": {
        "subcategories": {
            "Business News": {"author": "Dr. Emily Chebet"},
            "Startup Ideas": {"author": "Anne Mwangi"},
            "Stock Analysis": {"author": "Peter Kipchumba"},
            "Maritime Affairs": {"author": "Dr. Emily Chebet"}
        }
    },
    "Lifestyle": {
        "subcategories": {
            "Technology": {"author": "Anne Mwangi"},
            "Agriculture": {"author": "Peter Kipchumba"},
            "Health": {"author": "Dr. Emily Chebet"},
            "Food": {"author": "Marco Rossi"},
            "Travel": {"author": "Peter Kipchumba"},
            "Education": {"author": "Dr. Emily Chebet"},
            "Opinion": {"author": "Anne Mwangi"}
        }
    },
    "Sports": {
        "subcategories": {
            "Premier League": {"author": "James Wilson"},
            "League 1": {"author": "Pierre Dubois"},
            "Champions League": {"author": "Carlos Ruiz"},
            "Serie A": {"author": "Giovanni Moretti"},
            "Bundesliga": {"author": "Hans Müller"}
        }
    }
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
        "category": Category,
        "story": os.getenv("STORY", ""),
        "breaking_news": os.getenv("BREAKING_NEWS", False),
        "trending": os.getenv("TRENDING", False),
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
