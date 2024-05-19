from fastapi import FastAPI

from app.api.main import api_router
from app.common import app, image, vol

from modal import asgi_app, Secret

web_app = FastAPI()

# fastapi_app.add_middleware()

web_app.include_router(api_router)


@app.function(
    image=image,
    gpu=False,
    secrets=[
        Secret.from_name("OPENAI_API_KEY"),
        Secret.from_name("my-anthropic-secret"),
        Secret.from_name("Monogo DB connection password"),
        Secret.from_name("my-twilio-secret"),
        Secret.from_name("langsmith"),
    ],
    volumes={"/ernest": vol},
)
@asgi_app()
def fastapi_asgi():
    import os
    print("Starting FastAPI app")
    return web_app
