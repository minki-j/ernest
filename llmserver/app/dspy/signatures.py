import os
from app.common import stub
from modal import Image
import dspy
from dsp.utils import deduplicate

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

    def forward(self, user_info, previous_messages, message):
        initialize_dspy()

        pred = self.generate_chat_reply(
            user_info=user_info,
            previous_messages=previous_messages,
            message=message,
        )
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
