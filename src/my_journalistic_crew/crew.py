from my_journalistic_crew.tools.search_top_tweets import TwitterScraper
from my_journalistic_crew.tools.search_google_news import NewsSearchTool
from my_journalistic_crew.tools.search_google_images import ImageSearchTool
from my_journalistic_crew.tools.read_website_content import ScrapeWebsite
from my_journalistic_crew.tools.take_tweet_screenshot import TweetScreenshotTool
from my_journalistic_crew.tools.analyse_image import ImageAnalysisTool
from my_journalistic_crew.tools.download_image import DownloadImageTool
from my_journalistic_crew.tools.send_image_blob import BlobStorageTool
from my_journalistic_crew.MyPyModels.ArticleModel import GoogleNewsResults, GoogleImageResults, DraftArticle, FinalArticle
from my_journalistic_crew.tools.send_article_neo4j import Neo4jArticleTool
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task, LLM
import os
from dotenv import load_dotenv

load_dotenv() #load dotenv

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

    #the people: researcher, writer, editor
    @agent
    def researcher(self) -> Agent:
        """conduct research about a trending topic
        you have tools like google news api, google image search, video search, twitter scraper
        you pass the information as JSON
        """
        return Agent(
            config=self.agents_config['researcher'],
            respect_context_window=True,
            verbose=True,
            )
    @agent
    def analyst(self) -> Agent:
        """you read web pages, analyse images, and read tweets
        you download images and upload them to blob storage
        your reports form the basis of the final article  
        """
        return Agent(
            config=self.agents_config['writer'],
            respect_context_window=True,
            verbose=True,
            )
    @agent
    def writer(self) -> Agent:
        """write an engaging news article in markdown format with embedded imageurls. 
        the article will be published on my blog"""
        return Agent(
            config=self.agents_config['writer'],
            respect_context_window=True,
            verbose=True,
            allow_delegation=False,
            )
    #tasks in sequential execution
###the researcher
    @task
    def search_news(self) -> Task:
        """search for news using news search tool"""
        return Task(
            config=self.tasks_config['search_news'],
            tools=[NewsSearchTool()],
            output_pydantic=GoogleNewsResults
            )
    @task
    def search_images(self) -> Task:
        """search for images using image search tool"""
        return Task(
            config=self.tasks_config['search_images'],
            tools=[ImageSearchTool()],
            output_pydantic=GoogleImageResults
            )
    @task
    def search_tweets(self) -> Task:
        """use selenium webdriver to:
            navigate to twitter, 
            enter your search query,
            and scrape number of tweets requested"""
        return Task(
            config=self.tasks_config['search_tweets'],
            tools=[TwitterScraper()]
            )    
    ###the analyst
    @task
    def read_websites(self) -> Task:
        """open and read news stories using read website content tool"""
        return Task(
            config=self.tasks_config['read_websites'],
            tools=[ScrapeWebsite()]
            )
    @task
    def take_screenshots(self) -> Task:
        """take screenshots of top tweets using take tweet screenshot tool
        1 or 2 screnshots will be embedded into the article if necessary
        """
        return Task(
            config=self.tasks_config['take_screenshots'],
            tools=[TweetScreenshotTool()]
            )
    @task
    def analyse_images(self) -> Task:
        """analyse images using image analysis tool"""
        return Task(
            config=self.tasks_config['analyse_images'],
            tools=[ImageAnalysisTool()]
            )
    @task
    def download_images(self) -> Task:
        """download images from url and resize them to blog size"""
        return Task(
            config=self.tasks_config['download_images'],
            tools=[DownloadImageTool()]
            )
    @task
    def upload_images(self) -> Task:
        """upload images to blob storage and get a URI that will be embedded as markdown"""
        return Task(
            config=self.tasks_config['upload_images'],
            tools=[BlobStorageTool()]
            )
    ###the writer
    @task
    def write_article(self) -> Task:
        """write an engaging news article that will be published on my blog"""
        return Task(
            config=self.tasks_config['write_article'],
            output_pydantic=DraftArticle
           )
    @task
    def review_article(self) -> Task:
        """review the article you have written with correct URIs and ensure context completeness"""
        return Task(
            config=self.tasks_config['review_article'],
            output_pydantic=DraftArticle
            )
    @task
    def format_input(self) -> Task:
        """review article fields to conform to model requirements"""
        return Task(
            config=self.tasks_config['format_input'],
            output_pydantic=FinalArticle
           )
    @task
    def publish_article(self) -> Task:
        """publish article to neo4j database"""
        return Task(
            config=self.tasks_config['publish_article'],
            tools=[Neo4jArticleTool()]
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