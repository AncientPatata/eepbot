from typing import List
from mistralai import Mistral
from core.config import Config
from core.logger import logger
from openai import OpenAI


class Sleepy:
    def __init__(self, config: Config):
        self.mistral_client = Mistral(api_key=config.llm_config.mistral_api_token)
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.llm_config.openrouter_api_token,
        )

        self.config = config
        with open("sleepy_chan_prompt.txt") as sys_prompt_file_handle:
            self.system_prompt = sys_prompt_file_handle.read()
            # print(f"Started bot with system prompt:\n{system_prompt}")

    def get_response(self, message_list: List[dict]) -> List[str]:
        # response = self.mistral_client.chat.complete(
        #     model=self.config.llm_config.mistral_model,
        #     messages=[
        #         {"role": "system", "content": self.system_prompt},
        #     ]
        #     + message_list,
        # )
        response = self.openai_client.chat.completions.create(
            model="anthropic/claude-3.5-sonnet",
            messages=[
                {"role": "system", "content": self.system_prompt},
            ]
            + message_list,
            extra_body={
                "models":["deepseek/deepseek-r1:nitro"]
            }
        )
        raw_text = response.choices[0].message.content
        logger.info(f"LLM generated response: {raw_text}")
        return raw_text


            # model:"anthropic/claude-3.5-sonnet",
            # models:["deepseek/deepseek-r1:nitro"],