import dspy
from dspy.datasets import HotPotQA
from dspy.teleprompt import BootstrapFewShot

from app.dspy.validations import validate_context_and_answer
from app.dspy.signatures import RAG
from app.dspy.compile import Compile

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "compile router is working fine!"}

@router.get("/{module_name}")
def compile(module_name: str):
    return Compile().compile.remote(module_name)
