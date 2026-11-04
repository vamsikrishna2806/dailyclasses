"""06 · Output Parsers

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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
