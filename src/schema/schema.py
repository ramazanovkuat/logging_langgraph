from typing import Any, Literal, NotRequired

from pydantic import BaseModel, Field, SerializeAsAny
from typing_extensions import TypedDict

from schema.models import AllModelEnum, OpenAICompatibleName, OpenAIModelName


class AgentInfo(BaseModel):
    """Info about an available agent."""

    key: str = Field(
        description="Agent key.",
        examples=["agent"],
    )
    description: str = Field(
        description="Description of the agent.",
        examples=["An agent that helps with commont queries."],
    )


class ServiceMetadata(BaseModel):
    """Metadata about the service including available agents and models."""

    agents: list[AgentInfo] = Field(
        description="List of available agents.",
    )
    models: list[AllModelEnum] = Field(
        description="List of available LLMs.",
    )
    default_agent: str = Field(
        description="Default agent used when none is specified.",
        examples=["agent"],
    )
    default_model: AllModelEnum = Field(
        description="Default model used when none is specified.",
    )


class UserInput(BaseModel):
    """Basic user input for the agent."""

    message: str = Field(
        description="User input to the agent.",
        examples=["Расскажи о стоицизме"],
    )
    model: SerializeAsAny[AllModelEnum] | None = Field(
        title="Model",
        description="LLM Model to use for the agent.",
        default=OpenAICompatibleName.OPENAI_COMPATIBLE,
        examples=[OpenAICompatibleName.OPENAI_COMPATIBLE, OpenAIModelName.GPT_4O_MINI],
    )
    thread_id: str | None = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    user_id: str | None = Field(
        description="User ID to persist and continue a conversation across multiple threads.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    agent_config: dict[str, Any] = Field(
        description="Additional configuration to pass through to the agent",
        default={},
        examples=[{"temperature": 0.8}],
    )


class StreamInput(UserInput):
    """User input for streaming the agent's response."""

    stream_tokens: bool = Field(
        description="Whether to stream LLM tokens to the client.",
        default=True,
    )


class ToolCall(TypedDict):
    """Represents a request to call a tool."""

    name: str
    """The name of the tool to be called."""
    args: dict[str, Any]
    """The arguments to the tool call."""
    id: str | None
    """An identifier associated with the tool call."""
    type: NotRequired[Literal["tool_call"]]


class ChatMessage(BaseModel):
    """Message in a chat."""

    type: Literal["human", "ai", "tool", "custom"] = Field(
        description="Role of the message.",
        examples=["human", "ai", "tool", "custom"],
    )
    content: str = Field(
        description="Content of the message.",
        examples=["Hello, world!"],
    )
    tool_calls: list[ToolCall] = Field(
        description="Tool calls in the message.",
        default=[],
    )
    tool_call_id: str | None = Field(
        description="Tool call that this message is responding to.",
        default=None,
        examples=["call_Jja7J89XsjrOLA5r!MEOW!SL"],
    )
    run_id: str | None = Field(
        description="Run ID of the message.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    response_metadata: dict[str, Any] = Field(
        description="Response metadata. For example: response headers, logprobs, token counts.",
        default={},
    )
    custom_data: dict[str, Any] = Field(
        description="Custom message data.",
        default={},
    )

    def pretty_repr(self) -> str:
        """Get a pretty representation of the message."""
        
        base_title = self.type.title() + " Message"
        padded = " " + base_title + " "
        sep_len = (80 - len(padded)) // 2
        sep = "=" * sep_len
        second_sep = sep + "=" if len(padded) % 2 else sep
        title = f"{sep}{padded}{second_sep}"
        return f"{title}\n\n{self.content}"

    def pretty_print(self) -> None:
        print(self.pretty_repr())  # noqa: T201


class ChatResponse(BaseModel):
    """Response wrapper with status and data."""

    status: Literal["pending", "error", "success"] = Field(
        description="Status of the response.",
        examples=["pending", "success", "error"],
    )
    data: ChatMessage | dict[str, Any] | None = Field(
        description="Content of the response or error info.",
        default=None,
    )


class Feedback(BaseModel):  # type: ignore[no-redef]
    """Feedback for a run, to record to LangSmith."""

    run_id: str = Field(
        description="Run ID to record feedback for.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    key: str = Field(
        description="Feedback key.",
        examples=["human-feedback-stars"],
    )
    score: float = Field(
        description="Feedback score.",
        examples=[0.8],
    )
    kwargs: dict[str, Any] = Field(
        description="Additional feedback kwargs, passed to LangSmith.",
        default={},
        examples=[{"comment": "In-line human feedback"}],
    )


class FeedbackResponse(BaseModel):
    status: Literal["success"] = "success"


class ChatHistoryInput(BaseModel):
    """Input for retrieving chat history."""

    thread_id: str = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )


class ChatHistory(BaseModel):
    messages: list[ChatMessage]


class ChatHistoryResponse(BaseModel):
    """Response wrapper for chat history."""

    status: Literal["pending", "error", "success"] = Field(
        description="Status of the response.",
        examples=["pending", "success", "error"],
    )
    data: ChatHistory | dict[str, Any] | None = Field(
        description="Chat history or error details.",
        default=None,
    )
