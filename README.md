# From 0 to Agentic AI: Design, Build & Deploy with LangGraph

Materials for the DataHack Summit 2026 workshop by **Alessandro Romano**.

Build a production **AI Knowledge Assistant** — from a single LLM call to a
deployed, multi-tool agent with RAG, memory, and MCP.

## What's here

- **📊 Slides** — [view the deck](https://pigna90.github.io/langgraph-workshop/)
  (source in [`web/`](web/); use `→`/`space` to advance, `s` for speaker notes)
- **📁 `src/`** — all the learning materials: hands-on notebooks (per module) and
  the Knowledge Assistant app you build and deploy. See [`src/README.md`](src/README.md)
  for setup and how to run.

## Quick start

```bash
cd src
uv sync            # install everything
# add your API keys to src/.env
uv run jupyter lab                      # run the notebooks
uv run streamlit run app/solution/app.py   # run the app
```

## License

[MIT](LICENSE) — use, adapt, and teach from this freely.

Bundled third-party code keeps its own license: `web/vendor/` contains
[reveal.js](https://revealjs.com) 5.1.0, also MIT, © Hakim El Hattab.
