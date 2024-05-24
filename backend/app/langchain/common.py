from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAI

output_parser = StrOutputParser()

chat_model = ChatOpenAI(model="gpt-3.5-turbo")
chat_model_openai_4o = ChatOpenAI(model="gpt-4o")
# llm = OpenAI(model="gpt-3.5-turbo")
llm = OpenAI(model="gpt-4o")

# from langchain_anthropic import ChatAnthropic, Anthropic
# chat_model = ChatAnthropic(model="claude-3-haiku-20240307")
# llm = Anthropic(model="claude-3-haiku-20240307")
