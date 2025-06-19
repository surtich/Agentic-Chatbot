from src.langgraphagenticai.state.state import State

class ChatbotWithToolNode:
    """
    Lógica de chatbot mejorada con integración de herramientas.
    """
    def __init__(self, llm):
        self.llm = llm

    def process(self, state: State) -> State:
        """
        Procesa el estado de entrada y genera una respuesta con integración de herramientas.
        Esto no se está usando. Está previsto para implementar la lógica cuando el agente no use directamente las tools, sino que s ele proporcionan como contexto.
        """
        user_input = state["messages"][-1] if state["messages"] else ""
        llm_response = self.llm.invoke([{"role": "user", "content": user_input}])

        # Simular lógica específica de la herramienta
        tools_response = f"Integración de herramientas para: '{user_input}'"

        return {"messages": [llm_response, tools_response]}
    
    def create_chatbot(self, tools):
        """
        Devuelve una función de nodo de chatbot.
        """
        llm_with_tools = self.llm.bind_tools(tools)

        def chatbot_node(state: State) -> State:
            """
            Lógica del chatbot para procesar el estado de entrada y devolver una respuesta.
            """
            return {"messages": [llm_with_tools.invoke(state["messages"])]}

        return chatbot_node
