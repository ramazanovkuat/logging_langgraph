from pathlib import Path

import logging
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.messages import SystemMessage

from core import get_model, settings

load_dotenv()

llm = get_model(settings.DEFAULT_MODEL)

# Configure logging
logger = logging.getLogger(__name__)

SYSTEM_MESSAGE_PATH = Path(__file__).with_name("system_message.md")
with open(SYSTEM_MESSAGE_PATH, "r", encoding="utf-8") as f:
    MODEL_SYSTEM_MESSAGE = f.read()


def assistant(state: MessagesState):
    """Единственный узел: формируем prompt и получаем ответ LLM."""
    logger.info("Последние 10 сообщений: %s", state["messages"][-10:])
    messages = [SystemMessage(content=MODEL_SYSTEM_MESSAGE)] + state["messages"]
    response = llm.invoke(messages)
    logger.info("Ответ LLM: %s", response)
    return {"messages": response}


# --- Graph -------------------------------------------------------------
builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)        # узел
builder.add_edge(START, "assistant")            # START → assistant
builder.add_edge("assistant", END)              # assistant → END

agent = builder.compile()
