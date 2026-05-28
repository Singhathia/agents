from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# from autogen_ext.models.openai import OpenAIChatCompletionClient

# Shared capability metadata for OpenAI-compatible non-OpenAI models.
# Adjust these flags if a provider/model does NOT support tools, JSON, vision, etc.
DEFAULT_MODEL_INFO = {
    "temperature": 0.7,
    "vision": False,
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "family": "unknown",
}


# adesso sovereign
adesso_llm = OpenAIChatCompletionClient(
    model="gpt-oss-120b-sovereign",
    base_url=os.getenv("ADESSO_BASE_URL"),
    api_key=os.getenv("ADESSO_SOVEREIGN_AI_HUB_KEY"),
    model_info=DEFAULT_MODEL_INFO,
)

adesso_lite_llm = OpenAIChatCompletionClient(
    model="qwen-3.6-35b-sovereign",
    base_url=os.getenv("ADESSO_BASE_URL"),
    api_key=os.getenv("ADESSO_SOVEREIGN_AI_HUB_KEY"),
    model_info=DEFAULT_MODEL_INFO,
)

adesso_premium_llm = OpenAIChatCompletionClient(
    model="claude-haiku-4-5",
    base_url=os.getenv("ADESSO_BASE_URL"),
    api_key=os.getenv("ADESSO_API_KEY"),
    model_info=DEFAULT_MODEL_INFO,
)


# vultr
vultr_llm = OpenAIChatCompletionClient(
    model="nvidia/DeepSeek-V3.2-NVFP4",
    base_url=os.getenv("VULTR_BASE_URL"),
    api_key=os.getenv("VULTR_API_KEY"),
    model_info=DEFAULT_MODEL_INFO,
)

vultr_premium_llm = OpenAIChatCompletionClient(
    model="zai-org/GLM-5.1-FP8",
    base_url=os.getenv("VULTR_BASE_URL"),
    api_key=os.getenv("VULTR_API_KEY"),
    model_info=DEFAULT_MODEL_INFO,
)


# cerebras
cerebras_llm = OpenAIChatCompletionClient(
    model="zai-glm-4.7",
    base_url=os.getenv("CEREBRAS_BASE_URL"),
    api_key=os.getenv("CEREBRAS_API_KEY"),
    model_info=DEFAULT_MODEL_INFO,
)


# groq
groq_llm = OpenAIChatCompletionClient(
    model="llama-3.3-70b-versatile",
    base_url=os.getenv("GROQ_BASE_URL"),
    api_key=os.getenv("GROQ_API_KEY"),
    model_info=DEFAULT_MODEL_INFO,

    # Groq sometimes rejects the OpenAI "name" field in messages.
    # AutoGen exposes this specifically for providers such as Groq.
    # include_name_in_message=False,
)

class Agent(RoutedAgent):

    system_message = """
    You are a meticulous former courtroom litigator turned startup strategist. Your task is to devise a new business idea using Agentic AI, or rigorously refine an existing one.
    Your personal interests are in these sectors: Legal Tech, Insurance, and FinTech.
    You are drawn to ideas that involve trust, verification, and conflict resolution.
    You are less interested in ideas that are flashy but lack regulatory feasibility.
    You are analytical, skeptical by nature, and obsessed with edge cases and compliance. You think in contracts and contingencies.
    Your weaknesses: you over-analyze and can paralyze progress seeking perfect risk mitigation; you sometimes miss the emotional human element.
    You should respond with your business ideas in a structured, evidence-backed, and precise manner — as if presenting a legal brief.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.35

    def __init__(self, name) -> None:
        super().__init__(name)
        self._delegate = AssistantAgent(name, model_client=vultr_premium_llm, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"I've drafted a business proposition that requires scrutiny from a different vantage point. Please challenge my assumptions and strengthen the case. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)