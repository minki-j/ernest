import os
from modal import Image

from fastapi import APIRouter

from app.dspy.signatures import GenerateAnswer, RAG
from app.common import stub
from app.public.questions import QUESTIONS
from app.api.routes.compile import Compile

import dspy

router = APIRouter()

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
    compile_class = Compile()
    pred = compile_class.compiled_RAG.remote(question=QUESTIONS[-1])
    return {"message": pred.answer}
