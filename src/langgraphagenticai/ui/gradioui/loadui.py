import copy
import os
import uuid
import gradio as gr
from src.langgraphagenticai.LLMS.llm import LLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder, checkpointer
from src.langgraphagenticai.ui.uiconfigfile import Config
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Cargar variables de entorno desde .env en la raíz del proyecto (por defecto)
load_dotenv(override=True)
config =  Config()

def get_provider_dropdown():
    provider_options = config.get_provider_options()
    return gr.Dropdown(
        label="Selecciona un proveedor LLM",
        choices=config.get_provider_options(),
        value=provider_options[0] if provider_options else None,
        interactive=True
    )

def get_model_dropdown(provider):
    model_options = config.get_model_options(provider)
    return gr.Dropdown(
        label="Selecciona un modelo LLM",
        choices=model_options,
        value=model_options[0] if model_options else None,
        interactive=True
    )

def get_base_url_box(provider):
    base_url = config.get_base_url(provider)
    return gr.Textbox(
        label="Base URL",
        value=base_url if base_url else "",
        placeholder="Base URL",
        interactive=True  # Only enable if base_url is provided
    )

def get_api_key(provider):
    api_key_label = f"{provider.upper()}_API_KEY"
    api_key_env = os.getenv(api_key_label, "")

    return (api_key_label, api_key_env)

def get_time_frame_dropdown():
    return gr.Dropdown(
        label="Selecciona el periodo de tiempo",
        choices=[
            ("Diario", "daily"),
            ("Semanal", "weekly"),
            ("Mensual", "monthly"),
            ("Anual", "yearly")
        ],
        value="daily",
        interactive=True
    )


def show_warning(value):
    warning_text = f"⚠️ Por favor, introduce un valor para continuar."
    return gr.Markdown(value=warning_text, visible=value.strip() == "")

def password_with_eye(label, value="", placeholder="Introduce tu clave"):
    visible=False
    
    
    def updater(label, value):        
        textbox = gr.Textbox(
            label=label,
            value=value,
            type="text" if visible else "password",
            placeholder=placeholder,
            interactive=True,
            scale=5
        )

        
        return textbox
    
    with gr.Row():        
        textbox = updater(label, value)  
        
        # Función para alternar el tipo del campo
        def toggle_visibility():
            nonlocal visible
            visible = not visible
            textbox = gr.Textbox(
                type="text" if visible else "password",
            )
            toggle_btn = gr.Button("👁️" if visible else "🙈")
            return toggle_btn, textbox
        
        # Conectar el botón con la función de alternar visibilidad
        toggle_btn = gr.Button("🙈", size="sm", scale=1, min_width=40)
        toggle_btn.click(
            fn=toggle_visibility,
            inputs=[],
            outputs=[toggle_btn, textbox]
        )

        with gr.Row():
            warning_md = show_warning(value)

        # Conectar el evento de cambio del textbox para mostrar la advertencia
        textbox.change(
            fn=show_warning,
            inputs=[textbox],
            outputs=[warning_md]
        )        

    return toggle_btn, textbox, updater

def get_api_key_box(provider, api_key_updater):
    api_key_label, api_key_env = get_api_key(provider)
    api_key_box = api_key_updater(api_key_label, api_key_env)
    return api_key_box

def get_usecase_dropdown():
    usecase_options = config.get_usecase_options()
    return gr.Dropdown(
        label="Selecciona un caso de uso",
        choices=usecase_options,
        value=usecase_options[0] if usecase_options else None,
        interactive=True
    )

def get_conversations(usecase="Basic Chatbot"):
    conversations = gr.State([("Conversación 1", str(uuid.uuid4())) ])
    show = usecase in ["Basic Chatbot", "Chatbot with Search"]
    with gr.Group(visible=show) as conversations_container:
        with gr.Row():
            gr.Markdown("### Conversaciones 💬 ")
        with gr.Row():
            plus_btn = gr.Button("➕ Añadir", scale=1, size="sm", min_width=40)
            minus_btn = gr.Button("❌ Borrar", scale=1, size="sm", min_width=40, interactive=False)
        with gr.Row():
            conversations_dropdown = gr.Dropdown(
                choices=conversations.value,
                label="Selecciona conversación",
                interactive=True
            )

        plus_btn.click(
            fn=add_conversation,
            inputs=[conversations],
            outputs=[conversations, conversations_dropdown, minus_btn]
        )

        minus_btn.click(
            fn=del_conversation,
            inputs=[conversations, conversations_dropdown],
            outputs=[conversations, conversations_dropdown, minus_btn]
        )

    return conversations_container, conversations_dropdown

def add_conversation(conversations):
    new_id = str(uuid.uuid4())
    next_number = max([int(v.split(" ")[1]) for v,k in conversations]) + 1
    new_label = f"Conversación {next_number}"
    conversations.append((new_label, new_id))
    conversations_dropdown = gr.Dropdown(
        choices=conversations,
        value=new_id
    )
    minus_btn = gr.Button(interactive=len(conversations) > 1)
    return conversations, conversations_dropdown, minus_btn

def del_conversation(conversations, conversation_id):
    conversations = conversations if len(conversations) <= 1 else [c for c in conversations if c[1] != conversation_id]
    conversations_dropdown = gr.Dropdown(
        choices=conversations,
        value=conversations[0][1] if conversations else None
    )
    minus_btn = gr.Button(interactive=len(conversations) > 1)
    checkpointer.delete_thread(conversation_id)  # Eliminar la conversación del checkpointer
    return conversations, conversations_dropdown, minus_btn

def get_news(usecase="Basic Chatbot"):
    show = usecase in ["News Summarizer"]
    with gr.Group(visible=show) as news_container:
        with gr.Row():
            gr.Markdown("### 📰 News Explorer")
        with gr.Row():
            _, tavily_api_key_box, _ = password_with_eye("TAVILY_API_KEY", os.getenv("TAVILY_API_KEY", ""))
            time_frame_dropdown = get_time_frame_dropdown()
            topic_box = gr.Textbox(
                type="text",
                label="Tema",
                placeholder="Introduce un tema",
                value="Real Madrid",
                interactive=True,
            )
            news_btn = gr.Button(f"🔍 Noticias de {topic_box.value}")

            topic_box.input(
                fn=lambda value: gr.Button(value=f"🔍 Noticias de {value}" if value.strip() else "↑ ↑ ↑ Introduce un tema ↑ ↑ ↑", interactive=len(value.strip()) >= 2),
                inputs=[topic_box],
                outputs=[news_btn]
            )

    return news_container, tavily_api_key_box, time_frame_dropdown, topic_box, news_btn

def toggle_conversations(usecase):
    show = usecase in ["Basic Chatbot", "Chatbot with Search"]
    return gr.Group(visible=show), gr.Chatbot(visible=show, type="messages"), gr.Textbox(visible=show), gr.Markdown(visible=not show)

def toggle_news(usecase):
    show = usecase in ["News Summarizer"]
    return gr.Group(visible=show), gr.Chatbot(visible=not show, type="messages"), gr.Textbox(visible=not show), gr.Markdown(visible=show)    

# Inicializa un estado para guardar el LLM y los parámetros actuales
def initialize_llm_state():
    return {"llm": None, "params": None}

def initialize_graph_state():
    return {"graph": None, "params": None}

# Función para crear o reutilizar el LLM
def get_or_create_llm(llm_state, provider, model, api_key, base_url):
    # Construye el diccionario de parámetros actuales
    params = {
        "selected_llm": provider,
        "selected_model": model,
        "API_KEY": api_key,
        "BASE_URL": base_url
    }
    # Si los parámetros han cambiado, crea un nuevo LLM
    if llm_state["params"] != params:
        llm_instance = LLM(params)
        llm = llm_instance.get_llm_model()
        llm_state["llm"] = llm
        llm_state["params"] = copy.deepcopy(params)
    # Si no han cambiado, reutiliza el LLM
    return llm_state["llm"]

def get_or_create_graph(graph_state, llm, usecase):
    # Construye el diccionario de parámetros actuales
    params = {
        "llm": llm,
        "usecase": usecase
    }
    # Si los parámetros han cambiado, crea un nuevo LLM
    if graph_state["params"] != params:
        graph_builder = GraphBuilder(llm)
        graph, _ = graph_builder.setup_graph(usecase)
        graph_state["graph"] = graph
        graph_state["params"] = params
    # Si no han cambiado, reutiliza el LLM
    return graph_state["graph"]

def get_current_history(conversation_id, graph):
    if not graph:
        return []
    thread_id = conversation_id
    history = graph.get_state_history(
        config={"configurable": {"thread_id": thread_id}}
    )

    history = list(history)
    return history[0].values["messages"] if len(history) > 0 else []

def langchain_history_to_gradio_messages(history):
    gradio_history = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            gradio_history.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            gradio_history.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, ToolMessage):
            gradio_history.append({"role": "assistant", "content": f"🛠️ Tool: {msg.content}"})
    return gradio_history


# Callback para procesar el mensaje del usuario
def chat(user_message, chat_history, provider, model, api_key, base_url, usecase, conversation_dropdown, llm_state, graph_state):
    llm = get_or_create_llm(llm_state, provider, model, api_key, base_url)
    if llm is None:
        return chat_history + [("Error", "No se pudo crear el modelo LLM.")], llm_state, graph_state

    graph = get_or_create_graph(graph_state, llm, usecase)
    if graph is None:
        return chat_history + [("Error", "No se pudo crear el grafo.")], llm_state, graph_state
    
    config = {"configurable": {"thread_id": conversation_dropdown}}

    response = graph.invoke({"messages": [{"role": "user", "content": user_message}]}, config=config)
    # Extrae solo el texto
    
    chat_history = chat_history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response["messages"][-1].content}
    ]
    return chat_history, "", llm_state, graph_state

def news_summarizer(frequency, topic, provider, model, api_key, base_url, usecase, conversation_dropdown, llm_state, graph_state):
    llm = get_or_create_llm(llm_state, provider, model, api_key, base_url)
    if llm is None:
        return gr.Markdown("Error: No se pudo crear el modelo LLM."), llm_state, graph_state

    graph = get_or_create_graph(graph_state, llm, usecase)
    if graph is None:
        return gr.Markdown("Error: No se pudo crear el grafo."), llm_state, graph_state
    
    graph.invoke({"frequency": frequency, "topic": topic})
    NEWS_PATH = f"./news/{topic}-{frequency}_summary.md"
    try:
        # Leer el archivo markdown
        with open(NEWS_PATH, "r") as file:
            markdown_content = file.read()

    except FileNotFoundError:
        return gr.Markdown(f"Noticias no generadas o archivo no encontrado: {NEWS_PATH}"), llm_state, graph_state
    except Exception as e:
        return gr.Markdown(f"Ocurrió un error: {str(e)}"), llm_state, graph_state
    
    return gr.Markdown(f"{markdown_content}<br>✅ Resumen guardado en {NEWS_PATH}"), llm_state, graph_state

title="🤖 " + config.get_page_title()

css="""
    #main-container {
        display: flex;
        flex-direction: column;
        height: 95vh;
    }
    #chatbot {
        flex: 1 1 auto;
    },
    #news { 
        flex: 1 1 auto;
    }
"""

with gr.Blocks(title = title, css=css) as demo:

    # Estado oculto para guardar el LLM y los parámetros
    llm_state = gr.State(initialize_llm_state())
    graph_state = gr.State(initialize_graph_state())

    with gr.Sidebar(position="left"):
            provider_dropdown = get_provider_dropdown()
            model_dropdown = get_model_dropdown(provider_dropdown.value)
            base_url_box = get_base_url_box(provider_dropdown.value)
            
            api_key_label, api_key_env = get_api_key(provider_dropdown.value)
            _, api_key_box, api_key_updater = password_with_eye(api_key_label, api_key_env)

            usecase_dropdown = get_usecase_dropdown()

            conversations_panel, conversation_dropdown = get_conversations(usecase_dropdown.value)

            news_panel, tavily_api_key_box, time_frame_dropdown, topic_box, news_btn = get_news(usecase_dropdown.value)
    
    with gr.Column(elem_id="main-container"):
        gr.Markdown(f"# {title}")
        chatbot = gr.Chatbot(elem_id="chatbot", type="messages")
        msg = gr.Textbox(label="", placeholder="Escribe tu mensaje...")
        news_summary = gr.Markdown(visible=False)
   
    msg.submit(
        chat,
        inputs=[msg, chatbot, provider_dropdown, model_dropdown, api_key_box, base_url_box, usecase_dropdown, conversation_dropdown, llm_state, graph_state],
        outputs=[chatbot, msg, llm_state, graph_state]
    )

    news_btn.click(
        news_summarizer,
        inputs=[time_frame_dropdown, topic_box, provider_dropdown, model_dropdown, api_key_box, base_url_box, usecase_dropdown, conversation_dropdown, llm_state, graph_state],
        outputs=[news_summary, llm_state, graph_state],
        show_progress='full',
        show_progress_on=news_btn
    )

    provider_dropdown.change(
        fn=get_model_dropdown,
        inputs=[provider_dropdown],
        outputs=[model_dropdown]
    )

    provider_dropdown.change(
        fn=get_base_url_box,
        inputs=[provider_dropdown],
        outputs=[base_url_box]
    )

    provider_dropdown.change(
        fn=get_base_url_box,
        inputs=[provider_dropdown],
        outputs=[base_url_box]
    )

    provider_dropdown.change(
        fn=lambda provider: get_api_key_box(provider, api_key_updater),
        inputs=[provider_dropdown],
        outputs=[api_key_box]
    )

    usecase_dropdown.change(
        fn=toggle_conversations,
        inputs=[usecase_dropdown],
        outputs=[conversations_panel, chatbot, msg, news_summary]
    )

    usecase_dropdown.change(
        fn=toggle_news,
        inputs=[usecase_dropdown],
        outputs=[news_panel, chatbot, msg, news_summary]
    )

    conversation_dropdown.change(
        fn=lambda conversation_id, graph_state: langchain_history_to_gradio_messages(get_current_history(conversation_id, graph_state["graph"])),
        inputs=[conversation_dropdown, graph_state],
        outputs=[chatbot]
    )

if __name__ == "__main__":
    demo.launch()