import json
from pathlib import Path


def markdown(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.strip().splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip().splitlines(keepends=True),
    }


cells = [
    markdown(
        """
# RAG Concepts With A Free Model

This notebook teaches **RAG** step by step.

RAG means:

> Retrieval-Augmented Generation

Simple meaning:

> Before the AI answers, it first searches your documents, then answers only from the found information.

We will build a mini RAG chatbot using:

- A recent Agentic AI article PDF from arXiv
- Your GitHub repo as knowledge data
- Free local embeddings made with pure Python
- Groq free-tier model for final answers
- Gradio UI

Important: free API means a provider gives a free learning tier with limits. It does not mean unlimited forever.
"""
    ),
    markdown(
        """
## Real-World Example

Imagine you own a restaurant and give your staff a folder of documents:

- Menu
- Recipes
- Delivery policy
- Refund policy
- Customer FAQs

A normal chatbot may answer from general internet knowledge.

A RAG chatbot should answer like a trained employee:

> I will answer only from the restaurant documents you gave me.

If the answer is not in the documents, it should say:

> I cannot find this in the provided knowledge base.
"""
    ),
    markdown(
        """
## RAG Pipeline In Easy Words

RAG has these steps:

| Step | Simple Meaning | Restaurant Example |
|---|---|---|
| Documents | Your knowledge files | Menu, policy, recipes |
| Loading | Read the files | Open the menu |
| Chunking | Break big files into small parts | Split menu into sections |
| Embeddings | Convert text into number meaning | Make each section searchable |
| Vector search | Find relevant chunks | Find biryani policy section |
| Context | Selected chunks sent to LLM | Give waiter the exact page |
| Generation | LLM writes final answer | Waiter replies using that page |
| Citations | Show source | “From menu.pdf” |

The most important rule:

> The LLM should answer from retrieved context, not from random memory.
"""
    ),
    markdown(
        """
## Our RAG Data Sources

We will use two sources:

1. **Agentic AI article PDF**
   - Title: `The Hitchhiker's Guide to Agentic AI: From Foundations to Systems`
   - PDF: `https://arxiv.org/pdf/2606.24937`

2. **Your GitHub repo**
   - Repo: `https://github.com/Naeem2400/Agentic-AI-Routing-Gradio`

The notebook can download both. If PDF text extraction needs `pypdf` and it is not installed, the notebook will still use the arXiv abstract page as fallback text.
"""
    ),
    markdown(
        """
## Before Running

Your `.env` file should contain your Groq API key:

```text
GROQ_API_KEY=your_key_here
```

Never upload `.env` to GitHub.
"""
    ),
    code(
        """
import json
import math
import os
import re
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# Turn off LangSmith tracing for beginner notebooks.
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

print("GROQ_API_KEY:", "set" if os.getenv("GROQ_API_KEY") else "missing")
"""
    ),
    code(
        """
DATA_DIR = Path("rag_data")
DATA_DIR.mkdir(exist_ok=True)

ARXIV_ABS_URL = "https://arxiv.org/abs/2606.24937"
ARXIV_PDF_URL = "https://arxiv.org/pdf/2606.24937"
GITHUB_REPO_URL = "https://github.com/Naeem2400/Agentic-AI-Routing-Gradio"

GITHUB_OWNER = "Naeem2400"
GITHUB_REPO = "Agentic-AI-Routing-Gradio"
GITHUB_BRANCH = "main"

MODEL_NAME = "llama-3.1-8b-instant"
"""
    ),
    markdown(
        """
# Step 1: Download The Article PDF

We download the article PDF into `rag_data/`.

In a client project, this step could be:

- Download from Google Drive
- Read uploaded files
- Sync from Notion
- Read from a company website

For this learning notebook, we use an arXiv PDF.
"""
    ),
    code(
        """
def download_file(url: str, output_path: Path):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 RAG learning notebook"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        output_path.write_bytes(response.read())
    return output_path


pdf_path = DATA_DIR / "agentic_ai_article.pdf"

if not pdf_path.exists():
    print("Downloading PDF...")
    download_file(ARXIV_PDF_URL, pdf_path)
else:
    print("PDF already downloaded.")

print(pdf_path, pdf_path.stat().st_size, "bytes")
"""
    ),
    markdown(
        """
# Step 2: Extract Text From The PDF

To read PDF text, Python usually needs a package like `pypdf`.

If `pypdf` is missing, the notebook will use the arXiv abstract page as fallback.

Optional install command:

```python
%pip install pypdf
```

This package is free. It is not an LLM model.
"""
    ),
    code(
        """
class SimpleHTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.parts.append(text)

    def get_text(self):
        return "\\n".join(self.parts)


def clean_text(text: str) -> str:
    text = re.sub(r"\\s+", " ", text)
    return text.strip()


def fetch_html_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 RAG learning notebook"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        html = response.read().decode("utf-8", errors="ignore")

    parser = SimpleHTMLTextExtractor()
    parser.feed(html)
    return clean_text(parser.get_text())


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\\n".join(pages)
        return clean_text(text)
    except Exception as error:
        print("PDF text extraction fallback:", error)
        print("Using arXiv abstract page text instead.")
        return fetch_html_text(ARXIV_ABS_URL)


article_text = extract_pdf_text(pdf_path)
print("Article text characters:", len(article_text))
print(article_text[:600])
"""
    ),
    markdown(
        """
# Step 3: Download Your GitHub Repo Text

For RAG, we can use your repo as knowledge.

The notebook will fetch readable files:

- `.md`
- `.txt`
- `.py`
- `.ipynb`

For notebooks, it extracts Markdown and code cells as text.
"""
    ),
    code(
        """
def fetch_json(url: str):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 RAG learning notebook"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 RAG learning notebook"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="ignore")


def notebook_to_text(raw_json: str) -> str:
    try:
        notebook = json.loads(raw_json)
        parts = []
        for cell in notebook.get("cells", []):
            source = cell.get("source", [])
            if isinstance(source, list):
                source = "".join(source)
            if source.strip():
                parts.append(source.strip())
        return "\\n\\n".join(parts)
    except Exception:
        return raw_json


def fetch_github_repo_documents(max_files: int = 25):
    api_url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees/"
        f"{GITHUB_BRANCH}?recursive=1"
    )
    tree = fetch_json(api_url).get("tree", [])

    allowed_extensions = (".md", ".txt", ".py", ".ipynb")
    skip_parts = {".git", "venv", ".venv", "__pycache__", ".ipynb_checkpoints"}

    docs = []
    for item in tree:
        path = item.get("path", "")
        if item.get("type") != "blob":
            continue
        if any(part in skip_parts for part in Path(path).parts):
            continue
        if not path.endswith(allowed_extensions):
            continue

        raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{path}"
        try:
            raw_text = fetch_text(raw_url)
            if path.endswith(".ipynb"):
                raw_text = notebook_to_text(raw_text)
            raw_text = clean_text(raw_text)
            if raw_text:
                docs.append({
                    "title": path,
                    "source": f"{GITHUB_REPO_URL}/blob/{GITHUB_BRANCH}/{path}",
                    "text": raw_text,
                })
            if len(docs) >= max_files:
                break
        except Exception as error:
            print("Skipped", path, error)

    return docs


github_docs = fetch_github_repo_documents()
print("GitHub documents loaded:", len(github_docs))
for doc in github_docs[:5]:
    print("-", doc["title"])
"""
    ),
    markdown(
        """
# Step 4: Create Document Objects

Now we combine:

- Article text
- GitHub repo text

Each document keeps:

- `title`
- `source`
- `text`

This is important because later we need citations.
"""
    ),
    code(
        """
documents = [
    {
        "title": "The Hitchhiker's Guide to Agentic AI",
        "source": ARXIV_PDF_URL,
        "text": article_text,
    }
] + github_docs

print("Total documents:", len(documents))
print("Total characters:", sum(len(doc["text"]) for doc in documents))
"""
    ),
    markdown(
        """
# Step 5: Chunking

Big documents are too large to send fully to an LLM.

So we split them into **chunks**.

Example:

```text
Large PDF -> chunk 1, chunk 2, chunk 3...
```

Why chunk?

- Faster search
- More focused context
- Lower token cost
- Better citations

We also use **overlap** so meaning is not broken between chunks.
"""
    ),
    code(
        """
def chunk_text(text: str, chunk_size: int = 180, overlap: int = 35):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words)
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap

    return chunks


chunks = []
for doc in documents:
    for index, chunk in enumerate(chunk_text(doc["text"])):
        chunks.append({
            "chunk_id": f"{doc['title']}::chunk_{index + 1}",
            "title": doc["title"],
            "source": doc["source"],
            "text": chunk,
        })

print("Total chunks:", len(chunks))
print("\\nExample chunk:")
print(chunks[0]["text"][:800])
"""
    ),
    markdown(
        """
# Step 6: Embeddings

An **embedding** is a number version of text.

Simple example:

```text
"biryani menu price" -> [0.2, 0.8, 0.1, ...]
```

Why numbers?

Because computers can compare numbers and find similar meaning.

In production, you may use:

- OpenAI embeddings
- Gemini embeddings
- Hugging Face embeddings
- Chroma / Pinecone / Weaviate vector database

For this free learning notebook, we build a simple local embedding using word counts.

This is not as smart as real semantic embeddings, but it teaches the RAG idea clearly.
"""
    ),
    code(
        """
STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "by",
    "is", "are", "was", "were", "be", "as", "at", "from", "this", "that", "it",
    "we", "you", "your", "our", "their", "can", "will", "using", "use", "into",
    "about", "what", "which", "how", "why", "when", "where", "who"
}

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_\\-]{2,}")


def tokenize(text: str):
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    return [token for token in tokens if token not in STOPWORDS]


def embed_text(text: str):
    tokens = tokenize(text)
    counts = Counter(tokens)
    length = math.sqrt(sum(value * value for value in counts.values())) or 1.0
    return {word: value / length for word, value in counts.items()}


def cosine_similarity(vec_a: dict, vec_b: dict):
    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a
    return sum(value * vec_b.get(word, 0.0) for word, value in vec_a.items())


for chunk in chunks:
    chunk["embedding"] = embed_text(chunk["text"])

print("Embedding created for chunks:", len(chunks))
print("Sample embedding words:", list(chunks[0]["embedding"].items())[:10])
"""
    ),
    markdown(
        """
# Step 7: Retrieval

Retrieval means:

> Search the chunks and find the most relevant ones for the user's question.

This is the `R` in RAG.

The LLM should not see all documents. It should only see the best matching chunks.
"""
    ),
    code(
        """
def retrieve(question: str, top_k: int = 5):
    query_embedding = embed_text(question)

    scored = []
    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk["embedding"])
        scored.append({
            "score": score,
            "title": chunk["title"],
            "source": chunk["source"],
            "text": chunk["text"],
            "chunk_id": chunk["chunk_id"],
        })

    scored.sort(key=lambda item: item["score"], reverse=True)
    return [item for item in scored[:top_k] if item["score"] > 0]


test_question = "What notebooks are included in my GitHub repo?"
results = retrieve(test_question)

for item in results:
    print(round(item["score"], 4), "|", item["title"])
    print(item["text"][:250], "\\n")
"""
    ),
    markdown(
        """
# Step 8: Generation With Strict Grounding

Now the LLM receives:

- The user question
- Only the retrieved chunks

The system rule says:

> Answer only from the provided context. If the context does not contain the answer, say you cannot find it.

This prevents the chatbot from using random general training data.
"""
    ),
    code(
        """
def build_free_llm():
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("Missing GROQ_API_KEY in .env")

    return init_chat_model(
        f"groq:{MODEL_NAME}",
        temperature=0,
    )


def format_context(retrieved_chunks):
    context_parts = []
    for number, item in enumerate(retrieved_chunks, start=1):
        context_parts.append(
            f\"\"\"[SOURCE {number}]
Title: {item['title']}
URL: {item['source']}
Content: {item['text']}
\"\"\"
        )
    return "\\n\\n".join(context_parts)


STRICT_RAG_SYSTEM_PROMPT = \"\"\"You are a strict RAG assistant.
You must answer ONLY from the provided context.
If the context does not contain the answer, say:
"I could not find this in the provided documents."
Do not use outside knowledge.
Always mention the source title or source number used.\"\"\"


def fallback_extractive_answer(question: str, retrieved_chunks):
    if not retrieved_chunks:
        return "I could not find this in the provided documents."

    lines = [
        "Free fallback answer without LLM:",
        "I found these relevant document parts. Read them as the answer source:",
    ]
    for item in retrieved_chunks[:3]:
        lines.append(f"\\nSource: {item['title']}\\n{item['text'][:600]}...")
    return "\\n".join(lines)


def rag_answer(question: str, top_k: int = 5):
    retrieved_chunks = retrieve(question, top_k=top_k)

    if not retrieved_chunks:
        return "I could not find this in the provided documents.", []

    context = format_context(retrieved_chunks)

    user_prompt = f\"\"\"Question:
{question}

Context:
{context}

Answer with citations from the context only.\"\"\"

    try:
        llm = build_free_llm()
        response = llm.invoke([
            SystemMessage(content=STRICT_RAG_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ])
        return response.content, retrieved_chunks
    except Exception as error:
        print("LLM fallback:", error)
        return fallback_extractive_answer(question, retrieved_chunks), retrieved_chunks
"""
    ),
    markdown(
        """
# Step 9: Ask Questions

Try these questions.

Some questions should answer from the article.
Some should answer from your GitHub repo.
Some should say the answer is not found.
"""
    ),
    code(
        """
example_questions = [
    "What is this GitHub repo about?",
    "Which notebooks are included in my GitHub repo?",
    "What does the Agentic AI article discuss?",
    "What does the article say about agentic AI systems?",
    "Does my repo include a SQLite memory agent notebook?",
    "What is the refund policy of my restaurant?",
]

for question in example_questions:
    print("-", question)
"""
    ),
    code(
        """
answer, sources = rag_answer("Which notebooks are included in my GitHub repo?")
print(answer)
print("\\nSources:")
for source in sources[:3]:
    print("-", source["title"], source["source"])
"""
    ),
    code(
        """
answer, sources = rag_answer("What does the Agentic AI article discuss?")
print(answer)
print("\\nSources:")
for source in sources[:3]:
    print("-", source["title"], source["source"])
"""
    ),
    code(
        """
answer, sources = rag_answer("What is the refund policy of my restaurant?")
print(answer)
print("\\nSources found:", len(sources))
"""
    ),
    markdown(
        """
# Step 10: Gradio RAG UI

Now we create a small app.

The UI will:

1. Take a question
2. Retrieve chunks
3. Ask the free Groq model to answer from context
4. Show sources
"""
    ),
    code(
        """
def ui_rag_chat(question, top_k):
    if not question.strip():
        return "Please ask a question.", ""

    answer, retrieved = rag_answer(question, top_k=int(top_k))

    source_lines = []
    for item in retrieved:
        source_lines.append(
            f\"Score: {item['score']:.4f}\\nTitle: {item['title']}\\nURL: {item['source']}\\nPreview: {item['text'][:350]}...\\n\"
        )

    return answer, "\\n---\\n".join(source_lines)


with gr.Blocks(title="Free RAG Chatbot") as demo:
    gr.Markdown("# Free RAG Chatbot")
    gr.Markdown("Ask questions from the Agentic AI article and your GitHub repo only.")

    question_box = gr.Textbox(
        label="Question",
        placeholder="Ask about the article or GitHub repo...",
    )
    top_k_slider = gr.Slider(1, 8, value=5, step=1, label="Number of chunks to retrieve")
    ask_button = gr.Button("Ask RAG Bot")

    answer_box = gr.Textbox(label="Answer", lines=10)
    sources_box = gr.Textbox(label="Retrieved Sources", lines=14)

    ask_button.click(
        fn=ui_rag_chat,
        inputs=[question_box, top_k_slider],
        outputs=[answer_box, sources_box],
    )

    gr.Examples(
        examples=[
            ["What is this GitHub repo about?", 5],
            ["Which notebooks are included in my GitHub repo?", 5],
            ["What does the Agentic AI article discuss?", 5],
            ["Does my repo include a SQLite memory notebook?", 5],
            ["What is the refund policy of my restaurant?", 5],
        ],
        inputs=[question_box, top_k_slider],
    )


demo.launch()
"""
    ),
    markdown(
        """
# Final RAG Summary

You learned the full RAG flow:

```text
Documents
   ↓
Load text
   ↓
Chunks
   ↓
Embeddings
   ↓
Vector similarity search
   ↓
Relevant context
   ↓
LLM answer
   ↓
Sources / citations
```

Important lesson:

> RAG does not mean the model magically knows your documents.
> RAG means we search your documents first, then give the best parts to the model.

For client projects, you can upgrade this notebook by adding:

- Google Drive API loader
- Real embedding model
- Chroma / Pinecone vector database
- Login/authentication
- Better source citations
- Auto-sync when documents change
"""
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "venv",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.12.0",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

output_path = Path("rag_concepts_github_pdf_free_model.ipynb")
output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
print(f"Created {output_path}")
