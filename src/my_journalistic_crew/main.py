#!/usr/bin/env python
import os
# Disable OpenTelemetry completely
os.environ["OTEL_SDK_DISABLED"] = "true"

import sys
import warnings
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from my_journalistic_crew.crew import MyJournalisticCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """ 
    Run the crew and returns the results.
    """
    # Load environment variables
    
    inputs = {
        "topic" : "search the web for trade war proof sectors",
        "timestamp": datetime.now().isoformat(),
    }
    
    try:
        MyJournalisticCrew().crew().kickoff(inputs=inputs)
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
        MyJournalisticCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        MyJournalisticCrew().crew().replay(task_id=sys.argv[1])

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
        MyJournalisticCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
