import os
from modal import Image

from fastapi import APIRouter

from app.dspy.signatures import GenerateAnswer, RAG
from app.common import stub
from app.public.questions import QUESTIONS

router = APIRouter()

image = (
    Image.debian_slim(python_version="3.12.2")
    .pip_install("dspy-ai", "fastapi")
)

with image.imports():
    import dspy


@router.get("/")
def root():
    return {"message": "Server is working fine!"}

@router.get("/qna")
def qna():
    generate_answer = dspy.Predict(GenerateAnswer)
    pred = generate_answer(question=QUESTIONS[-1])
    return {"message": pred.answer}

@router.get("/rag")
def rag():
    generate_answer = dspy.Predict(GenerateAnswer)
    pred = generate_answer(question=QUESTIONS[-1])
    return {"message": pred.answer}
