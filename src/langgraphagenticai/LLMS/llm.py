import streamlit as st
from pydantic import SecretStr

from langchain_groq import ChatGroq as ChatLLM

class LLM:
    def __init__(self, user_controls_input: dict[str, str]):
        self.user_controls_input = user_controls_input

    def get_llm_model(self):
        try:
            api_key = self.user_controls_input.get("API_KEY", '')
            selected_model = self.user_controls_input["selected_model"]
            if api_key == '':
                st.error("La API Key es necesaria para continuar.")
            
            llm = ChatLLM(
                model=selected_model,
                api_key=SecretStr(api_key)  # Use SecretStr for sensitive data
            )

            return llm
        
        except Exception as e:
            raise ValueError(f"Error al crear el modelo LLM: {e}")
        