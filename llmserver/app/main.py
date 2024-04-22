from fastapi import FastAPI

from app.api.main import api_router
from app.common import stub, image

from modal import asgi_app, Secret

app = FastAPI()

# app.add_middleware()

app.include_router(api_router)

@stub.function(
    image=image,
    gpu=False,
    secrets=[
        Secret.from_name("OPENAI_API_KEY"),
        Secret.from_name("Monogo DB connection password"),
        Secret.from_name("my-twilio-secret"),
    ],
)
@asgi_app()
def fastapi_app():
    print("Starting FastAPI app")
    return app
