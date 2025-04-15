from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task, LLM
import os
from dotenv import load_dotenv
from src.my_journalistic_crew.tools.serper_dev_tool import SerperDevTool
from src.my_journalistic_crew.tools.scrape_website import ScrapeWebsite
from src.my_journalistic_crew.tools.twitter_search_tool import TwitterSearchTool
from src.my_journalistic_crew.tools.analyse_image import ImageAnalysisTool
from src.my_journalistic_crew.tools.download_image import DownloadImageTool
from src.my_journalistic_crew.tools.download_thumbnail import DownloadThumbnailTool
from my_journalistic_crew.tools.blob_storage_tool import BlobStorageTool
from my_journalistic_crew.tools.push_article_DB import Neo4jArticleTool
from src.my_journalistic_crew.models.outputs import DraftArticle, FinalArticle, CombinedBatchSearchResults, CombinedScrapingResults, ImageProcessingResults

load_dotenv()
llm = LLM(model=os.getenv("MODEL"), api_key=os.getenv("NVIDIA_API_KEY"),base_url="https://integrate.api.nvidia.com/v1",telemetry=False)
@CrewBase
class MyJournalisticCrew():
    """Journalist crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            llm=llm,
            function_calling_llm=llm,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=40,
            max_rpm=None,
            max_execution_time=None,
            max_retry_limit=2,
            allow_code_execution=False,
            code_execution_mode="safe",
            respect_context_window=True,
            use_system_prompt=True,
            tools=[SerperDevTool(),TwitterSearchTool()],
            knowledge_sources=None,
            embedder=None,
            system_template=None,
            prompt_template=None,
            response_template=None,
            step_callback=None
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            llm=llm,
            function_calling_llm=llm,
            memory=True,
            verbose=True,
            allow_delegation=False,
            max_iter=20,
            max_rpm=None,
            max_execution_time=None,
            max_retry_limit=2,
            allow_code_execution=False,
            code_execution_mode="safe",
            respect_context_window=True,
            use_system_prompt=True,
            tools=[ScrapeWebsite(), ImageAnalysisTool(), DownloadImageTool(), DownloadThumbnailTool(), BlobStorageTool(), Neo4jArticleTool()],
            knowledge_sources=None,
            embedder=None,
            system_template=None,
            prompt_template=None,
            response_template=None,
            step_callback=None
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            output_pydantic=DraftArticle,
            output_file="z_output/11_research_task.json",
            tools=[SerperDevTool(), TwitterSearchTool()]
        )
    
    @task
    def image_functions(self) -> Task:
        return Task(
            config=self.tasks_config['image_functions'],
            output_pydantic=ImageProcessingResults,
            tools=[DownloadImageTool(), DownloadThumbnailTool(), BlobStorageTool()],
            output_file="z_output/13_image_functions_task.json"
        )
    
    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_pydantic=FinalArticle,
            output_file="z_output/14_reporting_task.json",
            tools=[ScrapeWebsite(), ImageAnalysisTool(), Neo4jArticleTool()]
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