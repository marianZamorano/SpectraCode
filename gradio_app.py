import gradio as gr
import requests
import json
import threading
import time

def analyze_zip(zip_file):
    with open(zip_file.name, "rb") as f:
        files = {"file": f}
        response = requests.post("http://127.0.0.1:8000/analyze-repo", files=files)
    if response.status_code == 200:
        return response.content, "resultados.json"
    return None, "Error en análisis"

def live_progress():
    import websocket
    def on_message(ws, message):
        data = json.loads(message)
        yield f"{data['file']} → {data['ai_probability']}% IA\n"
    ws = websocket.WebSocketApp("ws://127.0.0.1:8000/ws/analyze", on_message=on_message)
    ws.run_forever()

iface = gr.Interface(
    fn=analyze_zip,
    inputs=gr.File(label="Sube ZIP del repositorio"),
    outputs=[gr.File(label="JSON Resultados"), gr.File(label="Nombre")],
    title="CodeGuard AI",
    description="Detecta IA + explica + parchea vulnerabilidades",
    live=True
)

if __name__ == "__main__":
    iface.launch()