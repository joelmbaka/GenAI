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

    ###agents###
    @agent
    def google_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['google_agent'],
            llm=llm,
            verbose=True,
            max_iter=3,
            tools=[SerperDevTool()],
        )
    @agent
    def article_reader(self) -> Agent:
        return Agent(
            config=self.agents_config['article_reader'],
            llm=llm,
            verbose=True,
            max_iter=3,
            tools=[WebScraper()],
        )
    @agent
    def twitter_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['twitter_agent'],
            llm=llm,
            verbose=True,
            max_iter=1,
            tools=[TwitterScraper()],
        )
    @agent
    def twitter_sentiment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['twitter_sentiment_agent'],
            llm=llm,
            verbose=True,
            max_iter=2,
            tools=[],
        )
    @agent        
    def article_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['article_writer'],
            llm=llm,
            verbose=True,
            max_iter=3,
            tools=[],
        )

    ###tasks###
    @task
    def search_google(self) -> Task:
        return Task(
            config=self.tasks_config['search_google'],
        )
    @task
    def read_articles(self) -> Task:
        return Task(
            config=self.tasks_config['read_articles'],
        )
    @task
    def scrape_twitter(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_twitter'],
        )
    @task
    def twitter_sentiments(self) -> Task:
        return Task(
            config=self.tasks_config['twitter_sentiments'],
        )
    @task
    def write_article(self) -> Task:
        return Task(
            config=self.tasks_config['write_article'],
        )

    ###mbogi###
    @crew
    def crew(self) -> Crew:
        """Creates the Journalist crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential,
            telemetry=False,
            output_log_file=True,
            max_iter=3,
        )
