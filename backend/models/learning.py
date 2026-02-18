"""
Learning and curriculum models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.core.database import Base


class LearningSession(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    subject = Column(String, nullable=False)
    topic = Column(String)
    session_type = Column(String)  # tutoring, practice, exam_prep, etc.
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    concepts_covered = Column(JSON)
    mastery_updates = Column(JSON)  # Knowledge graph updates
    
    student = relationship("StudentProfile", back_populates="sessions")
    interactions = relationship("TutoringInteraction", back_populates="session")


class TutoringInteraction(Base):
    __tablename__ = "tutoring_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=False)
    student_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    model_used = Column(String)  # haiku, sonnet, opus, verified
    curriculum_sources = Column(JSON)  # Retrieved curriculum chunks
    citations = Column(JSON)  # Source citations
    socratic_questions = Column(JSON)  # Generated questions
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("LearningSession", back_populates="interactions")


class PracticeProblem(Base):
    __tablename__ = "practice_problems"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    problem_text = Column(Text, nullable=False)
    problem_type = Column(String)  # multiple_choice, free_response, etc.
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    difficulty = Column(Float)  # 0.0 to 1.0
    target_concepts = Column(JSON)  # Concepts this problem targets
    curriculum_alignment = Column(JSON)  # Alignment to curriculum standards


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("practice_problems.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    student_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean)
    feedback = Column(Text)
    misconceptions_detected = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeGraph(Base):
    __tablename__ = "knowledge_graphs"
    
    id = Column(String, primary_key=True)  # UUID
    student_id = Column(Integer, ForeignKey("student_profiles.id"), unique=True, nullable=False)
    graph_data = Column(JSON, nullable=False)  # Full knowledge graph structure
    concepts = Column(JSON)  # List of concepts with mastery levels
    misconceptions = Column(JSON)  # Detected misconceptions
    prerequisite_gaps = Column(JSON)  # Missing prerequisites
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CurriculumDocument(Base):
    __tablename__ = "curriculum_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    board = Column(String, nullable=False)  # IGCSE, KCSE, etc.
    subject = Column(String, nullable=False)
    document_type = Column(String)  # syllabus, past_paper, marking_scheme, textbook
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON)  # Year, chapter, topic, etc.
    embedding_id = Column(String)  # Reference to vector DB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
