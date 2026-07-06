# Agentic AI Routing And LLM Gradio Agents

This repo contains beginner-friendly Agentic AI notebooks using LangGraph, LangChain, and Gradio.

## Notebooks

- `routing_agent_example.ipynb`: a no-LLM routing agent that chooses between `refund`, `cook_food`, `ask_question`, `call_tool`, and `end_chat`.
- `llm_gradio_agent.ipynb`: a restaurant agent with one LLM node and a Gradio app.

## Setup

Create and activate a virtual environment:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

Register the notebook kernel:

```bash
python -m ipykernel install --user --name agentic-ai --display-name "Python (Agentic AI)"
```

## API Key

The LLM notebook uses Groq first because OpenAI is usually paid.

Create a local `.env` file:

```env
GROQ_API_KEY=your_key_here
```

Do not upload `.env` to GitHub.

## Run

Open the notebooks in Cursor, VS Code, or Jupyter and select:

```text
Python (Agentic AI)
```

Run cells one by one.
