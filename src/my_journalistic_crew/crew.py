import os
from dotenv import load_dotenv
load_dotenv() #load dotenv
from my_journalistic_crew.tools.twitter_scraper import TwitterScraper
from my_journalistic_crew.tools.news_search_tool import NewsSearchTool
from my_journalistic_crew.tools.image_search_tool import ImageSearchTool
from my_journalistic_crew.tools.scrape_website_tool import ScrapeWebsite
from my_journalistic_crew.models.ArticleModel import DraftArticle, FinalArticle
from my_journalistic_crew.tools.image_analysis_tool import ImageAnalysisTool
from my_journalistic_crew.tools.neo4j_article_tool import Neo4jArticleTool
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task, LLM
#llama 4 maverick from nvidia nim
llm = LLM(
        model=os.getenv("MODEL"),
        api_key=os.getenv("NVIDIA_API_KEY"),
        base_url="https://integrate.api.nvidia.com/v1",
        telemetry=False
        )
#set up the crewbase aka team
@CrewBase
class MyJournalisticCrew():
    """Journalist crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    #the people: scraper, writer, publisher
    @agent
    def researcher(self) -> Agent:
        """scrape raw content from html websites and web apps"""
        return Agent(
            config=self.agents_config['researcher'],
            respect_context_window=True,
            max_iterations=1,
            verbose=True,
            )
    @agent
    def writer(self) -> Agent:
        """read news stories, read tweets and write journalistic articles"""
        return Agent(
            config=self.agents_config['writer'],
            respect_context_window=True,
            max_iterations=4,
            verbose=True,
            )
    @agent
    def editor(self) -> Agent:
        """review and publish articles to neo4j database"""
        return Agent(
            config=self.agents_config['editor'],
            respect_context_window=True,
            max_iterations=1,
            verbose=True,
            )
    #tasks in sequential execution
    @task
    def search_news(self) -> Task:
        """search for news on google news api given a topic"""
        return Task(
            config=self.tasks_config['search_news'],
            tools=[NewsSearchTool()],
            )    
    @task
    def scrape_tweets(self) -> Task:
        """use selenium webdriver to:
            navigate to twitter, 
            enter your search query,
            and scrape number of tweets requested"""
        return Task(
            config=self.tasks_config['scrape_tweets'],
            tools=[TwitterScraper()],
            )
    @task
    def search_images(self) -> Task:
        """search for images on google images api given a topic"""
        return Task(
            config=self.tasks_config['search_images'],
            tools=[ImageSearchTool()],
            )
    @task
    def read_website(self) -> Task:
        """open and read news stories using selenium web scraper"""
        return Task(
            config=self.tasks_config['read_website'],
            tools=[ScrapeWebsite()],
            )
    @task
    def write(self) -> Task:
        """write a news article using journalistic style"""
        return Task(
            config=self.tasks_config['write'],
            output_pydantic=DraftArticle,
           )
    @task
    def select_image(self) -> Task:
        """select a suitable image and thumbnail using its title and recency to match our story"""
        return Task(
            config=self.tasks_config['select_image'],
            tools=[ImageAnalysisTool()],
           )
    @task
    def format(self) -> Task:
        """review article fields to conform to model requirements"""
        return Task(
            config=self.tasks_config['format'],
            output_pydantic=FinalArticle,
           )
    @task
    def publish(self) -> Task:
        """Publish Article to Neo4j"""
        return Task(
            config=self.tasks_config['publish'],
            tools=[Neo4jArticleTool()],
           )
    @crew
    def crew(self) -> Crew:
        """this creates my journalistic crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential,
            telemetry=False,
        ) 