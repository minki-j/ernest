def messages_to_string(messages):
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

def messages_to_chatPromptTemplate(messages):
    result = []
    for msg in messages:
        result.append((msg["role"], msg["content"]))
    return result
