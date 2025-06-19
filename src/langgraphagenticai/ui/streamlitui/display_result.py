import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    @staticmethod
    def print_chat_history(usecase):
        if usecase in ["Basic Chatbot", "Chatbot with Search"]:
            # Mostrar todo el historial (soporta dicts y objetos LangChain)
            for msg in st.session_state["chat_history"]:
                # Si es un dict (antiguo), usa las claves
                if isinstance(msg, dict):
                    role = msg.get("role")
                    content = msg.get("content")
                # Si es un objeto LangChain, usa sus atributos
                elif hasattr(msg, "type") and hasattr(msg, "content"):
                    role = msg.type  # 'human', 'ai', etc.
                    content = msg.content
                else:
                    continue

                if role in ["user", "human"]:
                    with st.chat_message("user"):
                        st.write(content)
                else:
                    with st.chat_message("assistant"):
                        st.write(content)

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message

        if usecase in ["Basic Chatbot", "Chatbot with Search"]:
            
            # Añadir el mensaje del usuario al historial
            if user_message:
                st.session_state["chat_history"].append({"role": "user", "content": user_message})

            # Pasar todo el historial al grafo
            state = {"messages": st.session_state["chat_history"]}
            res = graph.invoke(state)

            # Actualizar historial con la respuesta del grafo
            st.session_state["chat_history"] = res["messages"]

            self.print_chat_history(usecase)

        elif usecase == "News Summarizer":
            frequency = self.user_message["frequency"]
            topic = self.user_message["topic"]
            with st.spinner("Obteniendo y resumiendo noticias... ⏳"):
                graph.invoke({"frequency": frequency, "topic": topic})
                NEWS_PATH = f"./news/{topic}-{frequency}_summary.md"
                try:
                    # Leer el archivo markdown
                    with open(NEWS_PATH, "r") as file:
                        markdown_content = file.read()

                    # Mostrar el contenido markdown en Streamlit
                    st.markdown(markdown_content, unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error(f"Noticias no generadas o archivo no encontrado: {NEWS_PATH}")
                except Exception as e:
                    st.error(f"Ocurrió un error: {str(e)}")
                with open(NEWS_PATH, 'r') as f:
                    st.download_button(
                        "💾 Descargar Resumen",
                        f.read(),
                        file_name=f"{topic}-{frequency}_summary.md"
                    )
                st.success(f"✅ Resumen guardado en {NEWS_PATH}")
