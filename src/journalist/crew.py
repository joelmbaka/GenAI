from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from journalist.tools.twitter_scraper import TwitterScraper
from journalist.tools.news_search_tool import NewsSearchTool
from journalist.tools.scrape_website_tool import ScrapeWebsite
import os
from dotenv import load_dotenv
from journalist.tools.utils.models import ArticleModel
from journalist.tools.neo4j_article_tool import Neo4jArticleTool
from journalist.tools.image_search_tool import ImageSearchTool

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
            max_iter=os.getenv("MAX_ITER_WEB_AGENT", 1)
        )
    @agent
    def twitter_analysis_agent(self) -> Agent:
        """Twitter Analysis Agent"""
        return Agent(
            config=self.agents_config['twitter_analysis_agent'],
            max_iter=os.getenv("MAX_ITER_TWITTER_AGENT", 1)
        )
    @agent
    def news_reporter_agent(self) -> Agent:
        """News Reporter Agent"""
        return Agent(
            config=self.agents_config['news_reporter_agent'],
            max_iter=os.getenv("MAX_ITER_NEWS_AGENT", 1)
        )

    @task
    def web_search_task(self) -> Task:
        """Web Search Task"""
        return Task(
            config=self.tasks_config['web_search_task'],
            tools=[NewsSearchTool()]
        )
    @task
    def read_and_summarize_task(self) -> Task:
        """Read and Summarize Task"""
        return Task(
            config=self.tasks_config['read_and_summarize_task'],
            tools=[ScrapeWebsite()]
        )
    @task
    def twitter_scrape_task(self) -> Task:
        """Twitter Scrape Task"""
        return Task(
            config=self.tasks_config['twitter_scrape_task'],
            tools=[TwitterScraper()],
        )
    @task
    def twitter_sentiment_task(self) -> Task:
        """Twitter Sentiment Task"""
        return Task(
            config=self.tasks_config['twitter_sentiment_task'],
        )
    @task
    def image_search_task(self) -> Task:
        """Featured Image Search"""
        return Task(
            config=self.tasks_config["image_search_task"],
            tools=[ImageSearchTool()],
        )    
    @task
    def news_reporting_task(self) -> Task:
        """News Reporting Task"""
        return Task(
            config=self.tasks_config['news_reporting_task'],
            output_pydantic=ArticleModel
        )
    @task
    def push_article_to_neo4j_task(self) -> Task:
        """Push Article to Neo4j Task"""
        return Task(
            config=self.tasks_config['push_article_to_neo4j_task'],
            tools=[Neo4jArticleTool()],
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