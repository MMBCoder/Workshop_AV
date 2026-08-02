# Agentic AI Workshop — code & notebooks

Everything you run during **From 0 to Agentic AI: Design, Build & Deploy with LangGraph**.

```
src/
├── pyproject.toml   # deps (managed by uv)
├── .env             # your API keys (gitignored)
├── notebooks/       # guided hands-on notebooks, per module
└── app/             # the Knowledge Assistant app
    ├── assistant.py #   the LangGraph agent (tools + RAG + memory)
    └── app.py       #   the Streamlit chat UI
```

## Setup — local (recommended)

1. **Install uv** (once) — the tool that manages Python + the environment:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install everything** (Python, all libs, Jupyter, Streamlit):
   ```bash
   cd src
   uv sync
   ```

3. **Add your keys** — edit `.env`:
   ```
   OPENAI_API_KEY=...
   TAVILY_API_KEY=...    # web search (module 2)
   SELTZ_API_KEY=...     # web search (module 5+)
   ```

## Run the notebooks

```bash
uv run jupyter lab
```
(or open a notebook in VS Code / Cursor and pick the `.venv` kernel)

## Run the app

The Knowledge Assistant is a Streamlit app — it runs **locally**, not in a notebook.

`app/app.py` is written for you. `app/assistant.py` is the assignment: fill in its
TODOs, then run it with

```bash
uv run streamlit run app/app.py
```

Want to see it working first? The finished version runs as-is:

```bash
uv run streamlit run app/solution/app.py
```

Either opens at `http://localhost:8501`. Chat with it — it searches the web, answers
from company docs (RAG), and remembers the conversation.

## Option — Google Colab (notebooks only)

No local setup: upload a notebook from `notebooks/` to Colab and run it. The
`!pip install` cell installs the deps, and you'll be prompted for your keys.
