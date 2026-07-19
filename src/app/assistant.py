"""The Knowledge Assistant graph — 📝 YOU BUILD THIS.

The Streamlit frontend (app.py) is provided and imports three things from here:
    • build_assistant(extra_tools)  -> the compiled LangGraph agent
    • load_mcp_tools(enabled)       -> tools from the enabled department MCP servers
    • MCP_SERVERS                   -> the registry of available departments

Fill in every  # TODO  below, then run:   uv run streamlit run app/app.py
When the app answers questions, you've correctly assembled everything from the day.
Stuck? A full reference lives in  app/solution/.
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

# --- PROVIDED: the department MCP servers the sidebar can toggle ---
# Each entry launches that department's server over stdio. "HR" is one you'll
# finish writing in mcp_servers/hr_server.py; "Finance" is provided as a second example.
_MCP_DIR = pathlib.Path(__file__).parent / "mcp_servers"
MCP_SERVERS = {
    "HR":      {"command": "python", "args": [str(_MCP_DIR / "hr_server.py")],      "transport": "stdio"},
    "Finance": {"command": "python", "args": [str(_MCP_DIR / "finance_server.py")], "transport": "stdio"},
}


async def load_mcp_tools(enabled: list[str]) -> list:
    """Load tools from the enabled department MCP servers (async). Return [] if none.

    Steps:
      1. build a dict of just the enabled servers from MCP_SERVERS
      2. if it's empty, return []
      3. else connect with MultiServerMCPClient(servers) and `await .get_tools()`
    """
    # TODO: implement the three steps above (see Module 6 · MCP demo)
    ...


# --- PROVIDED: a tiny company knowledge base for the RAG tool ---
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
    """Persisted Chroma — embed once, reuse the store afterwards (don't re-embed on every rebuild)."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=_CHROMA_DIR, embedding_function=embeddings)
    if vectorstore._collection.count() == 0:      # first run only
        chunks = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30).split_documents(_DOCS)
        vectorstore.add_documents(chunks)
    return vectorstore


def _build_tools():
    """Build the two always-on core tools: company-docs RAG + web search."""
    retriever = _get_vectorstore().as_retriever(search_kwargs={"k": 2})  # provided
    seltz = Seltz()

    @tool
    def search_company_docs(query: str) -> str:
        """Search internal company docs (HR, finance, runbooks) for an answer."""
        # TODO: retriever.invoke(query) -> join the hits into a cited string
        #       (each hit has .page_content and .metadata['source']); "no matching internal docs" if empty
        ...

    @tool
    def web_search(query: str, max_results: int = 3) -> str:
        """Search the web for current, external information."""
        # TODO: call seltz.search(query, max_results=...) in a try/except (return "search error: ..." on failure),
        #       then join resp.documents (each has .url and .content) into a readable string
        ...

    return [search_company_docs, web_search]


class State(TypedDict):
    messages: Annotated[list, add_messages]


def build_assistant(extra_tools: list | None = None):
    """Build and compile the assistant graph (core tools + any enabled MCP tools).

    Assemble the LangGraph you built in Module 4:
      • an "agent" node that calls the LLM (with tools bound + SYSTEM_PROMPT)
      • a "tools" node (ToolNode)
      • START -> agent, a conditional edge (tools? loop back : end), tools -> agent
      • compile WITH a checkpointer so the app has short-term memory (Module 6)
    """
    tools = _build_tools() + (extra_tools or [])
    llm = init_chat_model("gpt-4.1-mini", model_provider="openai", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: State):
        # TODO: invoke llm_with_tools on [("system", SYSTEM_PROMPT)] + state["messages"];
        #       return {"messages": [<reply>]}
        ...

    def should_continue(state: State) -> str:
        # TODO: return "tools" if the last message has tool_calls, else "end"
        ...

    builder = StateGraph(State)
    # TODO: add nodes "agent" (call_model) and "tools" (ToolNode(tools))
    # TODO: START -> "agent"; conditional edge from "agent" via should_continue -> {"tools":"tools","end":END}
    # TODO: edge "tools" -> "agent" (the loop-back)
    # TODO: return builder.compile(checkpointer=InMemorySaver())
    ...


if __name__ == "__main__":
    # quick smoke test once you've filled the TODOs:  uv run python app/assistant.py
    import asyncio

    async def _smoke():
        mcp_tools = await load_mcp_tools(["HR"])
        app = build_assistant(extra_tools=mcp_tools)
        cfg = {"configurable": {"thread_id": "smoke-test"}}
        out = await app.ainvoke({"messages": [("user", "What benefits do we get for remote work?")]}, cfg)
        print("MCP tools:", [t.name for t in (mcp_tools or [])])
        print("Answer:", out["messages"][-1].content)

    asyncio.run(_smoke())
