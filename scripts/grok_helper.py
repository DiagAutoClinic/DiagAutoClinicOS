"""
Grok Assistant Helper for CAN Bus Project
Use this to structure queries for Grok/X.ai
"""

import json
import textwrap
from pathlib import Path

class GrokAssistant:
    """Helper to format code and questions for Grok"""
    
    @staticmethod
    def format_code_context(file_path: str, line_start: int = 1, line_end: int = 50) -> str:
        """Extract code context to include in Grok queries"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                context = ''.join(lines[line_start-1:line_end])
                return f"```python\n{context}\n```"
        except:
            return f"File not found: {file_path}"
    
    @staticmethod
    def format_can_question(question: str, context_files: list = None) -> str:
        """Format a structured question for CAN bus topics"""
        header = "🔧 CAN BUS DIAGNOSTIC PROJECT QUESTION\n"
        header += "="*50 + "\n\n"
        
        context = ""
        if context_files:
            context += "📁 RELEVANT FILES:\n"
            for file in context_files:
                if Path(file).exists():
                    context += f"- {file}\n"
        
        formatted = f"{header}{context}\n❓ QUESTION: {question}\n\n"
        formatted += "💡 Please provide:\n1. Specific code implementation\n2. CAN bus protocol considerations\n3. Error handling\n4. Testing approach\n"
        
        return formatted
    
    @staticmethod
    def parse_ref_file_question(file_path: str) -> str:
        """Create a question about parsing .REF files"""
        return GrokAssistant.format_can_question(
            f"How should I parse this Racelogic .REF file: {file_path}?",
            context_files=[file_path, "ref_parser.py"]
        )

# Example usage
if __name__ == "__main__":
    grok = GrokAssistant()
    
    # Example: Create a question about signal decoding
    question = grok.format_can_question(
        "How do I implement big-endian signal extraction in Python?",
        context_files=["ref_parser.py"]
    )
    print(question)