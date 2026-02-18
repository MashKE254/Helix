"""
Knowledge Graph System
Maintains persistent knowledge graphs for each student
"""

from typing import Dict, List, Optional
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.learning import KnowledgeGraph as KnowledgeGraphModel
from backend.models.user import StudentProfile


class KnowledgeGraphService:
    """Manages student knowledge graphs"""
    
    def __init__(self):
        pass
    
    def get_or_create_graph(self, student_id: int, db: Session) -> KnowledgeGraphModel:
        """Get or create knowledge graph for student"""
        student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Check if graph exists
        graph = db.query(KnowledgeGraphModel).filter(
            KnowledgeGraphModel.student_id == student_id
        ).first()
        
        if not graph:
            # Create new graph
            graph_id = str(uuid.uuid4())
            graph = KnowledgeGraphModel(
                id=graph_id,
                student_id=student_id,
                graph_data={
                    "nodes": [],
                    "edges": [],
                    "concepts": {}
                },
                concepts={},
                misconceptions=[],
                prerequisite_gaps=[]
            )
            db.add(graph)
            db.commit()
            db.refresh(graph)
            
            # Update student profile
            student.knowledge_graph_id = graph_id
            db.commit()
        
        return graph
    
    def update_concept_mastery(
        self,
        student_id: int,
        concept: str,
        mastery_level: float,  # 0.0 to 1.0
        subject: str,
        db: Session
    ):
        """Update mastery level for a concept"""
        graph = self.get_or_create_graph(student_id, db)
        
        graph_data = graph.graph_data
        concepts = graph.concepts or {}
        
        # Update concept
        concepts[concept] = {
            "mastery": mastery_level,
            "subject": subject,
            "last_updated": datetime.utcnow().isoformat(),
            "attempts": concepts.get(concept, {}).get("attempts", 0) + 1
        }
        
        # Update graph structure
        if concept not in graph_data.get("concepts", {}):
            graph_data.setdefault("concepts", {})[concept] = {
                "id": concept,
                "mastery": mastery_level,
                "subject": subject
            }
        else:
            graph_data["concepts"][concept]["mastery"] = mastery_level
        
        graph.concepts = concepts
        graph.graph_data = graph_data
        graph.updated_at = datetime.utcnow()
        
        db.commit()
    
    def detect_misconception(
        self,
        student_id: int,
        concept: str,
        misconception_type: str,
        evidence: str,
        db: Session
    ):
        """Record a detected misconception"""
        graph = self.get_or_create_graph(student_id, db)
        
        misconceptions = graph.misconceptions or []
        
        # Check if misconception already exists
        existing = next(
            (m for m in misconceptions if m.get("concept") == concept and m.get("type") == misconception_type),
            None
        )
        
        if existing:
            existing["count"] = existing.get("count", 0) + 1
            existing["last_seen"] = datetime.utcnow().isoformat()
            existing["evidence"].append(evidence)
        else:
            misconceptions.append({
                "concept": concept,
                "type": misconception_type,
                "count": 1,
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "evidence": [evidence],
                "addressed": False
            })
        
        graph.misconceptions = misconceptions
        graph.updated_at = datetime.utcnow()
        
        db.commit()
    
    def identify_prerequisite_gaps(
        self,
        student_id: int,
        target_concept: str,
        required_prerequisites: List[str],
        db: Session
    ) -> List[str]:
        """Identify missing prerequisites for a concept"""
        graph = self.get_or_create_graph(student_id, db)
        
        concepts = graph.concepts or {}
        gaps = []
        
        for prereq in required_prerequisites:
            prereq_mastery = concepts.get(prereq, {}).get("mastery", 0.0)
            if prereq_mastery < 0.7:  # Threshold for mastery
                gaps.append(prereq)
        
        # Update prerequisite gaps
        existing_gaps = graph.prerequisite_gaps or []
        if gaps:
            gap_entry = {
                "target_concept": target_concept,
                "missing_prerequisites": gaps,
                "detected_at": datetime.utcnow().isoformat()
            }
            existing_gaps.append(gap_entry)
            graph.prerequisite_gaps = existing_gaps
            graph.updated_at = datetime.utcnow()
            db.commit()
        
        return gaps
    
    def get_student_state(self, student_id: int, db: Session) -> Dict:
        """Get complete student knowledge state"""
        graph = self.get_or_create_graph(student_id, db)
        
        return {
            "graph_id": graph.id,
            "concepts": graph.concepts or {},
            "misconceptions": graph.misconceptions or [],
            "prerequisite_gaps": graph.prerequisite_gaps or [],
            "last_updated": graph.updated_at.isoformat() if graph.updated_at else None
        }
    
    def get_weak_concepts(self, student_id: int, threshold: float = 0.6, db: Session = None) -> List[str]:
        """Get concepts with mastery below threshold"""
        graph = self.get_or_create_graph(student_id, db)
        concepts = graph.concepts or {}
        
        weak = [
            concept for concept, data in concepts.items()
            if data.get("mastery", 0.0) < threshold
        ]
        
        return weak
    
    def get_next_learning_path(self, student_id: int, subject: str, db: Session) -> List[str]:
        """Generate next learning path based on knowledge graph"""
        graph = self.get_or_create_graph(student_id, db)
        concepts = graph.concepts or {}
        
        # Simple algorithm: prioritize concepts with prerequisites met
        # In production, this would use graph traversal algorithms
        
        subject_concepts = [
            (concept, data) for concept, data in concepts.items()
            if data.get("subject") == subject
        ]
        
        # Sort by mastery (lowest first, but not mastered)
        subject_concepts.sort(key=lambda x: x[1].get("mastery", 0.0))
        
        # Return top 5 concepts to work on
        return [concept for concept, _ in subject_concepts[:5]]


knowledge_graph_service = KnowledgeGraphService()
