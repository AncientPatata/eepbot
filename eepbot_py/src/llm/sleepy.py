from typing import List
from mistralai import Mistral
from core.config import Config
from core.logger import logger
from openai import OpenAI
import boto3

class BaseSleepy:
    """
    A base class providing common functionality (e.g., reading the system prompt).
    Subclasses must implement `get_response(...)`.
    """

    def __init__(self, config: Config):
        self.config = config
        with open("sleepy_chan_prompt.txt", "r", encoding="utf-8") as sys_prompt_file_handle:
            self.system_prompt = sys_prompt_file_handle.read()

    def get_response(self, message_list: List[dict]) -> str:
        """
        Subclasses should implement their own logic to call the respective LLM.
        """
        raise NotImplementedError("Subclasses must implement `get_response`.")



class MistralSleepy(BaseSleepy):
    """
    Uses the Mistral client to generate responses.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        # Initialize the Mistral client
        self.mistral_client = Mistral(api_key=config.llm_config.mistral_api_token)


    def get_response(self, message_list: List[dict]) -> str:

        response = self.mistral_client.chat.complete(
            model=self.config.llm_config.mistral_model,
            messages=[{"role": "system", "content": self.system_prompt}] + message_list,
        )
        
        raw_text = response.choices[0].message.content
        logger.info(f"LLM generated response (Mistral): {raw_text}")
        return raw_text


class OpenRouterSleepy(BaseSleepy):
    """
    Uses the OpenRouter (OpenAI-like) client to generate responses.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        # Initialize the OpenRouter/OpenAI client
        self.openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.llm_config.openrouter_api_token,
        )

    def get_response(self, message_list: List[dict]) -> str:
        response = self.openai_client.chat.completions.create(
            model=self.config.llm_config.openrouter_model,
            messages=[{"role": "system", "content": self.system_prompt}] + message_list,
            extra_body={"models": [self.config.llm_config.openrouter_fallback_model]},
        )
        
        raw_text = response.choices[0].message.content

        logger.info(f"LLM generated response (OpenRouter): {raw_text}")
        return raw_text


class BedrockSleepy(BaseSleepy):
    """
    Uses the AWS Bedrock client to generate responses.
    """

    def __init__(self, config: Config):
        super().__init__(config)
        # Initialize the Boto3 AWS Client
        self.bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=config.llm_config.aws_region,
            aws_access_key_id=config.llm_config.aws_access_key_id,
            aws_secret_access_key=config.llm_config.aws_secret_access_key,
        )

    def get_response(self, message_list: List[dict]) -> str:
        # adjust message list : 
        new_message_list = []
        for msg in message_list:
            new_message_list.append({"role": msg["role"], "content":[{"text": msg["content"]}]})
        response = self.bedrock_client.converse(
            modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=new_message_list,
            system=[{"text":self.system_prompt}],
            inferenceConfig={"maxTokens":512}
        )
        
        raw_text = response["output"]["message"]["content"][0]["text"]

        logger.info(f"LLM generated response (Bedrock): {raw_text}")
        return raw_text
