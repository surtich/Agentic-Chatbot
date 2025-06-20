import streamlit as st
from pydantic import SecretStr
import importlib

PROVIDERS = {
    "groq": ("langchain_groq", "ChatGroq"),
    "gemini": ("langchain_google_genai", "ChatGoogleGenerativeAI"),
    "cohere": ("langchain_cohere", "ChatCohere"),
    "openrouter": ("langchain_community.chat_models", "ChatOpenAI"),
    "together": ("langchain_together", "ChatTogether"),
    "github": ("langchain_community.chat_models", "ChatOpenAI"),
}

def get_llm_class(provider):
    module_name, class_name = PROVIDERS[provider]
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def instantiate_llm(provider, model, api_key, base_url=None):
    ChatLLM = get_llm_class(provider.lower())
    if not ChatLLM:
        return None
    if base_url:
        return ChatLLM(model_name=model, openai_api_key=api_key, openai_api_base=base_url)
    return ChatLLM(model=model, api_key=SecretStr(api_key))

class LLM:
    def __init__(self, user_controls_input: dict[str, str]):
        self.user_controls_input = user_controls_input

    def get_llm_model(self):
        try:
            selected_llm = self.user_controls_input["selected_llm"]
            api_key = self.user_controls_input.get("API_KEY", '')
            selected_model = self.user_controls_input["selected_model"]
            if api_key == '':
                st.error("La API Key es necesaria para continuar.")
                return None
            
            base_url = self.user_controls_input.get("BASE_URL", None)

            llm = instantiate_llm(selected_llm, selected_model, api_key, base_url)

            return llm
        
        except Exception as e:
            raise ValueError(f"Error al crear el modelo LLM: {e}")
        