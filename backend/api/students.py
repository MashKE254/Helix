"""
Student endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List

from backend.core.database import get_db
from backend.api.auth import get_current_user
from backend.models.user import User, UserRole, StudentProfile
from backend.services.knowledge_graph import knowledge_graph_service

router = APIRouter()


class StudentIntake(BaseModel):
    age: Optional[int] = None
    grade_level: Optional[str] = None
    learning_style: Optional[str] = None
    native_language: str = "en"
    target_language: str = "en"
    curriculum_board: str
    curriculum_subjects: List[str]
    learning_profile: Optional[Dict] = None


class StudentStateResponse(BaseModel):
    graph_id: str
    concepts: Dict
    misconceptions: List
    prerequisite_gaps: List
    last_updated: Optional[str]


@router.post("/intake")
async def complete_intake(
    intake: StudentIntake,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete student intake interview"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can complete intake")
    
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Update profile
    student.age = intake.age
    student.grade_level = intake.grade_level
    student.learning_style = intake.learning_style
    student.native_language = intake.native_language
    student.target_language = intake.target_language
    student.curriculum_board = intake.curriculum_board
    student.curriculum_subjects = intake.curriculum_subjects
    student.learning_profile = intake.learning_profile or {}
    
    # Initialize knowledge graph
    knowledge_graph_service.get_or_create_graph(student.id, db)
    
    db.commit()
    
    return {"message": "Intake completed successfully", "student_id": student.id}


@router.get("/state", response_model=StudentStateResponse)
async def get_student_state(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student knowledge graph state"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can access state")
    
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    state = knowledge_graph_service.get_student_state(student.id, db)
    return state


@router.get("/weak-concepts")
async def get_weak_concepts(
    threshold: float = 0.6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get concepts with mastery below threshold"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can access weak concepts")
    
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    weak = knowledge_graph_service.get_weak_concepts(student.id, threshold, db)
    return {"weak_concepts": weak}


@router.get("/learning-path")
async def get_learning_path(
    subject: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommended learning path for subject"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can access learning path")
    
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    path = knowledge_graph_service.get_next_learning_path(student.id, subject, db)
    return {"learning_path": path}
