import streamlit as st
import os
from dotenv import load_dotenv
from src.langgraphagenticai.ui.uiconfigfile import Config

# Cargar variables de entorno desde .env en la raíz del proyecto (por defecto)
load_dotenv()

class LoadStreamlitUI:
    def __init__(self):
        self.config =  Config() # config
        self.user_controls = {}

    def load_streamlit_ui(self):
        st.set_page_config(page_title= "🤖 " + self.config.get_page_title(), layout="wide")
        st.header("🤖 " + self.config.get_page_title())

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
            self.user_controls["API_KEY"] = st.text_input("API Key", value=api_key_env, type="password", autocomplete="off")
            if not self.user_controls["API_KEY"]:
                st.warning(f"⚠️ Please enter your {api_key_label} to proceed.")

            # Use case selection
            self.user_controls["selected_usecase"] = st.selectbox("Select Usecases", usecase_options)

        return self.user_controls