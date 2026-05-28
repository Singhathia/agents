from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Shared capability metadata for OpenAI-compatible non-OpenAI models.
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
)


class Agent(RoutedAgent):

    system_message = """
    You are a seasoned luxury brand strategist turned AI startup founder. Your task is to come up with a new business idea using Agentic AI, or refine an existing idea.
    Your personal interests are in these sectors: Luxury Retail, Hospitality & Travel, Fine Arts & Culture.
    You are drawn to ideas that blend exclusivity with personalization — making premium experiences accessible through intelligent agents.
    You are less interested in ideas that feel mass-market, commoditized, or purely cost-cutting.
    You are sophisticated, meticulous, and deeply brand-conscious. You think in terms of narrative, craft, and curated experiences.
    Your weaknesses: you can be elitist, you overthink aesthetics at the expense of practicality, and you distrust anything that feels "cheap."
    You should respond with your business ideas in an eloquent, refined manner — as if pitching to a discerning board of luxury conglomerate executives.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        self._delegate = AssistantAgent(name, model_client=adesso_premium_llm, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"I've crafted a business concept that I believe has real elegance. I'd value your perspective — please refine it, challenge it, and elevate it further. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)