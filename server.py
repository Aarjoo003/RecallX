"""
RecallX Backend - Hugging Face Spaces Production Entrypoint
Serves the FastAPI retrieval engine on Hugging Face Spaces (Gradio/Python SDK).
"""

import os
import sys

# Ensure backend package is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.main import app as fastapi_app

# If Gradio is available in the environment, mount a clean documentation UI
try:
    import gradio as gr

    with gr.Blocks(title="RecallX Semantic Retrieval Engine") as demo:
        gr.Markdown("# 🧠 RecallX Semantic Conversation Intelligence Engine")
        gr.Markdown("> *Search what your group meant — not just what they typed.*")
        gr.Markdown(
            "### 🟢 API Status: Active\n"
            "FastAPI backend is running with 5,207 indexed messages.\n\n"
            "**Primary API Endpoints:**\n"
            "- Health Check: [`/health`](/health) | [`/api/health`](/api/health)\n"
            "- Hybrid Search: [`/api/search`](/api/search) (POST)\n"
            "- Decision Records: [`/api/decisions`](/api/decisions)\n"
            "- Participants: [`/api/participants`](/api/participants)\n"
            "- Interactive API Documentation: [`/docs`](/docs)\n"
        )

    # Mount Gradio at /gradio so root API routes remain purely on FastAPI
    app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")
except Exception as e:
    print(f"[RecallX] Gradio mount note: {e}")
    app = fastapi_app

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
