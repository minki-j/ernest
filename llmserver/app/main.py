from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.common import stub
from app.utils.dspy_initialize import check_dspy

from modal import Image, asgi_app, Secret

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI()

app.add_middleware(check_dspy)

app.include_router(api_router)

image = (
    Image.debian_slim(python_version="3.12.2")
    .pip_install("dspy-ai")
    .run_commands("pip install --upgrade fastapi pydantic")
)


# return the FastAPI app in a modal function
@stub.function(
    image=image,
    gpu=False,
    secrets=[Secret.from_name("OPENAI_API_KEY")],
)
@asgi_app()
def fastapi_app():
    return app
