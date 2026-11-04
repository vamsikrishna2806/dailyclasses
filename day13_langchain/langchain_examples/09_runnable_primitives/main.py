"""09 · Runnable Building Blocks

Run (with the venv active):  python main.py
Needs OPENAI_API_KEY in a .env file (see ../.env.example).
"""

from operator import itemgetter
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def make(instr):
    return ChatPromptTemplate.from_template(instr + " the movie {movie}.") | llm | StrOutputParser()

# Fork: three answers from one input
panel = RunnableParallel(
    praise=make("Write a 1-line praise review for"),
    criticism=make("Write a 1-line criticism for"),
    verdict=make("Give a one-word verdict for"),
)

def show(d: dict) -> str:
    return "\n".join(f"== {k.upper()} ==\n{v}" for k, v in d.items())

print((panel | RunnableLambda(show)).invoke({"movie": "Inception"}))

# Passthrough: keep the question and add its length
demo = RunnableParallel(question=RunnablePassthrough(), length=lambda x: len(x["question"]))
print(demo.invoke({"question": "hello"}))

# itemgetter: pick one key from a larger input
pick = {"topic": itemgetter("subject")} | ChatPromptTemplate.from_template("Write a haiku about {topic}") | llm | StrOutputParser()
print(pick.invoke({"subject": "rain", "extra": "ignored"}))
