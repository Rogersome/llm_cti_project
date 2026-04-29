from src.rag import SimpleRAG
from anthropic import Anthropic

client = Anthropic()

with open("data/docs.txt", "r", encoding="utf-8") as f:
    docs = f.read().split("\n\n")

rag = SimpleRAG(docs)

def ask(question):
    q = question.strip().lower()

    if len(q) < 5 or q in ["?", "???", "hello", "hi", "test"]:
        return "The input is unclear or not cybersecurity-related. Please provide a more specific description of the scenario."
    keywords = ["attack", "malware", "command", "script", "exploit", "security"]
    
    if not any(k in q for k in keywords):
        return "The input does not appear to be related to cybersecurity. Please provide more context."
    
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

    answer = response.content[0].text

    sources = "\n\n---\nSources:\n"
    for i, doc in enumerate(context):
        sources += f"[{i+1}] {doc[:150]}...\n"

    return answer + sources


if __name__ == "__main__":
    q = "What is command execution attack?"
    print(ask(q))