from typing import List
from mistralai import Mistral
import requests
from core.config import Config
from core.logger import logger
from openai import OpenAI
import boto3
from PIL import Image
from io import BytesIO

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
                condensed[-1]["content"] += f"<SPLIT>{content}"
            else:
                condensed.append({"role": role, "content": content})

        return condensed


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

    def is_valid_image_url(self, url: str, timeout: int = 3) -> bool:
        """
        Tries a HEAD request on the image URL to ensure it is reachable (status_code == 200).
        """
        if not url:
            return False
        try:
            r = requests.head(url, timeout=timeout)
            return r.status_code == 200
        except Exception:
            return False

    def resize_image(self, image_bytes: bytes, max_size=(1000, 1000)) -> bytes:
        """
        Resize the image to fit within max_size (width, height),
        re-encode as PNG, and return the resulting bytes.
        """
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                # Convert to RGB to avoid issues if the image has a palette or alpha
                img = img.convert("RGB")
                img.thumbnail(max_size)  # This will maintain aspect ratio.

                # Re-encode to PNG (or JPEG if you prefer) 
                buf = BytesIO()
                img.save(buf, format="PNG", optimize=True)
                return buf.getvalue()
        except Exception as e:
            logger.warning(f"Error resizing image: {e}")
            #return b''
            raise e

    def build_condensed_message_list(self, history, bot_id) -> List[dict]:
            """
            Builds a Bedrock-style conversation list but only includes the last N images.
            
            :param history: List of message dicts containing:
                {
                    "author": <discord_id_of_sender>,
                    "author_name": <user's display name>,
                    "content": <text>,
                    "image": <optional image URL>
                }
            :param bot_id: The ID of the bot, so we know which messages are from the assistant.
            :return: A Bedrock-style list of messages, each with a "role" and "content" list.
            """

            # 1) Identify all messages that contain an image
            all_img_indices = [
                i for i, msg in enumerate(history)
                if "image" in msg and msg["image"]
            ]

            # 2) Keep only the last N of these messages
            keep_img_indices = set(all_img_indices[-self.config.llm_config.max_images_in_history:])

            condensed = []
            for i, msg in enumerate(history):
                # figure out the role
                if msg["author"] == bot_id:
                    role = "assistant"
                    content_str = msg["content"]
                    # If it starts with 'me: ', remove it
                    if content_str.startswith("me: "):
                        content_str = content_str[4:]
                else:
                    role = "user"
                    content_str = f"{msg['author_name']}: {msg['content']}"

                # Build the initial content for this new message
                new_content_list = []
                if content_str:
                    new_content_list.append({"text": content_str})

                # 3) If this message is in keep_img_indices, attach the image
                #    (otherwise skip image to keep only the last N)
                if i in keep_img_indices:
                    logger.info(f"Found an image in msg idx={i} with url: {msg['image']}")
                    if self.is_valid_image_url(msg["image"]):
                        try:
                            # Download the image bytes
                            response = requests.get(msg["image"], timeout=5)
                            response.raise_for_status()
                            image_bytes = response.content

                            # Resize & re-encode the image
                            resized_image_bytes = self.resize_image(image_bytes)
                            if resized_image_bytes:  # only if we have a valid, <5MB image
                                new_content_list.append({
                                    "image": {
                                        "format": "png",
                                        "source": {"bytes": resized_image_bytes}
                                    }
                                })
                        except Exception as e:
                            logger.warning(f"Could not retrieve/resize image from {msg['image']}: {e}")

                # 4) Merging logic: If the last message is the same role, extend its content
                if condensed and condensed[-1]["role"] == role:
                    condensed[-1]["content"].extend(new_content_list)
                else:
                    condensed.append({"role": role, "content": new_content_list})

            return condensed

    def get_response(self, message_list: List[dict]) -> str:
        # adjust message list : 
        # new_message_list = []
        # for msg in message_list:
        #     new_message_list.append({"role": msg["role"], "content":[{"text": msg["content"]}]})
        logger.info("Asking LLM to generate response.")
        response = self.bedrock_client.converse(
            modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            messages=message_list,
            system=[{"text":self.system_prompt}],
            inferenceConfig={"maxTokens":512}
        )
        
        raw_text = response["output"]["message"]["content"][0]["text"]

        logger.info(f"LLM generated response (Bedrock): {raw_text}")
        return raw_text
