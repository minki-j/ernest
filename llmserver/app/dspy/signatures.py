import os
from typing import List
from app.common import stub
from modal import Image
import dspy
from dsp.utils import deduplicate
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from app.utils.dspy_initialize import initialize_dspy

class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")
    print("Class Initialized: GenerateAnswer")


class GenerateSearchQuery(dspy.Signature):
    """Write a simple search query that will help answer a complex question."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    query = dspy.OutputField()


class GenerateChatReply(dspy.Signature):
    """Generate a reply to a chat message."""

    previous_messages = dspy.InputField(desc="previous chat messages")
    user_info = dspy.InputField(desc="user information")
    message = dspy.InputField()
    reply = dspy.OutputField()


class Chatbot(dspy.Module):
    def __init__(self):
        super().__init__()

        self.generate_chat_reply = dspy.Predict(GenerateChatReply)
        print("Class Initialized : Chatbot")

    def fetch_chat_history(self, id: str) -> List[str]:
        print("Fetching chat history")
        # Fetch chat history from a MongoDB database

        uri = f"mongodb+srv://qmsoqm2:{os.environ["MONGO_DB_PASSWORD"]}@chathistory.tmp29wl.mongodb.net/?retryWrites=true&w=majority&appName=chatHistory"
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            db = client.get_database('chat_history')
            history_collection= db.get_collection('history')
            chat_history = list(history_collection.find({}))[0]
        except Exception as e:
            print(e)
            chat_history=None

        return chat_history

    def forward(self, conversation_id, message):
        initialize_dspy()
        
        chat_history = self.fetch_chat_history(id=conversation_id)
        
        if chat_history is None:
            return dspy.Prediction(reply="Error: can't find chat history...")
        
        user_info = ""
        for key, value in chat_history["user_info"].items():
            info = str(key) + ": " + str(value) + "\n"
            user_info += info

        previous_messages = ""
        for _, value in chat_history["messages"].items():
            author_message_block = value["author"] + ": " + value["message"] + "\n"
            previous_messages += author_message_block

        pred = self.generate_chat_reply(message=message, previous_messages=previous_messages, user_info=user_info)
        return dspy.Prediction(reply=pred.reply)


class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()

        # sub-modules
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        print("Class Initialized: RAG")

    def forward(self, question):
        context = self.retrieve(question).passages        
        pred = self.generate_answer(context=context, question=question)

        return dspy.Prediction(context=context, answer=pred.answer)


class SimplifiedBaleen(dspy.Module):
    def __init__(self, passages_per_hop=3, max_hops=2):
        super().__init__()

        self.generate_query = [
            dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)
        ]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        self.max_hops = max_hops

    def forward(self, question):
        context = []

        for hop in range(self.max_hops):
            query = self.generate_query[hop](context=context, question=question).query
            passages = self.retrieve(query).passages
            context = deduplicate(context + passages)

        pred = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=pred.answer)
