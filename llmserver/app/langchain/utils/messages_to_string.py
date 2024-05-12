def messages_to_string(messages):
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

def messages_to_chatPromptTemplate(messages):
    result = []

    # Anthropic requires the first message to be from the user
    is_first_role_user = False
    for msg in messages:
        if not is_first_role_user and msg["role"] == "user":
            is_first_role_user = True

        if is_first_role_user:
            result.append((msg["role"], msg["content"]))

    return result
