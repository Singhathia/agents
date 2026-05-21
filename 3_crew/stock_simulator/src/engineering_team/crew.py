from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, Union

import litellm


load_dotenv()

# Helps with providers that reject unsupported params like stop / stopSequences.
litellm.drop_params = True


COMMON_LLM_KWARGS = {
    "timeout": 120,
    "request_timeout": 120,
    "num_retries": 1,
    "drop_params": True,
    "additional_drop_params": ["stop"],
}


def make_llm(model: str, base_url_env: str, api_key_env: str) -> LLM:
    """Create a CrewAI LLM from environment variable names."""
    return LLM(
        model=model,
        base_url=os.getenv(base_url_env),
        api_key=os.getenv(api_key_env),
        **COMMON_LLM_KWARGS,
    )


# ---------------------------------------------------------------------
# Individual models
# ---------------------------------------------------------------------

adesso_llm = make_llm(
    model="openai/qwen-3.5-122b-sovereign",
    base_url_env="ADESSO_BASE_URL",
    api_key_env="ADESSO_SOVEREIGN_AI_HUB_KEY",
)

adesso_premium_llm = make_llm(
    model="openai/claude-haiku-4-5",
    base_url_env="ADESSO_BASE_URL",
    api_key_env="ADESSO_API_KEY",
)

adesso_coder_llm = make_llm(
    model="openai/qwen3-coder-480b",
    base_url_env="ADESSO_BASE_URL",
    api_key_env="ADESSO_API_KEY",
)

vultr_llm = make_llm(
    model="openai/nvidia/DeepSeek-V3.2-NVFP4",
    base_url_env="VULTR_BASE_URL",
    api_key_env="VULTR_API_KEY",
)

vultr_premium_llm = make_llm(
    model="openai/zai-org/GLM-5.1-FP8",
    base_url_env="VULTR_BASE_URL",
    api_key_env="VULTR_API_KEY",
)

cerebras_llm = make_llm(
    model="openai/zai-glm-4.7",
    base_url_env="CEREBRAS_BASE_URL",
    api_key_env="CEREBRAS_API_KEY",
)

groq_llm = make_llm(
    model="openai/llama-3.3-70b-versatile",
    base_url_env="GROQ_BASE_URL",
    api_key_env="GROQ_API_KEY",
)


# ---------------------------------------------------------------------
# Simple in-code fallback LLM
# ---------------------------------------------------------------------

class SimpleFallbackLLM(LLM):
    """
    Simple fallback wrapper for CrewAI.

    It tries each LLM in order.
    If one fails, it prints the error and tries the next one.
    """

    def __init__(self, name: str, llms: List[LLM]):
        super().__init__(
            model=name,
            timeout=120,
            request_timeout=120,
            num_retries=0,
            drop_params=True,
            additional_drop_params=["stop"],
        )
        self.llms = llms

    def call(
        self,
        messages: Union[str, List[Dict[str, str]]],
        tools: Optional[List[dict]] = None,
        callbacks: Optional[List[Any]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Union[str, Any]:
        errors = []

        for llm in self.llms:
            model_name = getattr(llm, "model", "unknown-model")

            try:
                print(f"\nTrying LLM: {model_name}")

                call_kwargs = {
                    "messages": messages,
                }

                if tools is not None:
                    call_kwargs["tools"] = tools

                if callbacks is not None:
                    call_kwargs["callbacks"] = callbacks

                if available_functions is not None:
                    call_kwargs["available_functions"] = available_functions

                return llm.call(**call_kwargs)

            except Exception as e:
                error_message = f"{model_name} failed: {type(e).__name__}: {e}"
                print(error_message)
                errors.append(error_message)

        raise RuntimeError(
            "All fallback LLMs failed:\n\n" + "\n\n".join(errors)
        )

    def supports_function_calling(self) -> bool:
        return True

    def get_context_window_size(self) -> int:
        return 128000


# ---------------------------------------------------------------------
# Fallback groups
# ---------------------------------------------------------------------

lead_llm = SimpleFallbackLLM(
    name="lead-fallback-llm",
    llms=[
        adesso_premium_llm,
        adesso_llm,
        cerebras_llm,
        groq_llm,
    ],
)

coder_llm = SimpleFallbackLLM(
    name="coder-fallback-llm",
    llms=[
        adesso_coder_llm,
        vultr_llm,
        cerebras_llm,
        groq_llm,
    ],
)

validation_llm = SimpleFallbackLLM(
    name="validation-fallback-llm",
    llms=[
        adesso_coder_llm,
        vultr_llm,
        cerebras_llm,
        groq_llm,
        adesso_llm,
    ],
)


@CrewBase
class EngineeringTeam:
    """EngineeringTeam crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config["engineering_lead"],
            llm=lead_llm,
            verbose=True,
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["backend_engineer"],
            llm=coder_llm,
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=500,
            max_retry_limit=3,
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["frontend_engineer"],
            llm=coder_llm,
            verbose=True,
            max_retry_limit=3,
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["test_engineer"],
            llm=coder_llm,
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=500,
            max_retry_limit=3,
        )

    @agent
    def validation_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["validation_engineer"],
            llm=validation_llm,
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=500,
            max_retry_limit=3,
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config["design_task"],
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_task"],
        )

    @task
    def backend_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["backend_validation_task"],
        )

    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config["frontend_task"],
        )

    @task
    def frontend_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["frontend_validation_task"],
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_task"],
        )

    @task
    def test_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_validation_task"],
        )

    @task
    def final_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["final_validation_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the engineering team crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )