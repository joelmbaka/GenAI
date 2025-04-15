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
from my_journalistic_crew.models.categories import Categories

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """ 
    Run the crew and returns the results.
    """
    # Load environment variables
    
    inputs = {
        "topic" : "Lets follow a developing story about Kiambu Governor Wamatangi, a member of UDA party, who has been Arrested over alleged graft. Conduct a thorough search to find out if there have ever been past graft allegations on this man before this one. Find out if there are any fallouts with the current president who is also the UDA party leader, because in this nation when you fall out with a seating president you are likely to be unfairly scrutinized with impunity",
        "timestamp": datetime.now().isoformat(),
        "categories": Categories
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
        "topic": "AI LLMs",
        "categories": Categories
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
        "current_year": str(datetime.now().year),
        "categories": Categories
    }
    try:
        MyJournalisticCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
