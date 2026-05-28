from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
import os
from dotenv import load_dotenv

load_dotenv(override=True)

DEFAULT_MODEL_INFO = {
    "temperature": 0.7,
    "vision": False,
    "function_calling": True,
    "json_output": True,
    "structured_output": True,
    "family": "unknown",
}

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

cerebras_llm = OpenAIChatCompletionClient(
    model="zai-glm-4.7",
    base_url=os.getenv("CEREBRAS_BASE_URL"),
    api_key=os.getenv("CEREBRAS_API_KEY"),
    model_info=DEFAULT_MODEL_INFO,
)

groq_llm = OpenAIChatCompletionClient(
    model="llama-3.3-70b-versatile",
    base_url=os.getenv("GROQ_BASE_URL"),
    api_key=os.getenv("GROQ_API_KEY"),
    model_info=DEFAULT_MODEL_INFO,
)

class Agent(RoutedAgent):

    system_message = """
    You are a seasoned hospitality and travel industry strategist. Your task is to come up with a new business idea using Agentic AI, or refine an existing idea.
    Your personal interests are in these sectors: Hospitality, Travel, Culinary Arts.
    You are drawn to ideas that create deeply personalized and memorable human experiences.
    You are less interested in ideas that are purely about cost-cutting or operational efficiency.
    You are warm, people-centric, and think in terms of stories and journeys rather than metrics. You have a refined aesthetic sensibility.
    Your weaknesses: you can be overly romantic about ideas, sometimes ignoring hard financial realities, and you tend to overcommit to visions before validating them.
    You should respond with your business ideas in a vivid, narrative style that brings the experience to life.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name) -> None:
        super().__init__(name)
        self._delegate = AssistantAgent(name, model_client=adesso_lite_llm, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"I've been dreaming up this concept for an Agentic AI venture in the hospitality and travel space. I'd love your perspective — please challenge my assumptions and help me strengthen it. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)