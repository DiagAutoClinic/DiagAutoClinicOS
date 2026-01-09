import math
import logging
import re
import ast
import operator
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class EquationSolver:
    """
    Solver for OBD-II and diagnostic equations.
    Converts raw bytes (A, B, C, D...) into physical values using string formulas.
    SECURE VERSION: Uses AST parsing instead of eval().
    """
    
    # Supported operators
    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @staticmethod
    def _eval_node(node, variables):
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            left = EquationSolver._eval_node(node.left, variables)
            right = EquationSolver._eval_node(node.right, variables)
            if type(node.op) in EquationSolver._operators:
                return EquationSolver._operators[type(node.op)](left, right)
            raise ValueError(f"Unsupported binary operator: {type(node.op)}")
        elif isinstance(node, ast.UnaryOp):
            operand = EquationSolver._eval_node(node.operand, variables)
            if type(node.op) in EquationSolver._operators:
                return EquationSolver._operators[type(node.op)](operand)
            raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        elif isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            else:
                raise ValueError(f"Unknown variable: {node.id}")
        elif isinstance(node, ast.Expression):
             return EquationSolver._eval_node(node.body, variables)
            
        raise ValueError(f"Unsupported operation: {node}")

    @staticmethod
    def solve(equation: str, data_bytes: List[int]) -> float:
        """
        Solve OBD-II equation using data bytes (A, B, C, D...).
        SECURE IMPLEMENTATION using AST parsing.
        
        Args:
            equation: Formula string (e.g., "A*0.5 + 10", "(256*A + B)/4")
            data_bytes: List of integer byte values [A, B, C, D...]
            
        Returns:
            Calculated float value or 0.0 on error
        """
        if not equation or not data_bytes:
            return 0.0

        # Clean equation (uppercase, remove unsafe chars)
        equation = equation.upper().strip()
        
        # Security check: Allow only A-Z, 0-9, operators, parens, spaces, dot
        if not re.match(r"^[A-Z0-9\.\+\-\*\/\(\)\s]+$", equation):
            logger.warning(f"Invalid characters in equation: {equation}")
            return 0.0

        # Map A, B, C, D... to data bytes
        variables = {}
        for i, byte_val in enumerate(data_bytes):
            var_name = chr(65 + i) # A, B, C, D...
            variables[var_name] = byte_val

        # Check if equation uses variables not present in data
        # This part was in the original, we can keep it or let AST fail.
        # Original logic was:
        used_vars = set(re.findall(r'[A-Z]', equation))
        available_vars = set(variables.keys())
        
        if not used_vars.issubset(available_vars):
            missing = used_vars - available_vars
            logger.debug(f"Equation '{equation}' requires missing bytes: {missing}")
            return 0.0

        try:
            # Parse into AST
            tree = ast.parse(equation, mode='eval')
            
            # Evaluate AST
            result = EquationSolver._eval_node(tree.body, variables)
            return float(result)
            
        except Exception as e:
            logger.error(f"Error solving equation '{equation}': {e}")
            return 0.0

    @staticmethod
    def validate_equation(equation: str) -> bool:
        """Check if an equation string is valid and safe"""
        if not equation:
            return False
        # Basic regex check first
        if not re.match(r"^[A-Z0-9\.\+\-\*\/\(\)\s]+$", equation.upper().strip()):
            return False
            
        try:
            # Try to parse it to ensure it's valid syntax
            ast.parse(equation, mode='eval')
            return True
        except:
            return False
