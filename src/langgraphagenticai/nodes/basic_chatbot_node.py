from src.langgraphagenticai.state.state import State

class BasicChatbotNode:
    """
    Una implementación básica de un nodo de chatbot que responde a mensajes. 
    """

    def __init__(self, llm):
        self.llm = llm

    def process(self, state: State) -> State:
        """
        Procesa el mensaje del usuario y genera una respuesta utilizando el modelo LLM.
        """
        
        return {"messages": self.llm.invoke(state['messages'])}