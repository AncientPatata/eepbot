import asyncio
import random
import re

import discord

from collections import defaultdict, deque
from core.config import Config
from core.logger import logger
from llm.sleepy import BaseSleepy
from llm.utils import build_condensed_message_list


class SleepyClient(discord.Client):
    def __init__(self, config: Config, sleepy: BaseSleepy, intents, **options):
        super().__init__(intents=intents, **options)
        self.config = config
        self.llm = sleepy
        self.message_history = defaultdict(
            lambda: deque(maxlen=config.llm_config.history_length)
        )

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    # async def on_message(self, message):
    #     print(f'Message from {message.author}: {message.content}')

    async def on_member_join(self, member):
        sleep_user = await self.fetch_user(self.config.bot_config.sleep_user_id)
        general_channel = await self.fetch_channel(
            self.config.bot_config.general_channel_id
        )
        if general_channel is not None:
            to_send = f"HELLO {member.mention} !!! <a:dankies:1335359329431191595> {sleep_user.mention} If no one is here we can chat until then."
            await general_channel.send(to_send)

    async def on_message(self, message: discord.Message):
        # we do not want the bot to reply to itself

        if not self.message_history:
            async for past_message in message.channel.history(limit=10):
                self.message_history[message.guild.id].append(
                    {
                        "author": past_message.author.id,
                        "content": past_message.content,
                        "author_name": past_message.author.display_name,
                    }
                )
        else:   
            self.message_history[message.guild.id].append(
                {
                    "author": message.author.id,
                    "content": message.content,
                    "author_name": message.author.display_name,
                }
            )

        ## If message was on nsfw channel DO NOT send the images over or even look at them.

        logger.debug(
            f"Logged message in guild {message.guild.id} from {message.author.display_name} with content: {message.content}"
        )
        # TODO: replace this with logs
        # print(f"message_history:\n{json.dumps(message_history,indent=4)}\n----")
        if message.author.id == self.user.id:
            return

        message_list = build_condensed_message_list(
            self.message_history[message.guild.id], self.user.id
        )
        if self.user.mentioned_in(message):
            async with message.channel.typing():
                raw_text = self.llm.get_response(message_list)
        else:
            return
        # Split on <SPLIT> or a blank line (\n\n).
        # \n\s*\n lets you catch "\n\n" and also "\n  \n" just in case of extra spaces
        chunks = re.split(r"<SPLIT>|\n\s*\n", raw_text)

        typing_speed = 0.01  # Adjust this value to control the typing speed

        # Simulate typing and send messages one by one
        for message_to_send in chunks:
            if len(message_to_send) > 0:
                async with message.channel.typing():
                    # Typing duration based on message length and typing speed
                    typing_duration = len(message_to_send) * typing_speed

                    typing_duration += random.uniform(0, 1)

                    await asyncio.sleep(typing_duration)
                    if message_to_send.startswith("me: "):
                        message_to_send = message_to_send[4:]
                    await message.channel.send(message_to_send)
                await asyncio.sleep(random.uniform(0, 1))
