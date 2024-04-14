from .common import stub
from modal import Image

image = Image.debian_slim(python_version="3.12.2").pip_install("dspy-ai")

with image.imports():
    import dspy

# ? Why does this run everytime the API gets called ?
print("\033[91m Setting up dspy configuration \033[0m")
turbo = dspy.OpenAI(model="gpt-3.5-turbo")
colbertv2_wiki17_abstracts = dspy.ColBERTv2(
    url="http://20.102.90.50:2017/wiki17_abstracts"
)
dspy.settings.configure(lm=turbo, rm=colbertv2_wiki17_abstracts)


@stub.cls()
class GenerateAnswer(dspy.Signature):
    print("init GenerateAnswer")
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")


@stub.cls()
class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        print("init RAG")
        super().__init__()

        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        print("question:", question)
        context = self.retrieve(question).passages
        print("context:", context)
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)
