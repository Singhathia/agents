from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

adesso_llm = LLM(
    model="openai/qwen-3.6-35b-sovereign",
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
    model="openai/gpt-oss-120b",
    base_url=os.getenv("CEREBRAS_BASE_URL"),
    api_key=os.getenv("CEREBRAS_API_KEY"),
)


@CrewBase
class Debate():
    """Debate crew"""


    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def debater(self) -> Agent:
        return Agent(
            config=self.agents_config['debater'],
            llm=cerebras_llm,
            verbose=True
        )

    @agent
    def judge(self) -> Agent:
        return Agent(
            config=self.agents_config['judge'],
            llm=cerebras_llm,
            verbose=True
        )

    @task
    def propose(self) -> Task:
        return Task(
            config=self.tasks_config['propose'],
        )

    @task
    def oppose(self) -> Task:
        return Task(
            config=self.tasks_config['oppose'],
        )

    @task
    def decide(self) -> Task:
        return Task(
            config=self.tasks_config['decide'],
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Debate crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
