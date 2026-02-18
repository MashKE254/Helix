"""
Teacher endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict

from backend.core.database import get_db
from backend.api.auth import get_current_user
from backend.models.user import User, UserRole, TeacherProfile

router = APIRouter()


class StudentReadiness(BaseModel):
    student_id: int
    student_name: str
    ready_for_new_content: bool
    needs_review: List[str]
    mastery_percentage: float


class ClassBriefing(BaseModel):
    class_id: str
    total_students: int
    ready_count: int
    review_count: int
    students: List[StudentReadiness]
    suggested_interventions: List[Dict]


@router.get("/briefing")
async def get_morning_briefing(
    class_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get morning briefing for class"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can access briefing")
    
    teacher = db.query(TeacherProfile).filter(TeacherProfile.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    # In production, would fetch actual class data
    # Simplified implementation
    return {
        "class_id": class_id,
        "total_students": 0,
        "ready_count": 0,
        "review_count": 0,
        "students": [],
        "suggested_interventions": []
    }


@router.get("/students/{student_id}/state")
async def get_student_state_for_teacher(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student state (teacher view)"""
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can access student state")
    
    # In production, would verify teacher has access to this student
    from backend.models.user import StudentProfile
    from backend.services.knowledge_graph import knowledge_graph_service
    
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    state = knowledge_graph_service.get_student_state(student_id, db)
    return state
