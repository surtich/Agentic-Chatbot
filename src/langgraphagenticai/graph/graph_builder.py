from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.tools.search_tool import get_tools,create_tool_node
from src.langgraphagenticai.nodes.chatbot_with_Tool_node import ChatbotWithToolNode


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

    def chatbot_with_tools_build_graph(self):
        """
        Construye un grafo de chatbot avanzado con integración de herramientas.
        Este método crea un grafo de chatbot que incluye tanto un nodo de chatbot
        como un nodo de herramienta. Define herramientas, inicializa el chatbot con
        capacidades de herramienta y configura aristas condicionales y directas entre nodos.
        El nodo de chatbot se establece como el punto de entrada.
        """
        ## Definir la herramienta y el nodo de herramienta

        tools=get_tools()
        tool_node=create_tool_node(tools)

        ##Definir LLM
        llm = self.llm

        # Definir nodo de chatbot
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)

        # Añadir nodos
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools", tool_node)

        # Definir aristas condicionales y directas
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.add_edge("chatbot", END)

    def setup_graph(self, usecase):
        """
        Configura el grafo basado en el caso de uso seleccionado.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        elif usecase == "Chatbot with Search":
            self.chatbot_with_tools_build_graph()
        else:
            raise ValueError(f"Caso de uso '{usecase}' no es compatible.")

        return self.graph_builder.compile()

