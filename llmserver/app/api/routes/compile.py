from app.dspy.optimizers.rag import CompileRag
from app.dspy.optimizers.intent_classifier import CompileIntentClassifier

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "compile router is working fine!"}

@router.get("/{module_name}")
def compile(module_name: str):
    if module_name == "rag":
        return CompileRag().compile.remote(module_name)
    elif module_name == "intent_classifier":
        return CompileIntentClassifier().compile.remote()
    else:
        return {"message": "Module name not found!"}
