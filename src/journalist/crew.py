from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from journalist.tools.twitter_scraper import TwitterScraper
from journalist.tools.web_scraper import WebScraper
#from journalist.tools.url_scraper import URLScraper
from crewai_tools import SerperDevTool
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
    tools = [TwitterScraper(), SerperDevTool(), WebScraper()]
###agents###
    @agent
    def political_news_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['political_news_reporter'],
            llm=llm,
            verbose=True,
            cache=False,
            max_iter=1,
        )
    @agent
    def business_news_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['business_news_reporter'],
            llm=llm,
            verbose=True,
            cache=False,
            max_iter=1,
        )
    @agent
    def sports_news_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['sports_news_reporter'],
            llm=llm,
            verbose=True,
            cache=False,
            max_iter=1,
        )
    
###tasks###
    @task
    def twitter_scraper_task(self) -> Task:
        return Task(
            config=self.tasks_config['twitter_scraper_task'],
            tools=[TwitterScraper()],
        )
    @task
    def serper_task(self) -> Task:
        return Task(
            config=self.tasks_config['serper_task'],
            tools=[SerperDevTool()],
        )
    @task
    def web_scraper_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_scraper_task'],
            tools=[WebScraper()],
        )
    @task
    def writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['writing_task'],
        )
    
    def chief_editor(self) -> Agent:
        return Agent(
            role="Chief Editor for the Kenya Times Magazine",
            goal="Assign tasks to journalists based on the category of the topic.",
            backstory="You're a meticulous senior editor with a keen eye for detail.",
            allow_delegation=True,
            llm=llm,
            verbose=True,
            cache=False,
            max_iter=1,
    )

    @crew
    def crew(self) -> Crew:
        """Creates the Journalist crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.chief_editor(),
            verbose=True,
            telemetry=False,
            cache=False,
            output_log_file="output.log",
            max_iter=1,
            
        )
