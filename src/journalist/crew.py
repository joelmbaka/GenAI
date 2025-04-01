from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from journalist.tools.twitter_scraper import TwitterScraper
from journalist.tools.serper_dev import SerperDevTool
from journalist.tools.web_scraper import WebScraper
import os
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
        model=os.getenv("MODEL"),
        api_key=os.getenv("NVIDIA_API_KEY"),
        base_url="https://integrate.api.nvidia.com/v1",
        telemetry=False
        )

@CrewBase
class Journalist():
    """Journalist crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def web_research_agent(self) -> Agent:
        """Web Research Agent"""
        return Agent(
            config=self.agents_config['web_research_agent'],
            tools=[SerperDevTool(), WebScraper()]
        )
    @task
    def web_search_task(self) -> Task:
        """Web Search Task"""
        return Task(
            config=self.tasks_config['web_search_task'],
            tools=[SerperDevTool()],
        )
    @task
    def read_and_summarize(self) -> Task:
        """Read and Summarize Task"""
        return Task(
            config=self.tasks_config['read_and_summarize_task'],
            tools=[WebScraper()],
        )
    @crew
    def crew(self) -> Crew:
        """Creates the Journalist crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential,
            telemetry=False,
        )
