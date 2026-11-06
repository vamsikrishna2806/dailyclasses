"""07 · Structured Output (Pydantic)

Run (with the venv active):  python main.py
Uses a free local model through Ollama (run: ollama pull llama3.2). No API key needed.
"""

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from langchain_ollama import ChatOllama

load_dotenv()

class Person(BaseModel):
    name: str = Field(description="full name of the person")
    age: int = Field(description="age in whole years")
    city: str | None = Field(default=None, description="city, if mentioned")

llm = ChatOllama(model="llama3.2", temperature=0)
person = llm.with_structured_output(Person).invoke(
    "Ravi Kumar is 25 and lives in Hyderabad."
)
print(person)
print("Next year he will be", person.age + 1)

try:
    Person(name="Ravi", age="twenty")
except ValidationError as e:
    print("Validation caught", e.error_count(), "error(s)")
