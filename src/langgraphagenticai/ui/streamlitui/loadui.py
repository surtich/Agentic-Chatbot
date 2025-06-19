import streamlit as st
import os
import uuid
from dotenv import load_dotenv
from src.langgraphagenticai.ui.uiconfigfile import Config

# Cargar variables de entorno desde .env en la raíz del proyecto (por defecto)
load_dotenv(override=True)

def abbreviate_text(text, max_length=20):
    """
    Abrevia el texto a un máximo de max_length caracteres.
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

class LoadStreamlitUI:
    def __init__(self):
        self.config =  Config() # config
        self.user_controls = {}

    def handle_conversations(self):
      
        st.markdown("### Conversaciones 💬")

        if "conversations" not in st.session_state:
            st.session_state.conversations = {str(uuid.uuid4()): "Conversación 1"}
        if "selected_conversation" not in st.session_state:
            st.session_state.selected_conversation = list(st.session_state.conversations.keys())[0]

        def add_conversation():
            # Genera un nuevo número de conversación basado en el último número. Extrae el número del texto "conversación number" y calcula el máximo
            next_number = max([int(c.split(" ")[1]) for c in st.session_state.conversations.values()]) + 1
            st.session_state.conversations[str(uuid.uuid4())] = f"Conversación {next_number}"
            st.session_state.selected_conversation = list(st.session_state.conversations.keys())[-1]  # Selecciona la nueva

        def delete_conversation():
            if len(st.session_state.conversations) > 1:
                selected = st.session_state.selected_conversation
                del st.session_state.conversations[selected]
                st.session_state.to_remove_conversation = st.session_state.selected_conversation
                # Selecciona la primera conversación restante
                st.session_state.selected_conversation = list(st.session_state.conversations.keys())[0]

        col1, col2 = st.columns(2)

        with col1:
            st.button("➕ Añadir", on_click=add_conversation)

        with col2:
            borrar_disabled = len(st.session_state.conversations) == 1
            st.button("❌ Borrar", on_click=delete_conversation, disabled=borrar_disabled)

        st.selectbox(
            "Selecciona una conversación",
            options=list(st.session_state.conversations.keys()),
            format_func=lambda x: st.session_state.conversations[x],
            key="selected_conversation",
        )

    def load_streamlit_ui(self):
        st.set_page_config(page_title= "🤖 " + self.config.get_page_title(), layout="wide")
        st.header("🤖 " + self.config.get_page_title())
        st.session_state.timeframe = ''
        st.session_state.topic = ''
        st.session_state.IsFetchButtonClicked = False

        with st.sidebar:
            # Get options from config
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)
            selected_llm = self.user_controls["selected_llm"]

            # Model selection dinámico
            model_options = self.config.get_model_options(selected_llm)
            self.user_controls[f"selected_model"] = st.selectbox("Select Model", model_options)
            # Base URL sólo se muestra si existe la configuración BASE_URL
            base_url = self.config.get_base_url(selected_llm)
            
            if base_url:
                self.user_controls["BASE_URL"] = st.text_input("Base URL", value=base_url)

            # API key input dinámico, pre-cargada desde .env si existe
            api_key_label = f"{selected_llm.upper()}_API_KEY"
            api_key_env = os.getenv(api_key_label, "")
            self.user_controls["API_KEY"] = st.session_state["API_KEY"] = st.text_input("API Key", value=api_key_env, type="password", autocomplete="off")
            if not self.user_controls["API_KEY"]:
                st.warning(f"⚠️ Por favor, introduce tu {api_key_label} para continuar.")

            # Use case selection
            self.user_controls["selected_usecase"] = st.selectbox("Select Usecases", usecase_options)

            # Mantener el estado para los casos de uso indicados
            if self.user_controls["selected_usecase"] in ["Basic Chatbot", "Chatbot with Search"]:
                self.handle_conversations()
        
            if self.user_controls["selected_usecase"] in ["Chatbot with Search", "News Summarizer"]:
                tavily_api_key = os.getenv("TAVILY_API_KEY", "")
                os.environ["TAVILY_API_KEY"] = self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = st.text_input("Tavily API Key", value=tavily_api_key, type="password", autocomplete="off")
                if not self.user_controls["TAVILY_API_KEY"]:
                    st.warning("⚠️ Por favor, introduce tu Tavily API Key para continuar.")
                elif self.user_controls['selected_usecase']=="News Summarizer":
                    st.subheader("📰 News Explorer ")
                    with st.sidebar:
                        time_frame = st.selectbox(
                            "📅 Selecciona el periodo",
                            ["daily", "weekly", "monthly", "yearly"],
                            index=0
                        )
                    self.user_controls['topic'] = st.text_input("Tema:", value="AI", placeholder="ej: AI, Real Madrid, etc.")
                    if st.button(f"🔍 Noticias de {abbreviate_text(self.user_controls['topic'])}" if self.user_controls['topic'] else "↑ ↑ ↑ Introduce tema ↑ ↑ ↑", use_container_width=True, disabled=(self.user_controls['topic'].strip() == "")):
                        st.session_state.IsFetchButtonClicked = True
                        st.session_state.timeframe = time_frame
                        st.session_state.topic = self.user_controls['topic'].strip()
                    else :
                        st.session_state.IsFetchButtonClicked = False                    

        return self.user_controls