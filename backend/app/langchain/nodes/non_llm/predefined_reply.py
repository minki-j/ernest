from app.langchain.schema import Documents


def generate_last_msg(state: dict[str, Documents]):
    print("==>> end_conversation")
    documents = state["documents"]

    documents.state.reply_message = "Thank you for your time. Have a great day!"

    return {"documents": documents}


def ask_name(state: dict[str, Documents]):
    print("==>> ask_name")
    documents = state["documents"]

    message = "Hi I'm Ernest! What's your name?"

    documents.state.reply_message = message

    return {"documents": documents}


def greeting(state: dict[str, Documents]):
    print("==>> greeting")
    documents = state["documents"]

    first_msg_from_ai = f"Hi {documents.user.name}! What's up?"

    documents.state.reply_message = first_msg_from_ai

    return {"documents": documents}
