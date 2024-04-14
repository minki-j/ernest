from modal import Image, asgi_app

from .signatures import GenerateAnswer, RAG
from .common import stub

image = (
    Image.debian_slim(python_version="3.12.2")
    .pip_install("dspy-ai", "fastapi")
    .env({"OPENAI_API_KEY": ""})
)

with image.imports():
    import dspy

question = "When did Newton discover gravity?"

@stub.function(gpu=False, image=image)
@asgi_app()
def web():
    from fastapi import FastAPI, Request
    from fastapi.responses import Response

    web_app = FastAPI()

    generate_answer = dspy.Predict(GenerateAnswer)
    pred = generate_answer(question=question)

    print("answer: ", pred.answer)

    @web_app.get("/")
    async def root():
        return {"message": pred.answer}

    return web_app
