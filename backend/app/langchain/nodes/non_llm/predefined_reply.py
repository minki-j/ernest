from app.langchain.schema import Documents


def generate_last_msg(state: dict[str, Documents]):
    print("\n==>> end_conversation")
    documents = state["documents"]

    documents.state.reply_message = f" The interview session has ended. Thank you for your time {documents.user.name}. You can check the result in the <review> tab. Have a great day! 😊"

    return {"documents": documents}


def ask_user_name(state: dict[str, Documents]):
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

def ask_vendor_info(state: dict[str, Documents]):
    print("\n==>> ask_vendor_info")
    documents = state["documents"]
    user_name = documents.user.name

    # documents.state.ui_type = "pick_vendor"
    documents.state.reply_message = f"Hi {user_name}! Before begin the interview, could you let me know which company or tool you are going to talk about?"

    return {"documents": documents}


def introduction(state: dict[str, Documents]):
    print("\n==>> introduction")
    documents = state["documents"]
    user_name = documents.user.name
    vendor_name = documents.vendor.name

    documents.state.reply_message = f"Hi {user_name}! Thanks for sharing your valuable time and insight on {vendor_name} today. The interview would take roughly 10 mins. There are 5 pre-defined topics I would like to discuss with you regarding your experience with {vendor_name}. If you want to move on to the next topic at any point, just reply \"pass\". Are you ready to begin?"

    return {"documents": documents}
