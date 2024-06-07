from app.schemas.schemas import Message, Bio


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


def messages_to_string(
    messages: list[Message], ai_role: str = "ai", user_role: str = "user"
):
    return ", ".join([f"{ai_role+" asked" if msg.role.value == "assistant" else user_role + " replied"} <{msg.content}>" for msg in messages])

def bios_to_string(
        bios: list[Bio]
):
    return ", ".join([bio.title + ": " + bio.content for bio in bios])