"""
Parent endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict

from backend.core.database import get_db
from backend.api.auth import get_current_user
from backend.models.user import User, UserRole, ParentProfile, StudentProfile
from backend.services.knowledge_graph import knowledge_graph_service

router = APIRouter()


class ChildDashboard(BaseModel):
    child_id: int
    child_name: str
    subjects: List[str]
    weak_concepts: List[str]
    misconceptions: List[Dict]
    recent_activity: List[Dict]
    time_spent_today: int  # minutes


@router.get("/dashboard")
async def get_parent_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get parent dashboard with all children's learning states"""
    if current_user.role != UserRole.PARENT:
        raise HTTPException(status_code=403, detail="Only parents can access dashboard")
    
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")
    
    children_ids = parent.children_ids or []
    children_dashboards = []
    
    for child_id in children_ids:
        child_user = db.query(User).filter(User.id == child_id).first()
        if not child_user:
            continue
        
        child_student = db.query(StudentProfile).filter(StudentProfile.user_id == child_id).first()
        if not child_student:
            continue
        
        # Get child's knowledge state
        state = knowledge_graph_service.get_student_state(child_student.id, db)
        weak_concepts = knowledge_graph_service.get_weak_concepts(child_student.id, 0.6, db)
        
        children_dashboards.append({
            "child_id": child_id,
            "child_name": child_user.full_name,
            "subjects": child_student.curriculum_subjects or [],
            "weak_concepts": weak_concepts,
            "misconceptions": state.get("misconceptions", []),
            "recent_activity": [],  # Would fetch from learning sessions
            "time_spent_today": 0  # Would calculate from sessions
        })
    
    return {
        "parent_name": current_user.full_name,
        "children": children_dashboards,
        "total_children": len(children_dashboards)
    }


@router.post("/link-child")
async def link_child(
    child_email: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Link a child account to parent"""
    if current_user.role != UserRole.PARENT:
        raise HTTPException(status_code=403, detail="Only parents can link children")
    
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")
    
    # Find child user
    child_user = db.query(User).filter(User.email == child_email).first()
    if not child_user or child_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=404, detail="Child account not found")
    
    # Add to children list
    children_ids = parent.children_ids or []
    if child_user.id not in children_ids:
        children_ids.append(child_user.id)
        parent.children_ids = children_ids
        db.commit()
    
    return {"message": "Child linked successfully", "child_id": child_user.id}
