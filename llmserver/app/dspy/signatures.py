from app.common import stub
from modal import Image
import dspy

# image = Image.debian_slim(python_version="3.12.2").pip_install("dspy-ai")

# with image.imports():
#     import dspy

class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")
    print("CLASS Initialized: GenerateAnswer")

class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()

        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        print("CLASS Initialized: RAG")

    def forward(self, question):
        print("question:", question)
        context = self.retrieve(question).passages
        print("context:", context)
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)