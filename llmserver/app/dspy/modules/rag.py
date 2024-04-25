import dspy
import os

from app.dspy.signatures.signatures import GenerateAnswer
from app.dspy.utils.load_compiled_module import load_compiled_module_if_exists

class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()

        # sub-modules
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

        load_compiled_module_if_exists(self, "rag")

        print("Class Initialized: RAG")

    def forward(self, question):
        context = self.retrieve(question).passages
        pred = self.generate_answer(context=context, question=question)

        return dspy.Prediction(context=context, answer=pred.answer)
