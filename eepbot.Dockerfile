FROM python:3.10-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY ./eepbot_py/src ./src
COPY ./eepbot_py/pyproject.toml .
COPY ./eepbot_py/uv.lock .
# TODO: Temporary (switch to docker secrets later and pass shit via env)
COPY ./eepbot_py/config.json . 
# TODO: does uv need this ? 
# COPY ./eepbot_py/.python-version . 
COPY ./eepbot_py/sleepy_chan_prompt.txt .


CMD [ "uv", "run", "python", "src/main.py" ]