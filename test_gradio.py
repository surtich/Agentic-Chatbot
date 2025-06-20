import gradio as gr

with gr.Blocks(title="Test") as demo:
    gr.Markdown("# ¡Hola Gradio!")

if __name__ == "__main__":
    demo.launch()
