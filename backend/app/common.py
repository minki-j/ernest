from modal import App, Image, Volume

app = App("survey_buddy")

image = (
    Image.debian_slim(python_version="3.12.2")
    .apt_install("graphviz", "libgraphviz-dev")
    .pip_install(
        "dspy-ai",
        "pymongo[srv]==4.6.3",
        "twilio",
        "python-multipart",
        "transformers",
        "huggingface_hub",
        "anthropic",
        "langchain",
        "langchain-openai",
        "langchain_anthropic",
        "langgraph==0.0.50",
        "langchainhub",
        "pygraphviz",
    )
    .run_commands("pip install --upgrade fastapi pydantic")
)

vol = Volume.from_name("ernest")
