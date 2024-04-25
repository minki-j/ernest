from modal import App, Image

app = App("survey_buddy")

image = (
    Image.debian_slim(python_version="3.12.2")
    .pip_install(
        "dspy-ai",
        "pymongo[srv]==4.6.3",
        "twilio",
        "python-multipart",
        "transformers",
        "huggingface_hub",
        "anthropic",
    )
    .run_commands("pip install --upgrade fastapi pydantic")
)
