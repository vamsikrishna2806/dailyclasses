"""04 · Prompt Templates

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()
template = PromptTemplate.from_template("Write a {tone} poem about {topic} in 4 lines.")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

for topic in ["Python", "the moon"]:
    prompt = template.invoke({"tone": "funny", "topic": topic}).to_string()
    print(llm.invoke(prompt).content)
    print("-" * 20)
