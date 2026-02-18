"""
Curriculum endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict

from backend.core.database import get_db
from backend.api.auth import get_current_user
from backend.models.learning import CurriculumDocument
from backend.services.rag_engine import rag_engine

router = APIRouter()


class CurriculumDocumentCreate(BaseModel):
    board: str
    subject: str
    document_type: str
    title: str
    content: str
    metadata: Optional[Dict] = None


@router.post("/documents")
async def add_curriculum_document(
    document: CurriculumDocumentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a curriculum document to the system"""
    # In production, would check for admin permissions
    
    curriculum_doc = CurriculumDocument(
        board=document.board,
        subject=document.subject,
        document_type=document.document_type,
        title=document.title,
        content=document.content,
        doc_metadata=document.metadata or {}
    )
    
    db.add(curriculum_doc)
    db.commit()
    db.refresh(curriculum_doc)
    
    # Add to vector store
    await rag_engine.add_curriculum_document(curriculum_doc, db)
    
    return {
        "id": curriculum_doc.id,
        "message": "Curriculum document added successfully"
    }


@router.get("/retrieve")
async def retrieve_curriculum_context(
    query: str,
    board: str,
    subject: str,
    topic: Optional[str] = None,
    top_k: int = 5,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve relevant curriculum documents"""
    results = await rag_engine.retrieve_curriculum_context(
        query=query,
        board=board,
        subject=subject,
        topic=topic,
        top_k=top_k
    )
    
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


@router.get("/marking-scheme")
async def get_marking_scheme(
    board: str,
    subject: str,
    topic: str,
    question_type: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve marking scheme for specific question type"""
    scheme = await rag_engine.retrieve_marking_scheme(
        board=board,
        subject=subject,
        topic=topic,
        question_type=question_type
    )
    
    if not scheme:
        raise HTTPException(status_code=404, detail="Marking scheme not found")
    
    return scheme
