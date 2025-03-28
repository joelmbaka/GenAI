#!/usr/bin/env python
import sys
import warnings
import json
import os

from datetime import datetime

from journalist.crew import Journalist

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Load tweets data if file exists and is not empty
tweets_data = None
try:
    with open('tweets.json', 'r') as f:
        content = f.read()
        if content.strip():  # Check if file has content
            tweets_data = json.loads(content)
except (FileNotFoundError, json.JSONDecodeError):
    pass

def run():
    """
    Run the crew and returns the results.
    """
    inputs = {
        "topic": "Emmanuel Macron, scrape 5 tweets",
        "current_year": str(datetime.now().year),
        "tweets_data": tweets_data
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
