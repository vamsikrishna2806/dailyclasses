"""06 · Output Parsers

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser, JsonOutputParser
from langchain_ollama import ChatOllama

load_dotenv()
llm = ChatOllama(model="llama3.2", temperature=0)

# 1. Message -> plain string
text = StrOutputParser().invoke(llm.invoke("Say hello in one line"))
print(type(text).__name__, text)

# 2. Text -> Python list
list_parser = CommaSeparatedListOutputParser()
raw = llm.invoke(f"List 4 fruits. {list_parser.get_format_instructions()}").content
print(list_parser.invoke(raw))

# 3. Text -> dict
json_parser = JsonOutputParser()
raw = llm.invoke(f"Name and age of a fictional person as JSON. {json_parser.get_format_instructions()}").content
print(json_parser.invoke(raw))
