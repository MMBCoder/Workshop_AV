"""The Knowledge Assistant graph (v3.2), extracted from the Module 6 notebook.

Single source of truth for the agent: core tools (RAG + web search + memory) PLUS
optional **department MCP servers** the user toggles on in the app sidebar.
Both the Streamlit UI (app.py) and deployment (Module 9) import from here.
"""
import pathlib
from typing import Annotated, TypedDict

from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from seltz import Seltz

load_dotenv(find_dotenv(usecwd=True))

# --- department MCP servers you can toggle on in the sidebar ---
# "each department hands you their MCP; add it to your assistant, or turn it off."
_MCP_DIR = pathlib.Path(__file__).parent / "mcp_servers"
MCP_SERVERS = {
    "HR":      {"command": "python", "args": [str(_MCP_DIR / "hr_server.py")],      "transport": "stdio"},
    "Finance": {"command": "python", "args": [str(_MCP_DIR / "finance_server.py")], "transport": "stdio"},
}


async def load_mcp_tools(enabled: list[str]) -> list:
    """Load tools from the enabled department MCP servers (async). [] if none."""
    servers = {name: MCP_SERVERS[name] for name in enabled if name in MCP_SERVERS}
    if not servers:
        return []
    return await MultiServerMCPClient(servers).get_tools()

# --- a tiny company knowledge base (same corpus as the Module 6 notebook) ---
_DOCS = [
    Document(page_content="The billing service is owned by the Payments team. On-call lead: Sam. "
             "Escalate outages in #billing-oncall.", metadata={"source": "runbook"}),
    Document(page_content="Employees get 28 days of paid time off (PTO) per year, plus public "
             "holidays. Requests go through the HR portal.", metadata={"source": "hr-policy"}),
    Document(page_content="Production deploys run weekdays at 9pm IST via the release bot. "
             "Rollbacks: `deploy rollback <service>`.", metadata={"source": "runbook"}),
    Document(page_content="Expense reports over $500 need manager approval. Reimbursement "
             "takes 5-7 business days.", metadata={"source": "finance-policy"}),
]

SYSTEM_PROMPT = (
    "You are the company Knowledge Assistant. For questions about internal policy, people, "
    "or operations, use search_company_docs. For general or current external info, use "
    "web_search. Always cite what you used."
)


_CHROMA_DIR = str(pathlib.Path(__file__).parent / "chroma_db")


def _get_vectorstore():
    """Persisted Chroma — embed the docs once, reuse the store on every later run."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=_CHROMA_DIR, embedding_function=embeddings)
    if vectorstore._collection.count() == 0:      # first run only
        chunks = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30).split_documents(_DOCS)
        vectorstore.add_documents(chunks)
    return vectorstore


def _build_tools():
    retriever = _get_vectorstore().as_retriever(search_kwargs={"k": 2})
    seltz = Seltz()

    @tool
    def search_company_docs(query: str) -> str:
        """Search internal company docs (HR, finance, runbooks) for an answer."""
        hits = retriever.invoke(query)
        if not hits:
            return "no matching internal docs"
        return "\n\n".join(f"[{h.metadata['source']}] {h.page_content}" for h in hits)

    @tool
    def web_search(query: str, max_results: int = 3) -> str:
        """Search the web for current, external information."""
        try:
            resp = seltz.search(query, max_results=max_results)
        except Exception as e:
            return f"search error: {e}"
        return "\n\n".join(f"{d.url}\n{(d.content or '')[:300]}" for d in resp.documents) or "no results"

    return [search_company_docs, web_search]


class State(TypedDict):
    messages: Annotated[list, add_messages]


def build_assistant(extra_tools: list | None = None):
    """Build and compile the assistant graph.

    Core tools (RAG + web search) are always on. `extra_tools` are the optional
    department MCP tools loaded from whichever servers the user enabled.
    """
    tools = _build_tools() + (extra_tools or [])
    llm = init_chat_model("gpt-4.1-mini", model_provider="openai", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: State):
        msgs = [("system", SYSTEM_PROMPT)] + state["messages"]
        return {"messages": [llm_with_tools.invoke(msgs)]}

    def should_continue(state: State) -> str:
        return "tools" if state["messages"][-1].tool_calls else "end"

    builder = StateGraph(State)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    builder.add_edge("tools", "agent")
    return builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    # quick smoke test: `uv run python app/assistant.py`
    import asyncio

    async def _smoke():
        mcp_tools = await load_mcp_tools(["HR"])            # enable HR department
        app = build_assistant(extra_tools=mcp_tools)
        cfg = {"configurable": {"thread_id": "smoke-test"}}
        out = await app.ainvoke({"messages": [("user", "What benefits do we get for remote work?")]}, cfg)
        print("MCP tools:", [t.name for t in mcp_tools])
        print("Answer:", out["messages"][-1].content)

    asyncio.run(_smoke())
