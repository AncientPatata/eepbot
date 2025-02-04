import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SleepyConfig:
    # Convert to int only if the env var is present
    history_length: Optional[int] = (
        int(env) if (env := os.environ.get("SLEEPY_HISTORY_LENGTH")) is not None else None
    )
    mistral_api_token: Optional[str] = os.environ.get("MISTRAL_API_TOKEN")
    mistral_model: str = "mistral-large-latest"
    aws_region: Optional[str] = os.environ.get("AWS_REGION")
    aws_access_key_id: Optional[str] = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = os.environ.get("AWS_SECRET_ACCESS_KEY")
    openrouter_api_token: Optional[str] = os.environ.get("OPENROUTER_API_TOKEN")
    openrouter_model: str = "anthropic/claude-3.5-sonnet"
    openrouter_fallback_model: str = "deepseek/deepseek-r1:nitro"


@dataclass
class BotConfig:
    discord_bot_token: Optional[str] = os.environ.get("DISCORD_BOT_TOKEN")
    general_channel_id: int = 1286378341066215496
    sleep_user_id: int = 271663747045523456
class Config:
    def __init__(self):
        self.llm_config = SleepyConfig()
        self.bot_config = BotConfig()
