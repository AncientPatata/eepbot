import asyncio
import json
import random

import discord

from collections import defaultdict, deque
from mistralai import Mistral


sleep_id = 271663747045523456
general_channel_id = 1286378341066215496
tom_user_id = 1073726088959758418

with open("./config.json", "r") as conf_file_handle:
    config = json.load(conf_file_handle)


message_history = defaultdict(lambda: deque(maxlen=config["HistoryLength"]))


model = "mistral-large-latest"

mistral_client = Mistral(api_key=config["MistralApiToken"])


with open("sleepy_chan_prompt.txt") as sys_prompt_file_handle:
    system_prompt = sys_prompt_file_handle.read()
    print(f"Started bot with system prompt:\n{system_prompt}")


def build_condensed_message_list(history, bot_id):
    """
    Given a list of messages (dicts) and the bot's ID,
    merge consecutive bot messages into one (joined with \n\n),
    and remove leading 'me: ' from the assistant's content.
    """
    condensed = []
    for msg in history:
        if msg["author"] == bot_id:
            role = "assistant"
            # We'll start with the original content.
            content = msg["content"]
            # If it starts with 'me: ', remove it.
            if content.startswith("me: "):
                content = content[4:]
        else:
            role = "user"
            # For user messages, you may still want to prefix with the user's name:
            content = f"{msg['author_name']}: {msg['content']}"
        
        # If this message is from the assistant and the previous message
        # in condensed is also assistant, just append it with \n\n:
        if role == "assistant" and condensed and condensed[-1]["role"] == "assistant":
            condensed[-1]["content"] += f"\n\n{content}"
        else:
            condensed.append({"role": role, "content": content})

    return condensed

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    # async def on_message(self, message):
    #     print(f'Message from {message.author}: {message.content}')

    async def on_member_join(self, member):
        sleep_user = await self.fetch_user(sleep_id)
        general_channel = await self.fetch_channel(general_channel_id)
        if general_channel is not None:
            to_send = f'HELLO {member.mention} !!! <a:dankies:1335359329431191595> {sleep_user.mention} <a:dankies:1335359329431191595>'
            await general_channel.send(to_send)



    async def on_message(self, message):
        # we do not want the bot to reply to itself

        message_history[message.guild.id].append({"author": message.author.id, "content": message.content, "author_name": message.author.display_name})
        # print(f"message_history:\n{json.dumps(message_history,indent=4)}\n----")
        if message.author.id == self.user.id:
            return
        
        # if self.user.mentioned_in(message) and message.author.id == tom_user_id:
        #     async with message.channel.typing():
        #         # simulate something heavy
        #         await asyncio.sleep(3)
        #     await asyncio.sleep(2)
        #     async with message.channel.typing():
        #         # simulate something heavy
        #         await asyncio.sleep(2)
        #     await message.reply("<:stare_worry_bruh:1321230481563582516> Hey it's me again...i just wanted...Can we talk? i've been watching you, why would u say that? [Redacted]", mention_author=True)
        #     return 

        message_list = [{"role": "assistant" if msg["author"]==self.user.id else "user", "content": (f"{msg['author_name']}: " if msg["author"] != self.user.id else "me: ") + msg["content"]} for msg in message_history[message.guild.id]]
        if self.user.mentioned_in(message):
            async with message.channel.typing():
                response = mistral_client.chat.complete(
                    model= model,
                    messages = [
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                    ] + message_list
                )
        else: 
            return
        messages_to_send = response.choices[0].message.content.split("\n\n")
        print(f"response :\n{response.choices[0].message}")
        typing_speed = 0.01  # Adjust this value to control the typing speed

        # Simulate typing and send messages one by one
        for word in messages_to_send:
            async with message.channel.typing():
                # Typing duration based on word length and typing speed
                typing_duration = len(word) * typing_speed

                typing_duration += random.uniform(0, 1)

                await asyncio.sleep(typing_duration)

                await message.channel.send(word)
            await asyncio.sleep(random.uniform(0,1))


intents = discord.Intents.default()
intents.message_content = True


client = MyClient(intents=intents)
client.run(config["BotToken"])

# <a:dankies:1335359329431191595>
# <:stare_worry_bruh:1321230481563582516>