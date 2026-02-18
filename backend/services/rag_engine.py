"""
RAG Engine for Curriculum Retrieval
Retrieves curriculum documents, past papers, and marking schemes
"""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import openai
from backend.core.config import settings
from backend.models.learning import CurriculumDocument
from sqlalchemy.orm import Session


class RAGEngine:
    """Retrieval-Augmented Generation Engine for curriculum intelligence"""
    
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get the curriculum collection"""
        try:
            self.collection = self.chroma_client.get_collection("curriculum")
        except:
            self.collection = self.chroma_client.create_collection(
                name="curriculum",
                metadata={"description": "Curriculum documents, syllabi, and past papers"}
            )
    
    async def add_curriculum_document(
        self,
        document: CurriculumDocument,
        db: Session
    ):
        """Add a curriculum document to the vector store"""
        # Generate embedding
        embedding = self.embedding_model.encode(document.content).tolist()
        
        # Prepare metadata
        metadata = {
            "board": document.board,
            "subject": document.subject,
            "type": document.document_type,
            "title": document.title,
        }
        if document.metadata:
            metadata.update(document.metadata)
        
        # Store in ChromaDB
        self.collection.add(
            ids=[str(document.id)],
            embeddings=[embedding],
            documents=[document.content],
            metadatas=[metadata]
        )
    
    async def retrieve_curriculum_context(
        self,
        query: str,
        board: str,
        subject: str,
        topic: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant curriculum documents for a query
        
        Returns:
            List of dictionaries with content, metadata, and relevance scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Build metadata filter
        where = {
            "board": board,
            "subject": subject
        }
        if topic:
            where["topic"] = topic
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where if where else None
        )
        
        # Format results
        retrieved_docs = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                retrieved_docs.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return retrieved_docs
    
    async def retrieve_marking_scheme(
        self,
        board: str,
        subject: str,
        topic: str,
        question_type: str
    ) -> Optional[Dict]:
        """Retrieve marking scheme for specific question type"""
        query = f"{topic} {question_type} marking scheme"
        results = await self.retrieve_curriculum_context(
            query=query,
            board=board,
            subject=subject,
            top_k=3
        )
        
        # Filter for marking schemes
        marking_schemes = [r for r in results if r['metadata'].get('type') == 'marking_scheme']
        return marking_schemes[0] if marking_schemes else None
    
    async def retrieve_learning_objectives(
        self,
        board: str,
        subject: str,
        chapter: str
    ) -> List[Dict]:
        """Retrieve learning objectives for a specific chapter"""
        query = f"{chapter} learning objectives syllabus"
        results = await self.retrieve_curriculum_context(
            query=query,
            board=board,
            subject=subject,
            top_k=5
        )
        
        # Filter for syllabus documents
        syllabi = [r for r in results if r['metadata'].get('type') == 'syllabus']
        return syllabi


rag_engine = RAGEngine()
