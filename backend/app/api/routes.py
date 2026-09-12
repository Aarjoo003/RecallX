import json
import os
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from ..models.search import SearchRequest, SearchResponse, InterpretedFilters
from ..models.message import ContextMessage, Participant
from ..models.decision import DecisionItem
from ..services.search_service import SearchService
from ..services.export_service import ExportService
from ..retrieval.decision_detector import DecisionDetector
from ..retrieval.context_reconstructor import ContextReconstructor
from ..config import PARTICIPANTS_FILE, EVAL_DIR, QUESTIONS_FILE
from ..indexing.index_manager import IndexManager

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    mgr = IndexManager.get_instance()
    return {
        "status": "healthy",
        "service": "RecallX Semantic Retrieval Engine",
        "index_ready": mgr.is_ready,
        "indexed_messages": len(mgr.idx_to_id) if mgr.is_ready else 0,
        "version": "1.0.0"
    }

@router.post("/search", response_model=SearchResponse)
def search_messages(request: SearchRequest):
    if not request.query or not request.query.strip():
        return SearchResponse(
            query="",
            query_type="empty",
            interpreted_filters=InterpretedFilters(cleaned_query=""),
            total_found=0,
            search_latency_ms=0.0,
            results=[]
        )
    service = SearchService.get_instance()
    response = service.search(request)
    return response

@router.get("/messages/{message_id}")
def get_message_detail(message_id: str):
    mgr = IndexManager.get_instance()
    msg = mgr.get_message(message_id)
    if not msg:
        raise HTTPException(status_code=404, detail=f"Message '{message_id}' not found.")
    return msg

@router.get("/thread/{thread_id}", response_model=List[ContextMessage])
def get_thread(thread_id: str):
    reconstructor = ContextReconstructor()
    thread_msgs = reconstructor.get_full_thread(thread_id)
    if not thread_msgs:
        raise HTTPException(status_code=404, detail=f"Thread '{thread_id}' not found.")
    return thread_msgs

@router.get("/export/pdf")
def export_chat_pdf(
    thread_id: Optional[str] = Query(None),
    message_id: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    direct_answer: Optional[str] = Query(None)
):
    reconstructor = ContextReconstructor()
    mgr = IndexManager.get_instance()
    
    target_msg = None
    if message_id:
        target_msg = mgr.get_message(message_id)
        if target_msg and not thread_id:
            thread_id = target_msg.get("thread_id")
            
    if not thread_id:
        if message_id and target_msg:
            ctx_msgs = reconstructor.reconstruct_context(message_id, window_size=6)
            msgs = [m.model_dump() for m in ctx_msgs]
            thread_id = target_msg.get("thread_id", "conversation")
        else:
            raise HTTPException(status_code=400, detail="Either thread_id or message_id must be provided.")
    else:
        thread_msgs = reconstructor.get_full_thread(thread_id)
        if not thread_msgs:
            raise HTTPException(status_code=404, detail=f"Thread '{thread_id}' not found.")
        msgs = [m.model_dump() for m in thread_msgs]

    export_service = ExportService()
    pdf_bytes = export_service.generate_chat_pdf(
        thread_id=thread_id,
        messages=msgs,
        target_message_id=message_id,
        query=query,
        direct_answer=direct_answer
    )
    clean_name = thread_id.replace("thread_", "").replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="recallx_chat_{clean_name}.pdf"'
        }
    )

@router.get("/export/image")
def export_chat_image(
    thread_id: Optional[str] = Query(None),
    message_id: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    direct_answer: Optional[str] = Query(None)
):
    reconstructor = ContextReconstructor()
    mgr = IndexManager.get_instance()
    
    target_msg = None
    if message_id:
        target_msg = mgr.get_message(message_id)
        if target_msg and not thread_id:
            thread_id = target_msg.get("thread_id")
            
    if not thread_id:
        if message_id and target_msg:
            ctx_msgs = reconstructor.reconstruct_context(message_id, window_size=6)
            msgs = [m.model_dump() for m in ctx_msgs]
            thread_id = target_msg.get("thread_id", "conversation")
        else:
            raise HTTPException(status_code=400, detail="Either thread_id or message_id must be provided.")
    else:
        thread_msgs = reconstructor.get_full_thread(thread_id)
        if not thread_msgs:
            raise HTTPException(status_code=404, detail=f"Thread '{thread_id}' not found.")
        msgs = [m.model_dump() for m in thread_msgs]

    export_service = ExportService()
    png_bytes = export_service.generate_chat_image(
        thread_id=thread_id,
        messages=msgs,
        target_message_id=message_id,
        query=query,
        direct_answer=direct_answer
    )
    clean_name = thread_id.replace("thread_", "").replace(" ", "_")
    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="recallx_chat_{clean_name}.png"'
        }
    )

@router.get("/context/{message_id}", response_model=List[ContextMessage])
def get_message_context(message_id: str, window: int = Query(3, ge=1, le=10)):
    reconstructor = ContextReconstructor()
    context = reconstructor.reconstruct_context(message_id, window_size=window)
    if not context:
        raise HTTPException(status_code=404, detail=f"Message '{message_id}' not found.")
    return context

@router.get("/decisions", response_model=List[DecisionItem])
def get_decisions():
    detector = DecisionDetector()
    return detector.get_detected_decisions()

@router.get("/participants")
def get_participants():
    if not PARTICIPANTS_FILE.exists():
        raise HTTPException(status_code=500, detail="Participants configuration missing.")
    with open(PARTICIPANTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/evaluation")
def get_evaluation_report(suite: str = Query("official")):
    if suite == "unseen":
        eval_results_path = EVAL_DIR / "unseen_eval_results.json"
    else:
        eval_results_path = EVAL_DIR / "eval_results.json"

    if not eval_results_path.exists():
        fallback = EVAL_DIR / "eval_results.json"
        if not fallback.exists():
            raise HTTPException(status_code=404, detail="Evaluation results not yet generated. Please run evaluate.py first.")
        eval_results_path = fallback

    with open(eval_results_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.post("/index/rebuild")
def rebuild_index():
    mgr = IndexManager.get_instance()
    mgr.initialize(force_rebuild=True)
    return {
        "status": "success",
        "message": f"Successfully rebuilt index with {len(mgr.idx_to_id)} messages."
    }
