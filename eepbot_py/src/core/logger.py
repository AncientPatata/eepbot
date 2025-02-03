import seqlog
import logging

# TODO: 
seqlog.log_to_seq(
    server_url="http://seq:5341",  # This matches the container name in the Docker network
    level=logging.INFO,
    batch_size=10,
    auto_flush_timeout=1,  # Flush every second
)

logger = logging.getLogger(__name__)