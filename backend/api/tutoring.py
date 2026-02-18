"""
Tutoring endpoints - Core Socratic dialogue
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

from backend.core.database import get_db
from backend.api.auth import get_current_user
from backend.models.user import User, UserRole, StudentProfile
from backend.models.learning import LearningSession, TutoringInteraction
from backend.services.rag_engine import rag_engine
from backend.services.model_router import model_router
from backend.services.knowledge_graph import knowledge_graph_service
from backend.services.verification import verification_service

router = APIRouter()


class TutoringRequest(BaseModel):
    query: str
    subject: str
    topic: Optional[str] = None
    session_id: Optional[int] = None


class TutoringResponse(BaseModel):
    response: str
    model_used: str
    citations: List[Dict]
    socratic_questions: List[str]
    session_id: int
    interaction_id: int


@router.post("/ask", response_model=TutoringResponse)
async def ask_tutor(
    request: TutoringRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question to the AI tutor"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can use tutoring")
    
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get or create session
    if request.session_id:
        session = db.query(LearningSession).filter(LearningSession.id == request.session_id).first()
        if not session or session.student_id != student.id:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = LearningSession(
            student_id=student.id,
            subject=request.subject,
            topic=request.topic,
            session_type="tutoring"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Retrieve curriculum context
    curriculum_docs = await rag_engine.retrieve_curriculum_context(
        query=request.query,
        board=student.curriculum_board,
        subject=request.subject,
        topic=request.topic,
        top_k=5
    )
    
    # Build context
    context = {
        "curriculum_docs": curriculum_docs,
        "student_profile": {
            "learning_style": student.learning_style,
            "native_language": student.native_language,
            "curriculum_board": student.curriculum_board
        }
    }
    
    # Check if verification needed (simplified heuristic)
    requires_verification = any(
        keyword in request.query.lower()
        for keyword in ["solve", "calculate", "prove", "verify", "code"]
    )
    
    # Route query through model router
    result = await model_router.route_query(
        query=request.query,
        context=context,
        requires_verification=requires_verification,
        student_profile=context["student_profile"]
    )
    
    # Verify factual grounding
    grounding = verification_service.check_factual_grounding(result["response"], context)
    if not grounding["grounded"]:
        result["response"] = "I don't have enough information from your curriculum to answer that question accurately. Let me help you find the relevant material."
    
    # Save interaction
    interaction = TutoringInteraction(
        session_id=session.id,
        student_query=request.query,
        ai_response=result["response"],
        model_used=result["model_used"],
        curriculum_sources=curriculum_docs,
        citations=result.get("citations", []),
        socratic_questions=result.get("socratic_questions", [])
    )
    db.add(interaction)
    
    # Update knowledge graph (simplified - would analyze response)
    # knowledge_graph_service.update_concept_mastery(...)
    
    db.commit()
    db.refresh(interaction)
    
    return {
        "response": result["response"],
        "model_used": result["model_used"],
        "citations": result.get("citations", []),
        "socratic_questions": result.get("socratic_questions", []),
        "session_id": session.id,
        "interaction_id": interaction.id
    }


@router.post("/sessions")
async def create_session(
    subject: str,
    topic: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new learning session"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can create sessions")
    
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    session = LearningSession(
        student_id=student.id,
        subject=subject,
        topic=topic,
        session_type="tutoring"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "subject": subject,
        "topic": topic,
        "started_at": session.started_at.isoformat()
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get session details and interactions"""
    session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify access
    if current_user.role == UserRole.STUDENT:
        student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if not student or session.student_id != student.id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    interactions = db.query(TutoringInteraction).filter(
        TutoringInteraction.session_id == session_id
    ).order_by(TutoringInteraction.timestamp).all()
    
    return {
        "session": {
            "id": session.id,
            "subject": session.subject,
            "topic": session.topic,
            "started_at": session.started_at.isoformat(),
            "duration_minutes": session.duration_minutes
        },
        "interactions": [
            {
                "id": i.id,
                "student_query": i.student_query,
                "ai_response": i.ai_response,
                "model_used": i.model_used,
                "timestamp": i.timestamp.isoformat()
            }
            for i in interactions
        ]
    }
