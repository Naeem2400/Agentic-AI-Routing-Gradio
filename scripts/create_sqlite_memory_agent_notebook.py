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
# SQLite Memory Agent With Free Groq API

In this notebook we will learn three important memory concepts for AI agents:

1. **Short-term memory**
2. **Long-term memory**
3. **Execution memory**

We will use:

- **SQLite** as a local memory database
- **Groq free-tier API** for the LLM
- **LangChain** for model messages
- **Gradio** for a small app

Important: free API means a provider gives a free learning tier with limits. It does not mean unlimited forever.
"""
    ),
    markdown(
        """
## Real-World Example: Restaurant Assistant

Imagine a restaurant assistant.

A customer says:

> My name is Maria. My favorite food is biryani. I am allergic to peanuts.

The assistant should remember:

- During this chat: what the customer just said
- Across future chats: name, favorite food, allergies
- During execution: what steps the agent performed

This is where memory becomes useful.
"""
    ),
    markdown(
        """
## Memory Concepts In Easy Words

### 1. Short-Term Memory

Short-term memory is the current conversation.

Daily life example:

> You are talking to a waiter right now. The waiter remembers what you said a few minutes ago.

In code, short-term memory usually stores the latest chat messages.

### 2. Long-Term Memory

Long-term memory stores important facts for later.

Daily life example:

> A restaurant remembers your favorite food and allergy for your next visit.

In code, long-term memory can be stored in a database like SQLite.

### 3. Execution Memory

Execution memory stores what the agent did internally.

Daily life example:

> The restaurant keeps a kitchen order log: order received, menu checked, bill calculated, reply sent.

In code, execution memory helps with debugging, audit, and understanding the agent workflow.
"""
    ),
    markdown(
        """
## Why SQLite?

SQLite is a small database stored in one local file.

For learning it is excellent because:

- No server setup
- Built into Python
- Easy to inspect
- Good for local memory examples

In a bigger production app, you may later move to PostgreSQL, MySQL, Supabase, Firebase, or a vector database.
"""
    ),
    markdown(
        """
## Before Running

Make sure your `.env` file has:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Never upload your `.env` file to GitHub.
"""
    ),
    code(
        """
import os
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

load_dotenv()

# Turn off LangSmith tracing for this beginner notebook.
# This avoids auth warnings if you do not have a LangSmith key.
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

print("GROQ_API_KEY:", "set" if os.getenv("GROQ_API_KEY") else "missing")
"""
    ),
    markdown(
        """
## Model Setup

We will use Groq with LangChain's universal initializer:

```python
init_chat_model("groq:llama-3.1-8b-instant")
```

This keeps the code flexible, because later you can switch providers more easily.
"""
    ),
    code(
        """
MODEL_NAME = "llama-3.1-8b-instant"
DB_PATH = Path("agent_memory.sqlite3")


def build_llm():
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("Missing GROQ_API_KEY. Add it to your .env file first.")

    return init_chat_model(
        f"groq:{MODEL_NAME}",
        temperature=0.2,
    )


SYSTEM_PROMPT = \"\"\"You are a helpful restaurant AI assistant.
Use very easy words.
Use the user's memory when it is available.
If the user has allergies, be careful and mention them.
If you are unsure, ask a simple follow-up question.\"\"\"
"""
    ),
    markdown(
        """
# Step 1: Create SQLite Memory Tables

We will create three tables:

| Table | Memory Type | Purpose |
|---|---|---|
| `short_term_messages` | Short-term | Latest chat messages for one session |
| `long_term_profile` | Long-term | Important user facts |
| `execution_logs` | Execution | Agent steps and actions |

The database file will be:

```text
agent_memory.sqlite3
```
"""
    ),
    code(
        """
def now_text():
    return datetime.now().isoformat(timespec="seconds")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            \"\"\"
            CREATE TABLE IF NOT EXISTS short_term_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            \"\"\"
        )

        conn.execute(
            \"\"\"
            CREATE TABLE IF NOT EXISTS long_term_profile (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                favorite_food TEXT,
                allergies TEXT,
                last_updated TEXT NOT NULL
            )
            \"\"\"
        )

        conn.execute(
            \"\"\"
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                step TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            \"\"\"
        )

    print(f"Database ready: {DB_PATH}")


init_db()
"""
    ),
    markdown(
        """
# Step 2: Short-Term Memory Functions

Short-term memory keeps the recent conversation.

We will store it by `session_id`.

Simple idea:

```text
One chat session = one short-term memory box
```

When a new session starts, the short-term memory can be empty again.
"""
    ),
    code(
        """
def save_short_term_message(session_id: str, user_id: str, role: str, content: str):
    with get_connection() as conn:
        conn.execute(
            \"\"\"
            INSERT INTO short_term_messages (session_id, user_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            \"\"\",
            (session_id, user_id, role, content, now_text()),
        )


def get_short_term_messages(session_id: str, limit: int = 8):
    with get_connection() as conn:
        rows = conn.execute(
            \"\"\"
            SELECT role, content, created_at
            FROM short_term_messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            \"\"\",
            (session_id, limit),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


def trim_short_term_memory(session_id: str, keep: int = 8):
    with get_connection() as conn:
        conn.execute(
            \"\"\"
            DELETE FROM short_term_messages
            WHERE session_id = ?
            AND id NOT IN (
                SELECT id
                FROM short_term_messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            )
            \"\"\",
            (session_id, session_id, keep),
        )


def clear_short_term_memory(session_id: str):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM short_term_messages WHERE session_id = ?",
            (session_id,),
        )


def format_short_term_memory(session_id: str):
    messages = get_short_term_messages(session_id)
    if not messages:
        return "No short-term messages yet."

    lines = []
    for item in messages:
        lines.append(f"{item['role'].title()}: {item['content']}")
    return "\\n".join(lines)
"""
    ),
    markdown(
        """
# Step 3: Long-Term Memory Functions

Long-term memory stores stable user facts.

In our restaurant example, we save:

- Name
- Favorite food
- Allergies

This helps the assistant personalize answers in future sessions.
"""
    ),
    code(
        """
def get_profile(user_id: str):
    with get_connection() as conn:
        row = conn.execute(
            \"\"\"
            SELECT user_id, name, favorite_food, allergies, last_updated
            FROM long_term_profile
            WHERE user_id = ?
            \"\"\",
            (user_id,),
        ).fetchone()

    if row is None:
        return {
            "user_id": user_id,
            "name": None,
            "favorite_food": None,
            "allergies": None,
            "last_updated": None,
        }

    return dict(row)


def update_profile(user_id: str, name=None, favorite_food=None, allergies=None):
    old = get_profile(user_id)

    new_name = name or old.get("name")
    new_favorite_food = favorite_food or old.get("favorite_food")
    new_allergies = allergies or old.get("allergies")

    with get_connection() as conn:
        conn.execute(
            \"\"\"
            INSERT INTO long_term_profile (
                user_id, name, favorite_food, allergies, last_updated
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                favorite_food = excluded.favorite_food,
                allergies = excluded.allergies,
                last_updated = excluded.last_updated
            \"\"\",
            (user_id, new_name, new_favorite_food, new_allergies, now_text()),
        )


def format_profile(user_id: str):
    profile = get_profile(user_id)
    lines = [
        f"User ID: {profile['user_id']}",
        f"Name: {profile['name'] or 'not saved yet'}",
        f"Favorite food: {profile['favorite_food'] or 'not saved yet'}",
        f"Allergies: {profile['allergies'] or 'not saved yet'}",
        f"Last updated: {profile['last_updated'] or 'never'}",
    ]
    return "\\n".join(lines)
"""
    ),
    markdown(
        """
# Step 4: Execution Memory Functions

Execution memory records what the agent did.

Example:

```text
1. Received user message
2. Extracted facts
3. Loaded short-term memory
4. Loaded long-term memory
5. Called LLM
6. Saved answer
```

This is useful when your agent gets bigger and you need to debug it.
"""
    ),
    code(
        """
def log_execution(session_id: str, user_id: str, step: str, detail: str):
    with get_connection() as conn:
        conn.execute(
            \"\"\"
            INSERT INTO execution_logs (session_id, user_id, step, detail, created_at)
            VALUES (?, ?, ?, ?, ?)
            \"\"\",
            (session_id, user_id, step, detail, now_text()),
        )


def get_execution_logs(session_id: str, limit: int = 20):
    with get_connection() as conn:
        rows = conn.execute(
            \"\"\"
            SELECT step, detail, created_at
            FROM execution_logs
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            \"\"\",
            (session_id, limit),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


def format_execution_logs(session_id: str):
    rows = get_execution_logs(session_id)
    if not rows:
        return "No execution logs yet."

    lines = []
    for row in rows:
        lines.append(f"{row['created_at']} | {row['step']} | {row['detail']}")
    return "\\n".join(lines)
"""
    ),
    markdown(
        """
# Step 5: Extract Important Facts

We need a simple way to save long-term memory.

For learning, we will use simple text patterns:

- `my name is Maria`
- `my favorite food is biryani`
- `I am allergic to peanuts`

Later, you can improve this using an LLM extractor or form fields.
"""
    ),
    code(
        """
def clean_fact(value: str):
    value = value.strip()
    value = re.sub(r"[.!?]+$", "", value)
    return value.strip()


def extract_and_save_user_facts(user_id: str, message: str):
    text = message.strip()
    updates = {}

    name_match = re.search(
        r"\\b(?:my name is|i am|i'm)\\s+([A-Za-z][A-Za-z ]{0,30}?)(?:\\.|,| and |$)",
        text,
        flags=re.IGNORECASE,
    )
    if name_match:
        updates["name"] = clean_fact(name_match.group(1)).title()

    food_match = re.search(
        r"\\b(?:my favorite food is|my favourite food is|i like|i love)\\s+([A-Za-z][A-Za-z ]{1,40}?)(?:\\.|,| and |$)",
        text,
        flags=re.IGNORECASE,
    )
    if food_match:
        updates["favorite_food"] = clean_fact(food_match.group(1)).lower()

    allergy_match = re.search(
        r"\\b(?:i am allergic to|i'm allergic to|allergic to|my allergy is)\\s+([A-Za-z][A-Za-z ,]{1,60}?)(?:\\.|$)",
        text,
        flags=re.IGNORECASE,
    )
    if allergy_match:
        updates["allergies"] = clean_fact(allergy_match.group(1)).lower()

    if updates:
        update_profile(user_id, **updates)

    return updates
"""
    ),
    markdown(
        """
# Step 6: Test Memory Without LLM

Before calling the model, test the memory database.
"""
    ),
    code(
        """
USER_ID = "customer_001"
SESSION_ID = str(uuid.uuid4())

print("USER_ID:", USER_ID)
print("SESSION_ID:", SESSION_ID)

save_short_term_message(SESSION_ID, USER_ID, "user", "My name is Maria and my favorite food is biryani.")
facts = extract_and_save_user_facts(USER_ID, "My name is Maria and my favorite food is biryani.")
log_execution(SESSION_ID, USER_ID, "fact_extraction", f"Saved facts: {facts}")

print("\\nSHORT-TERM MEMORY")
print(format_short_term_memory(SESSION_ID))

print("\\nLONG-TERM MEMORY")
print(format_profile(USER_ID))

print("\\nEXECUTION MEMORY")
print(format_execution_logs(SESSION_ID))
"""
    ),
    markdown(
        """
# Step 7: Build The Memory Agent

The agent will:

1. Receive a user message
2. Save the user message in short-term memory
3. Extract important facts into long-term memory
4. Read short-term memory
5. Read long-term memory
6. Call the Groq model
7. Save the assistant answer
8. Log each execution step
"""
    ),
    code(
        """
def build_memory_prompt(user_id: str, session_id: str):
    profile_text = format_profile(user_id)
    short_term_text = format_short_term_memory(session_id)

    return f\"\"\"{SYSTEM_PROMPT}

LONG-TERM MEMORY:
{profile_text}

SHORT-TERM MEMORY:
{short_term_text}

Use the memory naturally.
Do not say you are using a database unless the user asks.
If the user asks what you remember, answer from the memory above.
\"\"\"


def chat_with_memory_agent(user_message: str, user_id: str = USER_ID, session_id: str = SESSION_ID):
    log_execution(session_id, user_id, "receive_message", user_message)

    save_short_term_message(session_id, user_id, "user", user_message)
    log_execution(session_id, user_id, "short_term_save", "Saved user message")

    facts = extract_and_save_user_facts(user_id, user_message)
    log_execution(session_id, user_id, "long_term_update", f"Facts found: {facts or 'none'}")

    memory_prompt = build_memory_prompt(user_id, session_id)
    log_execution(session_id, user_id, "memory_load", "Loaded short-term and long-term memory")

    llm = build_llm()
    response = llm.invoke([
        SystemMessage(content=memory_prompt),
        HumanMessage(content=user_message),
    ])
    answer = response.content
    log_execution(session_id, user_id, "llm_call", f"Used model: {MODEL_NAME}")

    save_short_term_message(session_id, user_id, "assistant", answer)
    trim_short_term_memory(session_id)
    log_execution(session_id, user_id, "assistant_reply_saved", "Saved assistant answer")

    return answer
"""
    ),
    markdown(
        """
# Step 8: Try The Agent

Run these cells one by one.

The first message teaches the agent your long-term facts.
"""
    ),
    code(
        """
chat_with_memory_agent(
    "Hi, my name is Maria. My favorite food is biryani. I am allergic to peanuts."
)
"""
    ),
    markdown(
        """
Now ask a new question. The agent should use your memory.
"""
    ),
    code(
        """
chat_with_memory_agent("What should I order today?")
"""
    ),
    markdown(
        """
Ask what it remembers.
"""
    ),
    code(
        """
chat_with_memory_agent("What do you remember about me?")
"""
    ),
    markdown(
        """
# Step 9: See The Three Memories

Now inspect each memory type.
"""
    ),
    code(
        """
print("SHORT-TERM MEMORY")
print(format_short_term_memory(SESSION_ID))

print("\\nLONG-TERM MEMORY")
print(format_profile(USER_ID))

print("\\nEXECUTION MEMORY")
print(format_execution_logs(SESSION_ID))
"""
    ),
    markdown(
        """
# Step 10: New Session Example

This proves the difference between short-term and long-term memory.

We create a new session.

- Short-term memory is empty
- Long-term profile still remembers Maria's facts
"""
    ),
    code(
        """
NEW_SESSION_ID = str(uuid.uuid4())

print("NEW_SESSION_ID:", NEW_SESSION_ID)
print("\\nSHORT-TERM MEMORY IN NEW SESSION")
print(format_short_term_memory(NEW_SESSION_ID))

print("\\nLONG-TERM MEMORY STILL EXISTS")
print(format_profile(USER_ID))
"""
    ),
    code(
        """
chat_with_memory_agent(
    "Do you still know my favorite food?",
    user_id=USER_ID,
    session_id=NEW_SESSION_ID,
)
"""
    ),
    markdown(
        """
# Step 11: Gradio App

This app shows:

- Chat area
- User ID
- Long-term memory panel
- Execution memory panel

Use the same user ID if you want the agent to remember you.
Use a new session if you want a fresh short-term conversation.
"""
    ),
    code(
        """
def ui_send(message, chat_history, user_id, session_id):
    if not message.strip():
        return "", chat_history, format_profile(user_id), format_execution_logs(session_id)

    chat_history = chat_history or []
    answer = chat_with_memory_agent(message, user_id=user_id, session_id=session_id)

    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": answer})

    return "", chat_history, format_profile(user_id), format_execution_logs(session_id)


def ui_new_session(user_id):
    new_session_id = str(uuid.uuid4())
    return [], new_session_id, format_profile(user_id), "New short-term session started."


with gr.Blocks(title="SQLite Memory Agent") as demo:
    gr.Markdown("# SQLite Memory Agent")
    gr.Markdown("Restaurant assistant with short-term, long-term, and execution memory.")

    with gr.Row():
        user_id_box = gr.Textbox(value="customer_001", label="User ID")
        session_id_box = gr.Textbox(value=str(uuid.uuid4()), label="Session ID")

    chatbot = gr.Chatbot(label="Chat", type="messages")
    message_box = gr.Textbox(label="Message", placeholder="Tell me your name, favorite food, or allergy...")

    with gr.Row():
        send_button = gr.Button("Send")
        new_session_button = gr.Button("New Short-Term Session")

    with gr.Row():
        profile_box = gr.Textbox(label="Long-Term Memory", lines=8)
        logs_box = gr.Textbox(label="Execution Memory", lines=8)

    send_button.click(
        fn=ui_send,
        inputs=[message_box, chatbot, user_id_box, session_id_box],
        outputs=[message_box, chatbot, profile_box, logs_box],
    )

    message_box.submit(
        fn=ui_send,
        inputs=[message_box, chatbot, user_id_box, session_id_box],
        outputs=[message_box, chatbot, profile_box, logs_box],
    )

    new_session_button.click(
        fn=ui_new_session,
        inputs=[user_id_box],
        outputs=[chatbot, session_id_box, profile_box, logs_box],
    )


demo.launch()
"""
    ),
    markdown(
        """
# Final Summary

You learned:

| Memory | Simple Meaning | In This Notebook |
|---|---|---|
| Short-term memory | Current chat | `short_term_messages` table |
| Long-term memory | Important facts | `long_term_profile` table |
| Execution memory | Agent action log | `execution_logs` table |

Simple daily-life memory:

```text
Short-term = waiter remembers this conversation
Long-term = restaurant remembers your profile
Execution = kitchen log of what happened
```

This is the foundation for building more serious agents later.
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

output_path = Path("sqlite_memory_agent.ipynb")
output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
print(f"Created {output_path}")
