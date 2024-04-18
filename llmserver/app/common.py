from modal import Stub, Image

stub = Stub("survey_buddy")

image = (
    Image.debian_slim(python_version="3.12.2")
    .pip_install("dspy-ai")
    .run_commands("pip install --upgrade fastapi pydantic")
)
