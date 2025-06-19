import streamlit as st
from src.langgraphagenticai.LLMS.llm import LLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI

# INICIO de la función PRINCIPAL
def load_langgraph_agenticai_app():
    """
    Carga y ejecuta la aplicación LangGraph AgenticAI con la interfaz de usuario de Streamlit.
    Esta función inicializa la interfaz de usuario, maneja la entrada del usuario, configura el modelo LLM,
    configura el grafo basándose en el caso de uso seleccionado y muestra la salida mientras
    implementa el manejo de excepciones para mayor robustez.
    """
   
    # Cargar interfaz de usuario
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: No se pudo cargar la entrada del usuario desde la interfaz de usuario.")
        return
    

    usecase = user_input["selected_usecase"]

    if not usecase:
        st.error("Error: No se ha seleccionado un caso de uso.")
        return
    
    
    if usecase in ["Basic Chatbot", "Chatbot with Search"]:
        user_message = st.chat_input("Escribe tu mensaje")
    elif st.session_state.IsFetchButtonClicked:
        user_message = {"frequency": st.session_state.timeframe, "topic": st.session_state.topic}
    else:
        user_message = None

    try:
        llm = LLM(user_controls_input=user_input).get_llm_model()

        if not llm:
            st.error("Error: No se pudo crear el modelo LLM.")
            return
        
        graph_builder = GraphBuilder(llm)

        try:
            graph, checkpointer = graph_builder.setup_graph(usecase)
            display = DisplayResultStreamlit(usecase, graph, checkpointer)

            if st.session_state.get("to_remove_conversation"):
                print(f"Eliminando conversación: {st.session_state.to_remove_conversation}")
                checkpointer.delete_thread(st.session_state.to_remove_conversation)
                st.session_state.to_remove_conversation = None
            
            if user_message:
                print(f"Procesando mensaje del usuario: {user_message}")
                display.display_result_on_ui(user_message)
            else:
                print("Mostrando historial de chat")
                display.print_chat_history()           

        except ValueError as e:
            st.error(f"Error al configurar el grafo: {e}")
            return
    
    except Exception as e:
        raise ValueError(f"Ha ocurrido un error: {e}")

   