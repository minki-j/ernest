from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.runnables import ConfigurableField


output_parser = StrOutputParser()

chat_model = ChatOpenAI(model="gpt-3.5-turbo").configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature",
        name="LLM Temperature",
        description="The temperature of the LLM",
    )
)
chat_model_openai_4o = ChatOpenAI(model="gpt-4o").configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature",
        name="LLM Temperature",
        description="The temperature of the LLM",
    )
)
# llm = OpenAI(model="gpt-3.5-turbo")
llm = OpenAI(model="gpt-4o").configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature",
        name="LLM Temperature",
        description="The temperature of the LLM",
    )
)

# from langchain_anthropic import ChatAnthropic, Anthropic
# chat_model = ChatAnthropic(model="claude-3-haiku-20240307")
# llm = Anthropic(model="claude-3-haiku-20240307")
