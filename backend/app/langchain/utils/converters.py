from app.schemas.schemas import Message

def to_path_map(node_names):
    dict = {}
    for name in node_names:
        dict[name] = name
    return dict


def to_role_content_tuples(messages: list[Message]):
    result = []

    # Anthropic requires the first message to be from the user
    is_first_role_user = False
    for msg in messages:
        if not is_first_role_user and msg.role.value == "user":
            is_first_role_user = True

        if is_first_role_user:
            result.append((msg.role.value, msg.content))

    return result


def messages_to_string(messages: list[Message]):
    return "\n".join([f"{msg.role.value}: {msg.content}" for msg in messages])
