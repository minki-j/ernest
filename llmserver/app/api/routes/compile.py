from app.dspy.optimizers.compile import Compile

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "compile router is working fine!"}

@router.get("/{module_name}")
def compile(module_name: str):
    return Compile().compile.remote(module_name)
