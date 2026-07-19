"""Streamlit chat UI for the Knowledge Assistant, with a department-MCP sidebar.

Run locally:  uv run streamlit run app/app.py

Left sidebar: toggle department MCP servers (HR, Finance, …) on/off. Turning one
on connects to its MCP server and the agent gains that department's tools; turning
it off removes them. Core tools (web search + company-docs RAG) are always on.
"""
import asyncio
import uuid

import streamlit as st
from langchain_core.messages import AIMessage, ToolMessage

from assistant import MCP_SERVERS, build_assistant, load_mcp_tools

st.set_page_config(page_title="Knowledge Assistant", page_icon="🧠")

# --- one thread_id per browser session = short-term memory (Module 6) ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.history = []
    st.session_state.enabled = []       # which MCP departments are on
    st.session_state.agent = None
    st.session_state.built_with = None  # the enabled-set the current agent was built with

cfg = {"configurable": {"thread_id": st.session_state.thread_id}}


async def rebuild(enabled: list[str]):
    """Load the enabled departments' MCP tools and rebuild the agent."""
    mcp_tools = await load_mcp_tools(enabled)
    return build_assistant(extra_tools=mcp_tools)


# --- sidebar: department MCP servers ---
with st.sidebar:
    st.header("🔌 Departments (MCP)")
    st.caption("Toggle a department's MCP server to add or remove its tools.")
    chosen = [name for name in MCP_SERVERS if st.checkbox(name, value=(name in st.session_state.enabled))]
    st.session_state.enabled = chosen
    st.divider()
    st.caption("Always on: 🔎 web search · 📚 company docs (RAG)")

# --- (re)build the agent if the enabled set changed (or first run) ---
if st.session_state.built_with != st.session_state.enabled:
    with st.spinner("Connecting to department MCP servers…"):
        st.session_state.agent = asyncio.run(rebuild(st.session_state.enabled))
        st.session_state.built_with = list(st.session_state.enabled)

# --- header ---
st.title("🧠 Company Knowledge Assistant")
active = ", ".join(st.session_state.enabled) if st.session_state.enabled else "none"
st.caption(f"Active departments: **{active}**")

# --- replay conversation ---
for role, content in st.session_state.history:
    st.chat_message(role).write(content)


async def answer(prompt: str):
    """Run the agent (async — required for MCP tools) and collect tools used.

    Also prints a short reasoning/tool trace to the terminal so you can see, live,
    what the agent decided and which tools it called.
    """
    print(f"\n🧑 USER: {prompt}")
    tools_used, final = [], ""
    async for step in st.session_state.agent.astream(
        {"messages": [("user", prompt)]}, cfg, stream_mode="values"
    ):
        last = step["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            for tc in last.tool_calls:
                print(f"  🔧 tool call: {tc['name']}({tc['args']})")
                tools_used.append(tc["name"])
        elif isinstance(last, ToolMessage):
            result = str(last.content).replace("\n", " ")
            print(f"  👁️  {last.name} → {result[:120]}")
        elif isinstance(last, AIMessage) and last.content:
            final = last.content
    print(f"🤖 ANSWER: {final[:150]}")
    return final, list(dict.fromkeys(tools_used))


# --- handle a new message ---
if prompt := st.chat_input("Ask about the company…"):
    st.session_state.history.append(("user", prompt))
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        final, tools_used = asyncio.run(answer(prompt))
        st.write(final)
        if tools_used:
            st.caption("🔧 used: " + ", ".join(tools_used))
    st.session_state.history.append(("assistant", final))
