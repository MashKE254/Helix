"""
Practice problem generation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict

from backend.core.database import get_db
from backend.api.auth import get_current_user
from backend.models.user import User, UserRole, StudentProfile
from backend.models.learning import PracticeProblem, PracticeAttempt
from backend.services.rag_engine import rag_engine
from backend.services.model_router import model_router
from backend.services.knowledge_graph import knowledge_graph_service
from backend.services.verification import verification_service

router = APIRouter()


class PracticeRequest(BaseModel):
    subject: str
    topic: str
    difficulty: Optional[float] = 0.5
    target_concepts: Optional[List[str]] = None
    problem_type: Optional[str] = "free_response"


class PracticeProblemResponse(BaseModel):
    problem_id: int
    problem_text: str
    problem_type: str
    difficulty: float
    target_concepts: List[str]


class PracticeSubmission(BaseModel):
    problem_id: int
    answer: str


@router.post("/generate", response_model=PracticeProblemResponse)
async def generate_practice_problem(
    request: PracticeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a practice problem"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can generate practice")
    
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get student's weak concepts if not specified
    target_concepts = request.target_concepts
    if not target_concepts:
        weak = knowledge_graph_service.get_weak_concepts(student.id, 0.6, db)
        target_concepts = weak[:3] if weak else [request.topic]
    
    # Retrieve curriculum context for problem generation
    query = f"{request.topic} practice problem {request.problem_type}"
    curriculum_docs = await rag_engine.retrieve_curriculum_context(
        query=query,
        board=student.curriculum_board,
        subject=request.subject,
        topic=request.topic,
        top_k=3
    )
    
    # Generate problem using AI
    context = {
        "curriculum_docs": curriculum_docs,
        "student_profile": {
            "learning_style": student.learning_style,
            "curriculum_board": student.curriculum_board
        },
        "requirements": {
            "difficulty": request.difficulty,
            "target_concepts": target_concepts,
            "problem_type": request.problem_type
        }
    }
    
    # Use Sonnet for problem generation
    generation_prompt = f"""Generate a {request.problem_type} practice problem for {request.subject} on {request.topic}.
Difficulty level: {request.difficulty} (0.0 = easy, 1.0 = hard)
Target concepts: {', '.join(target_concepts)}
Curriculum board: {student.curriculum_board}

Return only the problem text, formatted clearly."""
    
    result = await model_router.route_query(
        query=generation_prompt,
        context=context,
        requires_verification=False
    )
    
    problem_text = result["response"]
    
    # Create practice problem record
    problem = PracticeProblem(
        student_id=student.id,
        subject=request.subject,
        topic=request.topic,
        problem_text=problem_text,
        problem_type=request.problem_type,
        difficulty=request.difficulty,
        target_concepts=target_concepts,
        curriculum_alignment=curriculum_docs[0].get("metadata", {}) if curriculum_docs else {}
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    
    return {
        "problem_id": problem.id,
        "problem_text": problem_text,
        "problem_type": request.problem_type,
        "difficulty": request.difficulty,
        "target_concepts": target_concepts
    }


@router.post("/submit")
async def submit_practice_answer(
    submission: PracticeSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit answer to practice problem"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can submit answers")
    
    student = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get problem
    problem = db.query(PracticeProblem).filter(PracticeProblem.id == submission.problem_id).first()
    if not problem or problem.student_id != student.id:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Retrieve marking scheme
    marking_scheme = await rag_engine.retrieve_marking_scheme(
        board=student.curriculum_board,
        subject=problem.subject,
        topic=problem.topic,
        question_type=problem.problem_type
    )
    
    # Generate feedback using AI
    feedback_prompt = f"""Student answer: {submission.answer}
Correct problem: {problem.problem_text}
Marking scheme: {marking_scheme.get('content', '') if marking_scheme else 'Standard marking'}

Provide:
1. Whether the answer is correct (true/false)
2. Detailed feedback
3. Any misconceptions detected
4. Suggestions for improvement

Format as JSON with keys: is_correct, feedback, misconceptions, suggestions."""
    
    context = {
        "curriculum_docs": [marking_scheme] if marking_scheme else [],
        "student_profile": {
            "curriculum_board": student.curriculum_board
        }
    }
    
    result = await model_router.route_query(
        query=feedback_prompt,
        context=context,
        requires_verification=False
    )
    
    # Parse feedback (simplified - would use structured output)
    feedback_text = result["response"]
    is_correct = "correct" in feedback_text.lower() or "yes" in feedback_text.lower()
    
    # Detect misconceptions (simplified)
    misconceptions = []
    if not is_correct:
        misconceptions.append({
            "concept": problem.topic,
            "type": "incorrect_application",
            "evidence": submission.answer
        })
    
    # Create attempt record
    attempt = PracticeAttempt(
        problem_id=submission.problem_id,
        student_id=student.id,
        student_answer=submission.answer,
        is_correct=is_correct,
        feedback=feedback_text,
        misconceptions_detected=misconceptions
    )
    db.add(attempt)
    
    # Update knowledge graph
    if is_correct:
        mastery_increase = 0.1
    else:
        mastery_increase = -0.05
    
    # Get current mastery or default
    state = knowledge_graph_service.get_student_state(student.id, db)
    current_mastery = state.get("concepts", {}).get(problem.topic, {}).get("mastery", 0.5)
    new_mastery = max(0.0, min(1.0, current_mastery + mastery_increase))
    
    knowledge_graph_service.update_concept_mastery(
        student_id=student.id,
        concept=problem.topic,
        mastery_level=new_mastery,
        subject=problem.subject,
        db=db
    )
    
    # Record misconceptions
    for misconception in misconceptions:
        knowledge_graph_service.detect_misconception(
            student_id=student.id,
            concept=misconception["concept"],
            misconception_type=misconception["type"],
            evidence=misconception["evidence"],
            db=db
        )
    
    db.commit()
    db.refresh(attempt)
    
    return {
        "attempt_id": attempt.id,
        "is_correct": is_correct,
        "feedback": feedback_text,
        "misconceptions": misconceptions,
        "updated_mastery": new_mastery
    }
