from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

adesso_llm = LLM(
    model="openai/qwen-3.5-122b-sovereign",
    base_url=os.getenv("ADESSO_BASE_URL"),
    api_key=os.getenv("ADESSO_SOVEREIGN_AI_HUB_KEY"),
)

# adesso_embedder = {
#     "provider": "openai",
#     "config": {
#         "model": "qwen-3-vl-embedding-2b-sovereign",
#         "api_key": os.getenv("ADESSO_SOVEREIGN_AI_HUB_KEY"),
#         "api_base": os.getenv("ADESSO_BASE_URL"),
#     },
# }


adesso_premium_llm = LLM(
    model="openai/claude-haiku-4-5",
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
class Coder():
    """Coder crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # One click install for Docker Desktop:
    #https://docs.docker.com/desktop/

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'],
            llm=vultr_llm,
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",  # Uses Docker for safety
            max_execution_time=30, 
            max_retry_limit=3 
    )


    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'],
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Coder crew"""


        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
