from langgraph.graph import StateGraph, START, END

from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.state.state import State

class GraphBuilder:
    def __init__(self, llm):
        self.llm = llm
        self.graph_builder = StateGraph(State)

    def basic_chatbot_build_graph(self):
        """
        Construye un grafo básico para un chatbot.
        """

        self.basic_chatbot_node = BasicChatbotNode(self.llm)

        self.graph_builder.add_node("chatbot", self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)

    def setup_graph(self, usecase):
        """
        Configura el grafo basado en el caso de uso seleccionado.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        else:
            raise ValueError(f"Caso de uso '{usecase}' no es compatible.")

        return self.graph_builder.compile()

