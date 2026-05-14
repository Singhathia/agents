import os
from dotenv import load_dotenv

load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


MODEL_ROUTER = {
    "default": required_env("DEFAULT_MODEL"),
    "large_context": required_env("LARGE_CONTEXT_MODEL"),
    "reasoning": required_env("REASONING_MODEL"),

    "coding": required_env("CODING_MODEL"),
    "cheap_agent": required_env("CHEAP_AGENT_MODEL"),
    "general": required_env("GENERAL_MODEL"),
    "hard": required_env("HARD_MODEL"),
    "escalation": required_env("ESCALATION_MODEL"),

    "claude_fast": required_env("FAST_CLAUDE_MODEL"),
    "claude_quality": required_env("QUALITY_CLAUDE_MODEL"),

    "backup": required_env("BACKUP_MODEL"),
    "cheap_backup": required_env("CHEAP_BACKUP_MODEL"),

    "local_coding": required_env("LOCAL_CODING_MODEL"),
    "local_fast": required_env("LOCAL_FAST_MODEL"),
    "local_reasoning": required_env("LOCAL_REASONING_MODEL"),
}


def get_model(model_type: str = "default") -> str:
    return MODEL_ROUTER.get(model_type, MODEL_ROUTER["default"])