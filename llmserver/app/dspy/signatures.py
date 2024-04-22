from app.common import stub
from modal import Image
import dspy
from dsp.utils import deduplicate

# image = Image.debian_slim(python_version="3.12.2").pip_install("dspy-ai")

# with image.imports():
#     import dspy

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
