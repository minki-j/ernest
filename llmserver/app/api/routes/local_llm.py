from fastapi import APIRouter, requests

from pydantic import BaseModel

from app.local_llms.llama3_8b_on_vllm import Llama3_8B_on_VLLM

router = APIRouter()

class UserQuestionRequest(BaseModel):
    prompt: str

@router.post("/")
def root(request: UserQuestionRequest):
    print("Local LLM API call: path root(/)")
    user_questions = [request.prompt]
    llama3_8b = Llama3_8B_on_VLLM()
    try:
        reply = llama3_8b.generate.remote(user_questions)
    except:
        print("error in generating response")
        reply = "Error in generating response"
        
    print(f"==>> reply: {reply}")
    return {"content": [{"text": reply}]}
