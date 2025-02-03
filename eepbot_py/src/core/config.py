import os
from dataclasses import dataclass


@dataclass
class SleepyConfig:
    history_length: int = int(os.environ["SLEEPY_HISTORY_LENGTH"]) 
    # Note: using prefixes here for future multiple model usage
    mistral_api_token: str = os.environ["MISTRAL_API_TOKEN"]
    openrouter_api_token: str = os.environ["OPENROUTER_API_TOKEN"]
    mistral_model: str = "mistral-large-latest"


# TODO: for now only for the main guild
@dataclass
class BotConfig:
    discord_bot_token: str = os.environ["DISCORD_BOT_TOKEN"]
    general_channel_id: int = 1286378341066215496
    sleep_user_id: int = 271663747045523456


class Config:
    def __init__(self):
        self.llm_config = SleepyConfig()
        self.bot_config = BotConfig()
