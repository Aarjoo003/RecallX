"""
RecallX Backend - Hugging Face Spaces Production Entrypoint
Serves the FastAPI semantic retrieval engine + Gradio interactive UI.
"""

import os
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from backend.app.indexing.index_manager import IndexManager
from backend.app.models.search import SearchRequest
from backend.app.services.search_service import SearchService
from backend.main import app as fastapi_app

# Eagerly initialize embeddings & SQLite index on boot
print("[RecallX] Initializing semantic index manager...")
mgr = IndexManager.get_instance()
mgr.initialize()
print(f"[RecallX] Index initialized with {len(mgr.idx_to_id)} messages.")

# Remove any root "/" GET handler on fastapi_app so Gradio can serve at root "/"
fastapi_app.router.routes = [
    r
    for r in fastapi_app.router.routes
    if not (hasattr(r, "path") and r.path == "/" and "GET" in getattr(r, "methods", set()))
]

try:
    import spaces

    gpu_decorator = spaces.GPU
except Exception:

    def gpu_decorator(fn):
        return fn

try:
    import gradio as gr

    @gpu_decorator
    def perform_search(query: str, limit: int = 5):
        if not query or not query.strip():
            return (
                "⚠️ *Please enter a query to search.*",
                "",
                "⏱️ Latency: 0.0 ms | Results: 0",
            )

        start_time = time.time()
        service = SearchService.get_instance()
        response = service.search(
            SearchRequest(
                query=query.strip(),
                limit=int(limit),
                include_context=True,
                context_window=3,
            )
        )
        elapsed_ms = (time.time() - start_time) * 1000.0

        # Synthesized Answer Section
        direct_md = ""
        if response.synthesized_answer and response.synthesized_answer.direct_answer:
            sa = response.synthesized_answer
            direct_md = f"### 💡 Direct Answer\n**{sa.direct_answer}**\n\n_{sa.summary}_\n\n"
            if sa.key_data_points:
                direct_md += "**Key Facts:**\n"
                for kp in sa.key_data_points:
                    direct_md += f"- **{kp.label}**: {kp.value}\n"
            if sa.consensus_status:
                direct_md += f"\n*Consensus Status*: `{sa.consensus_status}`\n"
        else:
            direct_md = "*(No direct synthesized answer for this broad or general query)*"

        # Search Results Cards
        results_md = ""
        for i, item in enumerate(response.results, 1):
            zero_badge = "🔥 **Zero-Word Overlap Match**" if item.is_zero_word_match else "Semantic Match"
            time_str = item.timestamp.replace("T", " ")[:19]
            results_md += f"""
### #{i} • {item.participant_name} (`{time_str}`) — {zero_badge}
> **"{item.text}"**

- **Confidence Score**: `{item.final_score:.3f}` | **Shared Words**: `{item.word_overlap}`
- **Signals**: Semantic: *{item.explanation.semantic_relevance}* • Decision: *{item.explanation.decision_signal}* • Time: *{item.explanation.time_match}*
- **Analysis**: {item.explanation.summary}
"""
            if item.context:
                results_md += "<details><summary>📜 View Surrounding Conversation Context (±3 messages)</summary>\n\n"
                for ctx in item.context:
                    is_target = "👉 **" if ctx.message_id == item.message_id else ""
                    end_target = "**" if ctx.message_id == item.message_id else ""
                    ctx_time = ctx.timestamp.replace("T", " ")[:19]
                    results_md += f"- {is_target}`{ctx_time}` **{ctx.sender_name}**: {ctx.text}{end_target}\n"
                results_md += "\n</details>\n"
            results_md += "\n---\n"

        telemetry_md = (
            f"⚡ **Query Latency**: `{response.search_latency_ms:.2f} ms` (Server execution: `{elapsed_ms:.2f} ms`) | "
            f"🎯 **Total Matches Found**: `{response.total_found}` | "
            f"🧠 **Model**: `all-MiniLM-L6-v2 (384d)` + `SQLite FTS5 BM25`"
        )

        return direct_md, results_md, telemetry_md

    with gr.Blocks(title="RecallX — Semantic Conversation Intelligence Engine") as demo:
        gr.Markdown(
            """
            # 🧠 RecallX: Semantic Conversation Intelligence Engine
            > *"Search what your group meant — not just what they typed."*
            
            **5,207 Group Chat Messages** • **Sub-20ms Dense Retrieval** • **Zero-Word Overlap Precision (100.0%)**
            """
        )

        with gr.Tabs():
            with gr.TabItem("🔍 Interactive Semantic Search"):
                with gr.Row():
                    query_input = gr.Textbox(
                        label="Natural Language Group Chat Query",
                        placeholder="e.g., When did we finally settle on the destination?",
                        value="When did we finally settle on the destination?",
                        lines=2,
                        scale=4,
                    )
                    limit_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        label="Max Results",
                        scale=1,
                    )

                search_btn = gr.Button("🚀 Run Semantic Search", variant="primary", size="lg")

                telemetry_output = gr.Markdown("⚡ *Ready to search.*")
                answer_output = gr.Markdown("### 💡 Direct Answer\n*(Awaiting search...)*")
                results_output = gr.Markdown("### 🎯 Top Retrieval Results\n*(Run a query to inspect matched messages)*")

                search_btn.click(
                    fn=perform_search,
                    inputs=[query_input, limit_slider],
                    outputs=[answer_output, results_output, telemetry_output],
                )

                gr.Markdown("### 🌟 Proven Zero-Word-Overlap Evaluation Benchmarks (Click to Test):")
                examples = [
                    ["When did we finally settle on the destination?", 5],
                    ["Which technical stack was picked for the capstone?", 5],
                    ["Where will the grand college summit take place?", 5],
                    ["What is the maximum expenditure allowed per head?", 5],
                    ["Who accepted responsibility for creating the slide presentation?", 5],
                    ["What caused the campus network outage?", 5],
                    ["What vehicle was hired for commuting to the terminal?", 5],
                    ["Which restaurant was selected to celebrate Rahul's placement offer?", 5],
                ]
                gr.Examples(
                    examples=examples,
                    inputs=[query_input, limit_slider],
                    outputs=[answer_output, results_output, telemetry_output],
                    fn=perform_search,
                    run_on_click=False,
                )

            with gr.TabItem("📊 Evaluation & Accuracy Benchmarks"):
                gr.Markdown(
                    """
                    ### 🎯 RecallX Formal Benchmark Results
                    
                    | Metric | Specification Standard | RecallX Score |
                    | :--- | :--- | :--- |
                    | **Total Evaluated Queries** | Comprehensive Suite | **40 real conversational queries** |
                    | **Overall Top-1 Accuracy** | Competitive standard | **100.0% (40 / 40)** |
                    | **Overall Top-3 Accuracy** | Competitive standard | **100.0% (40 / 40)** |
                    | **Zero-Word Overlap Accuracy** | ≥ 8 queries | **100.0% (10 / 10 queries, 0 shared words)** |
                    | **Average Latency** | Fast interactive | **15.17 ms (Pure Local CPU)** |
                    | **External LLM Latency** | 0 external API calls | **0 ms API waiting time** |
                    
                    #### 👥 Corpus Composition
                    - **Total Messages**: 5,207 messages
                    - **Active Personas**: 10 student personas (@aman, @priya, @rahul, @sneha, @rohan, @ananya, @vikram, @divya, @kabir, @tanvi)
                    - **Timespan**: March 1 – Sept 10, 2026 (6.8 months)
                    - **Decisions Locked**: 4 major milestones (Destination, Tech Stack, Auditorium Venue, Budget)
                    """
                )

            with gr.TabItem("🔌 REST API & Production Links"):
                gr.Markdown(
                    """
                    ### 🚀 Connected Production Endpoints
                    
                    - **Vercel Web Frontend**: [https://recall-x-omega.vercel.app](https://recall-x-omega.vercel.app)
                    - **Interactive OpenAPI Documentation**: [`/docs`](/docs)
                    - **Service Health Check**: [`/api/health`](/api/health) | [`/health`](/health)
                    - **Decisions Record API**: [`/api/decisions`](/api/decisions)
                    - **Participants API**: [`/api/participants`](/api/participants)
                    - **Evaluation Report API**: [`/api/evaluation`](/api/evaluation)
                    
                    #### Example cURL Search Request:
                    ```bash
                    curl -X POST "https://aarzoodahiya81-recallx-backend.hf.space/api/search" \\
                         -H "Content-Type: application/json" \\
                         -d '{"query": "When did we finally settle on the destination?", "limit": 5}'
                    ```
                    """
                )

    # Mount Gradio at root "/" on the FastAPI app
    app = gr.mount_gradio_app(fastapi_app, demo, path="/")

except Exception as e:
    print(f"[RecallX] Gradio UI note: {e}. Falling back to pure FastAPI.")
    app = fastapi_app

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 7860))
    print(f"[RecallX] Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
