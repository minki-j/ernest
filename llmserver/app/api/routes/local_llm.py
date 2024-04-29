from fastapi import APIRouter, requests, Query

from pydantic import BaseModel

from app.local_llms.llama3_8b_on_vllm import Llama3_8B_on_VLLM
from app.local_llms.llama3_8b import Llama3_8B

router = APIRouter()


class UserQuestionRequest(BaseModel):
    prompt: str


@router.post("/")
def root(
    request: UserQuestionRequest,
    vllm: bool = Query(False),
    model: str = Query("llama3_8b"),
):
    print("Local LLM API call: path root(/)")
    user_questions = [request.prompt]

    if model == "llama3_8b":
        if vllm:
            llama3_8b = Llama3_8B_on_VLLM()
        else:
            llama3_8b = Llama3_8B()

    try:
        replys = llama3_8b.generate.remote(user_questions)
    except:
        print("error in generating response")
        replys = ["Error in generating response"]

    response = {"content": []}
    for reply in replys:
        response["content"].append({"text": reply})

    return response
