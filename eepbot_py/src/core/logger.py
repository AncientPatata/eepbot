import seqlog
import logging
import discord

# TODO: 
seqlog.log_to_seq(
    server_url="http://seq:5341",  # This matches the container name in the Docker network
    level=logging.INFO,
    batch_size=10,
    auto_flush_timeout=1,  # Flush every second
)

logger = logging.getLogger('eepbot')
logger.setLevel(logging.DEBUG)  # Set the desired level for your bot's logs

# Configure the discord logger
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.DEBUG)  # Capture debug level logs for discord
logging.getLogger('discord.http').setLevel(logging.INFO)  # Less verbose for HTTP logs

# Add the Seq handler to the discord logger
for handler in logging.getLogger().handlers:
    discord_logger.addHandler(handler)

# If you want the discord logger to propagate logs up to the root logger (good for uniform logging):
discord_logger.propagate = True

# # Setup logging using discord's utility, but disable its default handler to avoid duplication
# discord.utils.setup_logging(level=logging.DEBUG, root=False)
