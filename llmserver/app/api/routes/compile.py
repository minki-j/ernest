import dspy
from dspy.datasets import HotPotQA
from dspy.teleprompt import BootstrapFewShot

from app.dspy.validations import validate_context_and_answer
from app.dspy.signatures import RAG

from fastapi import APIRouter

router = APIRouter()

# # Load the dataset.
# dataset = HotPotQA(train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0)

# # Tell DSPy that the 'question' field is the input. Any other fields are labels and/or metadata.
# trainset = [x.with_inputs('question') for x in dataset.train]
# devset = [x.with_inputs('question') for x in dataset.dev]

@router.post("/compile/{module_name}")
def compile(module_name: str):
    print("Start compiling module ", module_name)
    if module_name == "rag":
        teleprompter = BootstrapFewShot(metric=validate_context_and_answer)
        return teleprompter.compile(RAG(), trainset=["test"])
