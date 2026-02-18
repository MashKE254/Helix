"""
Hierarchical Model Router
Routes queries to appropriate AI models based on cognitive complexity
"""

from typing import Dict, Optional, List
from enum import Enum
import anthropic
from backend.core.config import settings
import json


class ModelType(str, Enum):
    HAIKU = "claude-3-haiku-20240307"
    SONNET = "claude-3-sonnet-20240229"
    OPUS = "claude-3-opus-20240229"
    VERIFIED = "verified"  # Deterministic verification systems


class ModelRouter:
    """Routes queries to appropriate models based on complexity"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def _classify_complexity(self, query: str, context: Optional[Dict] = None) -> float:
        """
        Classify query complexity (0.0 to 1.0)
        Returns complexity score
        """
        # Simple heuristics for complexity
        simple_indicators = [
            "what is", "define", "recall", "list", "simple",
            "quick", "yes/no", "dashboard", "status"
        ]
        complex_indicators = [
            "explain why", "how does", "derive", "prove", "debug",
            "analyze", "compare", "socratic", "dialogue", "misconception"
        ]
        
        query_lower = query.lower()
        
        # Count indicators
        simple_count = sum(1 for ind in simple_indicators if ind in query_lower)
        complex_count = sum(1 for ind in complex_indicators if ind in query_lower)
        
        # Base complexity
        if simple_count > complex_count:
            base_complexity = 0.2
        elif complex_count > simple_count:
            base_complexity = 0.8
        else:
            base_complexity = 0.5
        
        # Adjust based on query length and context
        length_factor = min(len(query.split()) / 50, 0.3)
        context_factor = 0.2 if context and len(context.get('curriculum_docs', [])) > 3 else 0.0
        
        complexity = min(base_complexity + length_factor + context_factor, 1.0)
        return complexity
    
    def _select_model(self, complexity: float, requires_verification: bool = False) -> ModelType:
        """Select model based on complexity score"""
        if requires_verification:
            return ModelType.VERIFIED
        
        if complexity < settings.HAIKU_THRESHOLD:
            return ModelType.HAIKU
        elif complexity < settings.SONNET_THRESHOLD:
            return ModelType.SONNET
        else:
            return ModelType.OPUS
    
    async def route_query(
        self,
        query: str,
        context: Optional[Dict] = None,
        requires_verification: bool = False,
        student_profile: Optional[Dict] = None
    ) -> Dict:
        """
        Route query to appropriate model and get response
        
        Returns:
            {
                "model_used": ModelType,
                "response": str,
                "complexity_score": float,
                "citations": List[Dict],
                "socratic_questions": List[str]
            }
        """
        # Classify complexity
        complexity = self._classify_complexity(query, context)
        
        # Select model
        model_type = self._select_model(complexity, requires_verification)
        
        # Build system prompt with pedagogical constraints
        system_prompt = self._build_system_prompt(context, student_profile)
        
        # Route to appropriate handler
        if model_type == ModelType.VERIFIED:
            return await self._handle_verified(query, context)
        else:
            return await self._handle_llm(query, model_type, system_prompt, context)
    
    def _build_system_prompt(
        self,
        context: Optional[Dict],
        student_profile: Optional[Dict]
    ) -> str:
        """Build system prompt with pedagogical constraints"""
        prompt = """You are Helix, a Socratic tutor. Your role is to guide students through learning, not to give direct answers.

CONSTRAINTS:
1. Never give direct answers to practice problems or homework
2. Use Socratic questioning to guide understanding
3. Cite curriculum sources when explaining concepts
4. Detect and address misconceptions through targeted questions
5. Adapt explanations to the student's learning style and language

"""
        if context and context.get('curriculum_docs'):
            prompt += "CURRICULUM CONTEXT:\n"
            for doc in context['curriculum_docs'][:3]:
                prompt += f"- {doc.get('metadata', {}).get('title', 'Unknown')}: {doc.get('content', '')[:200]}...\n"
        
        if student_profile:
            prompt += f"\nSTUDENT PROFILE:\n"
            prompt += f"- Learning style: {student_profile.get('learning_style', 'unknown')}\n"
            prompt += f"- Native language: {student_profile.get('native_language', 'en')}\n"
            prompt += f"- Curriculum: {student_profile.get('curriculum_board', 'unknown')}\n"
        
        return prompt
    
    async def _handle_llm(
        self,
        query: str,
        model_type: ModelType,
        system_prompt: str,
        context: Optional[Dict]
    ) -> Dict:
        """Handle query with LLM model"""
        messages = [{"role": "user", "content": query}]
        
        response = self.client.messages.create(
            model=model_type.value,
            max_tokens=4000,
            system=system_prompt,
            messages=messages
        )
        
        response_text = response.content[0].text
        
        # Extract citations and questions (simplified - would use structured output in production)
        citations = context.get('curriculum_docs', []) if context else []
        
        # Generate Socratic questions (simplified)
        socratic_questions = await self._generate_socratic_questions(query, response_text)
        
        return {
            "model_used": model_type.value,
            "response": response_text,
            "complexity_score": self._classify_complexity(query, context),
            "citations": citations,
            "socratic_questions": socratic_questions
        }
    
    async def _handle_verified(
        self,
        query: str,
        context: Optional[Dict]
    ) -> Dict:
        """Handle query requiring deterministic verification"""
        # This would route to Wolfram Alpha, RDKit, Judge0, etc.
        # Simplified implementation - in production would use verification_service
        from backend.services.verification import verification_service
        
        # Check if it's math, chemistry, or code
        if any(keyword in query.lower() for keyword in ["solve", "calculate", "prove", "equation"]):
            # Math verification
            result = verification_service.verify_math_expression(query)
            response = f"Verified result: {result.get('simplified', 'Unable to verify')}"
        elif any(keyword in query.lower() for keyword in ["chemical", "reaction", "balance"]):
            # Chemistry verification
            result = verification_service.verify_chemical_equation(query)
            response = f"Equation balance: {result.get('balanced', False)}"
        else:
            response = "Verified computation would be performed here"
        
        return {
            "model_used": "verified",
            "response": response,
            "complexity_score": 1.0,
            "citations": [],
            "socratic_questions": []
        }
    
    async def _generate_socratic_questions(self, query: str, response: str) -> List[str]:
        """Generate follow-up Socratic questions"""
        # Simplified - would use LLM to generate contextual questions
        return [
            "What do you think would happen if...?",
            "Can you explain why that is?",
            "How does this relate to what we learned earlier?"
        ]


model_router = ModelRouter()
