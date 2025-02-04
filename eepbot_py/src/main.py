import discord

from client import SleepyClient
from llm.sleepy import OpenRouterSleepy, BedrockSleepy
from core.config import Config

intents = discord.Intents.default()
intents.message_content = True

config = Config()

sleepy_llm = BedrockSleepy(config)
client = SleepyClient(config, sleepy_llm, intents=intents)
client.run(config.bot_config.discord_bot_token, log_handler=None)
