# src/financial_researcher/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

adesso_llm = LLM(
    model="openai/gpt-oss-120b-sovereign",
    base_url=os.getenv("ADESSO_BASE_URL"),
    api_key=os.getenv("ADESSO_SOVEREIGN_AI_HUB_KEY"),
)

adesso_premium_llm = LLM(
    model="openai/gpt-4.1-mini",
    base_url=os.getenv("ADESSO_BASE_URL"),
    api_key=os.getenv("ADESSO_API_KEY"),
)

vultr_llm = LLM(
    model="openai/nvidia/DeepSeek-V3.2-NVFP4",
    base_url=os.getenv("VULTR_BASE_URL"),
    api_key=os.getenv("VULTR_API_KEY"),
)

vultr_premium_llm = LLM(
    model="openai/zai-org/GLM-5.1-FP8",
    base_url=os.getenv("VULTR_BASE_URL"),
    api_key=os.getenv("VULTR_API_KEY"),
)

cerebras_llm = LLM(
    model="openai/zai-glm-4.7",
    base_url=os.getenv("CEREBRAS_BASE_URL"),
    api_key=os.getenv("CEREBRAS_API_KEY"),
)

groq_llm = LLM(
    model="openai/llama-3.3-70b-versatile",
    base_url=os.getenv("GROQ_BASE_URL"),
    api_key=os.getenv("GROQ_API_KEY"),
)

@CrewBase
class ResearchCrew():
    """Research crew for comprehensive topic analysis and reporting"""

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            llm=vultr_llm,
            verbose=True,
            tools=[SerperDevTool()]
            
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'],
            llm=cerebras_llm,
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task']
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            output_file='output/report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )