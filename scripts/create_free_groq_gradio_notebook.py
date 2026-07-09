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
# Free API Model Practice: Specific Class vs Universal `init_chat_model`

In this notebook we will use **Groq** as the free-tier API option for learning.

Important: free API means the provider gives a learning/free tier with limits. It does not mean unlimited forever. Always check the provider dashboard for your current limits.

We will learn three things:

1. How to use a model with a **specific class**: `ChatGroq`
2. How to use the same model with the **universal initializer**: `init_chat_model`
3. How to use both styles inside a simple **Gradio general AI agent**
"""
    ),
    markdown(
        """
## Daily Life Example

Imagine you want to order food.

Using a **specific class** is like going directly to one restaurant and saying:

> I always order from this restaurant.

Using **`init_chat_model`** is like using one food delivery app where you can choose different restaurants:

> Today Groq, tomorrow Gemini, later Anthropic or Mistral.

Both can give you food. The difference is how flexible your setup is.
"""
    ),
    markdown(
        """
## Before Running

Make sure your `.env` file has your Groq key:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Never share your API key on GitHub, LinkedIn, or screenshots.
"""
    ),
    code(
        """
import os

from dotenv import load_dotenv

load_dotenv()

# Turn off LangSmith tracing for this beginner notebook.
# This avoids 401 auth warnings if you do not have a LangSmith key.
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

print("GROQ_API_KEY:", "set" if os.getenv("GROQ_API_KEY") else "missing")
"""
    ),
    markdown(
        """
## Choose A Free-Tier Friendly Model

We will use a small, fast Groq-hosted model for learning:

```python
llama-3.1-8b-instant
```

Why this model?

- Good for practice
- Fast responses
- Works well for beginner agent examples
- Uses your Groq API key
"""
    ),
    code(
        """
MODEL_NAME = "llama-3.1-8b-instant"
TEMPERATURE = 0.2

SYSTEM_PROMPT = \"\"\"You are a helpful beginner AI assistant.
Explain things in very easy words.
Use simple daily-life examples when helpful.
Keep answers clear and practical.\"\"\"
"""
    ),
    markdown(
        """
# Part 1: Specific Class Model

This style uses the provider package directly.

For Groq, the specific class is:

```python
ChatGroq
```

This is simple when you already know: **I am using Groq.**
"""
    ),
    code(
        """
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

specific_llm = ChatGroq(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
)

messages = [
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content="Explain what an AI agent is using a restaurant example."),
]

specific_response = specific_llm.invoke(messages)
specific_response.content
"""
    ),
    markdown(
        """
## What Happened?

`ChatGroq` directly connects LangChain to Groq.

Think of it like this:

```text
Your question -> ChatGroq -> Groq model -> answer
```

This is easy and clear for one provider.
"""
    ),
    markdown(
        """
# Part 2: Universal Model With `init_chat_model`

Now we use LangChain's universal initializer:

```python
init_chat_model
```

This lets us initialize many providers with one common style.

For Groq, we write:

```python
groq:llama-3.1-8b-instant
```

The first part, `groq:`, tells LangChain which provider to use.
"""
    ),
    code(
        """
from langchain.chat_models import init_chat_model

universal_llm = init_chat_model(
    f"groq:{MODEL_NAME}",
    temperature=TEMPERATURE,
)

universal_response = universal_llm.invoke(messages)
universal_response.content
"""
    ),
    markdown(
        """
## What Happened?

`init_chat_model` created the Groq model for us.

Think of it like this:

```text
Your question -> init_chat_model -> choose Groq -> Groq model -> answer
```

This is useful when your project may switch providers later.
"""
    ),
    markdown(
        """
# Part 3: Simple Comparison

Use this rule:

| Style | Best When | Example |
|---|---|---|
| Specific class | You know the exact provider | `ChatGroq(...)` |
| Universal initializer | You want flexible provider switching | `init_chat_model("groq:model")` |

For learning, both are good. For projects that may grow, `init_chat_model` can make your code cleaner.
"""
    ),
    code(
        """
comparison = {
    "specific_class": "ChatGroq(model=MODEL_NAME)",
    "universal_initializer": 'init_chat_model(f"groq:{MODEL_NAME}")',
    "same_key": "Both use GROQ_API_KEY from .env",
    "main_difference": "Specific is direct. Universal is flexible.",
}

comparison
"""
    ),
    markdown(
        """
# Part 4: Build A Helper Function

Now we make one helper function.

It can return:

- the specific Groq model
- or the universal `init_chat_model` model

This is useful because our Gradio app can switch between both.
"""
    ),
    code(
        """
def build_llm(style: str = "universal"):
    \"\"\"Create an LLM using either the specific class or the universal initializer.\"\"\"
    if style == "specific":
        return ChatGroq(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
        )

    return init_chat_model(
        f"groq:{MODEL_NAME}",
        temperature=TEMPERATURE,
    )


test_llm = build_llm("universal")
test_llm.invoke([
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content="Give me 3 simple AI agent ideas for a small business."),
]).content
"""
    ),
    markdown(
        """
# Part 5: General AI Agent Function

This is a general assistant.

It is not limited to restaurant only. You can ask learning questions, business ideas, coding basics, or agent planning questions.

Note: this version does **not** have live search/weather tools. It only uses the LLM. For current news or live weather, connect tools like you did in the tool-agent notebook.
"""
    ),
    code(
        """
from langchain_core.messages import AIMessage


def general_agent_answer(user_question: str, style: str = "universal") -> str:
    llm = build_llm(style)
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_question),
    ])
    return response.content


general_agent_answer(
    "Explain specific class vs init_chat_model in one short paragraph.",
    style="universal",
)
"""
    ),
    markdown(
        """
# Part 6: Gradio General Agent App

Now we make a simple web app.

The user can choose:

- `universal` = `init_chat_model`
- `specific` = `ChatGroq`

Both use the same free-tier Groq API key.
"""
    ),
    code(
        """
import gradio as gr


def gradio_agent(message, history, model_style):
    llm = build_llm(model_style)

    chat_messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Keep a small conversation memory from the Gradio chat history.
    # Some Gradio versions use pairs: [(user, assistant), ...]
    # Newer versions may use dictionaries: {"role": "user", "content": "..."}
    for item in history or []:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role == "user" and content:
                chat_messages.append(HumanMessage(content=content))
            elif role == "assistant" and content:
                chat_messages.append(AIMessage(content=content))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            user_text, assistant_text = item[0], item[1]
            if user_text:
                chat_messages.append(HumanMessage(content=user_text))
            if assistant_text:
                chat_messages.append(AIMessage(content=assistant_text))

    chat_messages.append(HumanMessage(content=message))

    try:
        response = llm.invoke(chat_messages)
        return response.content
    except Exception as error:
        return f"Error: {error}"


with gr.Blocks(title="Free Groq General AI Agent") as demo:
    gr.Markdown("# Free Groq General AI Agent")
    gr.Markdown(
        "Choose **universal** to use `init_chat_model`, or **specific** to use `ChatGroq` directly."
    )

    model_style = gr.Radio(
        choices=["universal", "specific"],
        value="universal",
        label="Model setup style",
    )

    gr.ChatInterface(
        fn=gradio_agent,
        additional_inputs=[model_style],
        examples=[
            "Explain AI agents with a restaurant example.",
            "Give me 5 AI agent ideas for a small business.",
            "Explain LangChain and LangGraph in easy words.",
        ],
    )


demo.launch()
"""
    ),
    markdown(
        """
# Final Understanding

You learned:

1. **Groq API key** lets you call a free-tier model for learning.
2. **Specific class** means using a provider class directly, like `ChatGroq`.
3. **Universal initializer** means using `init_chat_model` so your code can switch providers more easily.
4. **Gradio** turns your model into a simple web app.

Simple memory:

```text
ChatGroq = direct restaurant
init_chat_model = delivery app that can choose different restaurants
Gradio = front counter where users talk to your agent
```
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

output_path = Path("free_groq_specific_universal_gradio.ipynb")
output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
print(f"Created {output_path}")
