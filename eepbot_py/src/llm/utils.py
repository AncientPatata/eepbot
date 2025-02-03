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
