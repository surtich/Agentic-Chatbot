import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


class DisplayResultStreamlit:
    def __init__(self, usecase, graph, checkpointer):
        self.usecase = usecase
        self.graph = graph
        self.checkpointer = checkpointer

    def get_current_history(self):
        thread_id = st.session_state.selected_conversation
        history = self.graph.get_state_history(
            config={"configurable": {"thread_id": thread_id}}
        )

        history = list(history)
        return history[0].values["messages"] if len(history) > 0 else []


    def print_chat_history(self):  
        if self.usecase in ["Basic Chatbot", "Chatbot with Search"]:
            history = self.get_current_history()
            for msg in history:
                content = msg.get("content") if isinstance(msg, dict) else msg.content 
                role = msg.get("role") if isinstance(msg, dict) else msg.type if hasattr(msg, "type") else "tool"
                if not content or not role:
                    continue
               
                # Mostrar según el rol
                if role in ["user", "human"]:
                    with st.chat_message("user"):
                        st.write(content)
                elif role in ["ai", "assistant"]:
                    with st.chat_message("assistant"):
                        st.write(content)
                elif role == "tool":
                    with st.chat_message("assistant"):
                        st.write(f"🛠️ Tool: {content}")

    def display_result_on_ui(self, user_message):
        usecase = self.usecase
        graph = self.graph

        if usecase in ["Basic Chatbot", "Chatbot with Search"]:          
            
            # Pasar todo el historial al grafo
            config = {"configurable": {"thread_id": st.session_state.selected_conversation}}

            graph.invoke({"messages": [{"role": "user", "content": user_message}]}, config=config)
            self.print_chat_history()
            
        elif usecase == "News Summarizer":
            frequency = user_message["frequency"]
            topic = user_message["topic"]
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
