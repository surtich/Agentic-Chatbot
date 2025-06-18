import streamlit as st
from src.langgraphagenticai.LLMS.llm import LLM
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

    user_message = st.chat_input("Escribe tu mensaje")

    if user_message:

        llm = LLM(user_controls_input=user_input).get_llm_model()

        if not llm:
            st.error("Error: No se pudo crear el modelo LLM.")
            return

        response = llm.invoke(user_message)

        print("Response:", response.content)