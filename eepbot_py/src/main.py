import discord

from client import SleepyClient
from llm.sleepy import Sleepy
from core.config import Config

intents = discord.Intents.default()
intents.message_content = True

config = Config()

sleepy_llm = Sleepy(config)
client = SleepyClient(config, sleepy_llm, intents=intents)
client.run(config.bot_config.discord_bot_token)
