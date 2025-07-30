from pathlib import Path

import logging
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig


from core import get_model, settings

load_dotenv()

llm = get_model(settings.DEFAULT_MODEL)

# Configure logging
logger = logging.getLogger(__name__)

SYSTEM_MESSAGE_PATH = Path(__file__).with_name("system_message.md")
with open(SYSTEM_MESSAGE_PATH, "r", encoding="utf-8") as f:
    MODEL_SYSTEM_MESSAGE = f.read()


def assistant(state: MessagesState, config: RunnableConfig | None = None):
    system_message = MODEL_SYSTEM_MESSAGE
    messages = [SystemMessage(content=system_message)] + state["messages"]
    user_id = None
    thread_id = None
    if config and isinstance(config.configurable, dict):
        user_id = config.configurable.get("user_id")
        thread_id = config.configurable.get("thread_id")
    logger.info(
        "Incoming messages [user_id=%s thread_id=%s]: %s",
        user_id,
        thread_id,
        [m.content for m in state["messages"]],
    )
    response = llm.invoke(messages)
    logger.info(
        "Assistant response [user_id=%s thread_id=%s]: %s",
        user_id,
        thread_id,
        getattr(response, "content", str(response)),
    )
    return {"messages": response}


# --- Graph -------------------------------------------------------------
builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)        # узел
builder.add_edge(START, "assistant")            # START → assistant
builder.add_edge("assistant", END)              # assistant → END

agent = builder.compile()
