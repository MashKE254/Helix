"""
User models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from backend.core.database import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    INDIVIDUAL = "individual"
    FAMILY_PRO = "family_pro"
    INSTITUTIONAL = "institutional"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    parent_profile = relationship("ParentProfile", back_populates="user", uselist=False)
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False)


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer)
    grade_level = Column(String)
    learning_style = Column(String)  # visual, auditory, kinesthetic, etc.
    learning_profile = Column(JSON)  # Detailed profile from intake
    native_language = Column(String, default="en")
    target_language = Column(String, default="en")
    curriculum_board = Column(String)  # IGCSE, KCSE, CBSE, Common Core, etc.
    curriculum_subjects = Column(JSON)  # List of subjects
    knowledge_graph_id = Column(String, unique=True)  # Reference to knowledge graph
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="student_profile")
    sessions = relationship("LearningSession", back_populates="student")


class ParentProfile(Base):
    __tablename__ = "parent_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    children_ids = Column(JSON)  # List of student user IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="parent_profile")


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    school_name = Column(String)
    school_district = Column(String)
    subjects = Column(JSON)  # List of subjects taught
    class_ids = Column(JSON)  # List of class IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="teacher_profile")
