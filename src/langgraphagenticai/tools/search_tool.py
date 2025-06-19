from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode

def get_tools():
    """
    Devuelve la lista de herramientas a utilizar en el chatbot
    """
    tools=[TavilySearchResults(max_results=10)]
    return tools

def create_tool_node(tools):
    """
    crea y devuelve un nodo de herramienta para el grafo
    """
    return ToolNode(tools=tools)
