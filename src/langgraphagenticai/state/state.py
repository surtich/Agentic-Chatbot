from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    """
     Representa el estado del grafo
    """
    messages: Annotated[List, add_messages]