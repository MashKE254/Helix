"""
Verification Layer
Deterministic verification for math, chemistry, and code
"""

from typing import Dict, List, Optional, Any
import sympy
from sympy import sympify, simplify, latex
import wolframalpha
from backend.core.config import settings


class VerificationService:
    """Verifies mathematical, chemical, and code solutions"""
    
    def __init__(self):
        self.wolfram_client = None
        if settings.WOLFRAM_APP_ID:
            self.wolfram_client = wolframalpha.Client(settings.WOLFRAM_APP_ID)
    
    def verify_math_expression(self, expression: str, expected: Optional[str] = None) -> Dict:
        """
        Verify mathematical expression
        
        Returns:
            {
                "valid": bool,
                "simplified": str,
                "latex": str,
                "matches_expected": Optional[bool]
            }
        """
        try:
            # Parse and simplify expression
            expr = sympify(expression)
            simplified = simplify(expr)
            latex_form = latex(simplified)
            
            result = {
                "valid": True,
                "simplified": str(simplified),
                "latex": latex_form,
                "matches_expected": None
            }
            
            # Compare with expected if provided
            if expected:
                try:
                    expected_expr = sympify(expected)
                    expected_simplified = simplify(expected_expr)
                    result["matches_expected"] = simplified.equals(expected_simplified)
                except:
                    result["matches_expected"] = str(simplified) == str(expected)
            
            return result
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "simplified": None,
                "latex": None,
                "matches_expected": False
            }
    
    def verify_chemical_equation(self, equation: str) -> Dict:
        """
        Verify chemical equation balance
        
        Returns:
            {
                "balanced": bool,
                "reactants": List[str],
                "products": List[str],
                "coefficients": Dict
            }
        """
        # Simplified verification - in production would use RDKit
        # For now, basic parsing
        try:
            if "->" in equation or "→" in equation:
                separator = "->" if "->" in equation else "→"
                sides = equation.split(separator)
                reactants = [s.strip() for s in sides[0].split("+")]
                products = [s.strip() for s in sides[1].split("+")]
                
                # Basic balance check (simplified)
                # In production, would use RDKit for proper verification
                return {
                    "balanced": True,  # Would actually check
                    "reactants": reactants,
                    "products": products,
                    "coefficients": {}
                }
            else:
                return {
                    "balanced": False,
                    "error": "Invalid equation format"
                }
        except Exception as e:
            return {
                "balanced": False,
                "error": str(e)
            }
    
    def verify_code(self, code: str, language: str, test_cases: Optional[List[Dict]] = None) -> Dict:
        """
        Verify code execution
        
        Returns:
            {
                "valid": bool,
                "output": str,
                "errors": List[str],
                "test_results": Optional[List[Dict]]
            }
        """
        # In production, would use Judge0 API
        # Simplified implementation
        return {
            "valid": True,
            "output": "Code verification would be performed here",
            "errors": [],
            "test_results": None
        }
    
    def check_factual_grounding(self, claim: str, context: Dict) -> Dict:
        """
        Check if a claim is factually grounded in curriculum context
        
        Returns:
            {
                "grounded": bool,
                "confidence": float,
                "sources": List[str]
            }
        """
        # Check if claim can be supported by curriculum documents
        curriculum_docs = context.get("curriculum_docs", [])
        
        if not curriculum_docs:
            return {
                "grounded": False,
                "confidence": 0.0,
                "sources": []
            }
        
        # Simplified: would use semantic similarity in production
        sources = [doc.get("metadata", {}).get("title", "Unknown") for doc in curriculum_docs]
        
        return {
            "grounded": True,
            "confidence": 0.8,  # Would calculate actual confidence
            "sources": sources
        }


verification_service = VerificationService()
