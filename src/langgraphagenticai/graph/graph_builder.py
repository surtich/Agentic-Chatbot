from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.nodes.news_node import NewsNode
from src.langgraphagenticai.state.news_state import NewsState
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.tools.search_tool import get_tools,create_tool_node
from src.langgraphagenticai.nodes.chatbot_with_Tool_node import ChatbotWithToolNode


class GraphBuilder:
    def __init__(self, llm):
        self.llm = llm

    def basic_chatbot_build_graph(self):
        """
        Construye un grafo básico para un chatbot.
        """
        self.graph_builder = StateGraph(State) 

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

        self.graph_builder = StateGraph(State) 

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

    def news_build_graph(self):

        self.graph_builder = StateGraph(NewsState)

        # Initialize the AINewsNode
        ai_news_node = NewsNode(self.llm)

        self.graph_builder.add_node("fetch_news", ai_news_node.fetch_news)
        self.graph_builder.add_node("summarize_news", ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result", ai_news_node.save_result)

        self.graph_builder.set_entry_point("fetch_news")
        self.graph_builder.add_edge("fetch_news", "summarize_news")
        self.graph_builder.add_edge("summarize_news", "save_result")
        self.graph_builder.add_edge("save_result", END)

    def setup_graph(self, usecase):
        """
        Configura el grafo basado en el caso de uso seleccionado.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        elif usecase == "Chatbot with Search":
            self.chatbot_with_tools_build_graph()
        elif usecase == "News Summarizer":
            self.news_build_graph()
        
        else:
            raise ValueError(f"Caso de uso '{usecase}' no es compatible.")

        return self.graph_builder.compile()

