from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task, LLM
import os
from dotenv import load_dotenv
from src.my_journalistic_crew.tools.serper_dev_tool import SerperDevTool
from src.my_journalistic_crew.tools.read_website_content import ScrapeWebsite
from src.my_journalistic_crew.tools.analyse_image import ImageAnalysisTool
from src.my_journalistic_crew.tools.download_image import DownloadImageTool
from src.my_journalistic_crew.tools.send_image_blob import BlobStorageTool
from src.my_journalistic_crew.models.outputs import GoogleImageResults, DraftArticle

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
            function_calling_llm=None,
            memory=True,
            verbose=False,
            allow_delegation=False,
            max_iter=20,
            max_rpm=None,
            max_execution_time=None,
            max_retry_limit=2,
            allow_code_execution=False,
            code_execution_mode="safe",
            respect_context_window=True,
            use_system_prompt=True,
            tools=[],
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
            function_calling_llm=None,
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
            tools=[],
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
          output_file="z_output/research_task_output.json",
          tools=[SerperDevTool()]
       )
    
    @task
    def image_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['image_search_task'],
            output_pydantic=GoogleImageResults,
            output_file="z_output/image_search_task_output.json",
            tools=[SerperDevTool()]
        )
    
    @task
    def image_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['image_analysis'],
            output_file="z_output/image_analysis_output.json",
            tools=[ImageAnalysisTool()]
        )
    
    @task
    def image_download_task(self) -> Task:
        return Task(
            config=self.tasks_config['image_download_task'],
            output_file="z_output/image_download_task_output.json",
            tools=[DownloadImageTool()]
        )
    
    @task
    def push_image_to_blob(self) -> Task:
        return Task(
            config=self.tasks_config['push_image_to_blob'],
            output_file="z_output/push_image_to_blob_output.json",
            tools=[BlobStorageTool()]
        )
    
    @task
    def scrape_website_task(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_website_task'],
            output_file="z_output/scrape_website_task_output.json",
            tools=[ScrapeWebsite()]
         )
    
    @task
    def reporting_task(self) -> Task:
       return Task(
          config=self.tasks_config['reporting_task'],
          output_pydantic=DraftArticle,
          output_file="z_output/reporting_task_output.json"
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