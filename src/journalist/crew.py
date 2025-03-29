from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from journalist.tools.twitter_scraper import TwitterScraper
from journalist.tools.pygooglenews import GoogleNewsTool
from journalist.tools.url_scraper import URLScraper
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
    def political_news_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['political_news_reporter'],
            llm=llm,
            tools=[TwitterScraper(), GoogleNewsTool(), URLScraper()],
            verbose=True,
            cache=False
        )
    @agent
    def business_news_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['business_news_reporter'],
            llm=llm,
            tools=[TwitterScraper(), GoogleNewsTool(), URLScraper()],
            verbose=True,
            cache=False
        )
    @agent
    def sports_news_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['sports_news_reporter'],
            llm=llm,
            tools=[TwitterScraper(), GoogleNewsTool(), URLScraper()],
            verbose=True,
            cache=False
        )
    
###tasks###
    @task
    def political_news_reporter_task(self) -> Task:
        return Task(
            config=self.tasks_config['political_news_reporter_task'],
        )
    @task
    def business_news_reporter_task(self) -> Task:
        return Task(
            config=self.tasks_config['business_news_reporter_task'],
        )
    @task
    def sports_news_reporter_task(self) -> Task:
        return Task(
            config=self.tasks_config['sports_news_reporter_task'],
        )

 

    def chief_editor(self) -> Agent:
        return Agent(
            role="Chief Editor",
            goal="Assign tasks to the journalists based on the category of the topic and review their work.",
            backstory="You're a meticulous senior editor with a keen eye for detail. You're known for your ability to review news articles and make sure they are accurate and meet our standards.",
            allow_delegation=True,
            llm=llm,
            verbose=True,
            cache=False
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
            cache=False
        )
