from dataclasses import dataclass

from langgraph.pregel import Pregel

from agents.agent import agent
from schema import AgentInfo

DEFAULT_AGENT = "agent"


@dataclass
class Agent:
    description: str
    graph: Pregel


agents: dict[str, Agent] = {
    "agent": Agent(
        description="An agent", graph=agent
    ),
}


def get_agent(agent_id: str) -> Pregel:
    return agents[agent_id].graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]
