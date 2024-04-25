from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import dspy
from app.public.questions import QUESTIONS
from app.dspy.signatures.signatures import GenerateAnswer
from app.dspy.modules.rag import RAG
from app.dspy.modules.intent_classifier import IntentClassifier

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
    rag = RAG()
    pred = rag(question=QUESTIONS[-1])
    return {"message": pred.answer}


class IntentClassifierRequest(BaseModel):
    question: str

@router.post("/intent_classifier")
async def intent_classifier(request: IntentClassifierRequest):
    question = request.question
    print("Question: ", question)

    if not question:
        raise HTTPException(status_code=400, detail="No question provided.")

    intent_classifier = IntentClassifier()
    pred = intent_classifier(question="")
    return {"message": pred.answer}
