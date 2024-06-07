from app.langchain.schema import Documents


def generate_last_msg(state: dict[str, Documents]):
    print("\n==>> end_conversation")
    documents = state["documents"]

    documents.state.reply_message = f" The interview session has ended. Thank you for your time {documents.user.name}. You can check the result in the <review> tab. Have a great day! 😊"

    return {"documents": documents}


def ask_name(state: dict[str, Documents]):
    print("\n==>> ask_name")
    documents = state["documents"]

    message = "Hi I'm Ernest! What's your name?"

    documents.state.reply_message = message

    return {"documents": documents}


def greeting(state: dict[str, Documents]):
    print("\n==>> greeting")
    documents = state["documents"]

    first_msg_from_ai = f"Hi {documents.user.name}! What's up?"

    documents.state.reply_message = first_msg_from_ai

    return {"documents": documents}

def reply_for_incomplete_msg(state: dict[str, Documents]):
    print("\n==>> reply_for_incomplete_msg")
    documents = state["documents"]

    message = "Oops, it looks like your message got cut off ✂️"

    documents.state.reply_message = message

    return {"documents": documents}
