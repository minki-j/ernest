from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.common import stub, image
from app.utils.dspy_initialize import initialize_dspy

from modal import Image, asgi_app, Secret

app = FastAPI()

app.add_middleware(initialize_dspy)

app.include_router(api_router)

# return the FastAPI app in a modal function
@stub.function(
    image=image,
    gpu=False,
    secrets=[Secret.from_name("OPENAI_API_KEY")],
)
@asgi_app()
def fastapi_app():
    return app
