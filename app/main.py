from src.rag import SimpleRAG
from anthropic import Anthropic

client = Anthropic()

with open("data/docs.txt", "r", encoding="utf-8") as f:
    docs = f.read().split("\n\n")

rag = SimpleRAG(docs)

def ask(question):
    context = rag.retrieve(question)

    prompt = f"""
You are a cybersecurity assistant.

Context:
{context}

Question:
{question}

Answer with:
- Summary
- Threat mapping
- Defense
"""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text


if __name__ == "__main__":
    q = "What is command execution attack?"
    print(ask(q))