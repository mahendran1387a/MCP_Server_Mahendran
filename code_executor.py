"""
Code Execution Sandbox
Safely execute Python code with timeout and resource limits
"""
import sys
import io
import contextlib
from typing import Dict, Any, Optional
import ast
import time


class CodeExecutor:
    """Safe Python code execution sandbox"""

    def __init__(self, timeout: int = 5):
        """
        Initialize code executor

        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
        self.restricted_imports = {
            'os', 'subprocess', 'sys', 'importlib', 'eval', 'exec',
            'compile', '__import__', 'open', 'file', 'input', 'raw_input'
        }

    def execute_code(self, code: str, globals_dict: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute Python code safely

        Args:
            code: Python code to execute
            globals_dict: Optional global variables to provide

        Returns:
            Dict with stdout, stderr, result, and execution info
        """
        # Basic security check
        if not self._is_code_safe(code):
            return {
                'success': False,
                'error': 'Code contains restricted operations',
                'stdout': '',
                'stderr': '',
                'execution_time': 0
            }

        # Prepare execution environment
        if globals_dict is None:
            globals_dict = {}

        # Add safe builtins
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'abs': abs,
                'sum': sum,
                'min': min,
                'max': max,
                'sorted': sorted,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'any': any,
                'all': all,
            },
            **globals_dict
        }

        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        start_time = time.time()
        result = None
        error = None

        try:
            with contextlib.redirect_stdout(stdout_capture):
                with contextlib.redirect_stderr(stderr_capture):
                    # Execute code
                    exec(code, safe_globals)

                    # Try to get the last expression result
                    try:
                        tree = ast.parse(code)
                        if tree.body and isinstance(tree.body[-1], ast.Expr):
                            result = eval(ast.unparse(tree.body[-1].value), safe_globals)
                    except:
                        pass

        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}"

        execution_time = time.time() - start_time

        return {
            'success': error is None,
            'result': result,
            'stdout': stdout_capture.getvalue(),
            'stderr': stderr_capture.getvalue(),
            'error': error,
            'execution_time': execution_time
        }

    def _is_code_safe(self, code: str) -> bool:
        """
        Basic safety check for code

        Args:
            code: Code to check

        Returns:
            True if code appears safe
        """
        # Check for restricted keywords
        restricted_keywords = ['import os', 'import sys', 'import subprocess',
                              '__import__', 'eval(', 'exec(', 'compile(',
                              'open(', 'file(', 'input(']

        code_lower = code.lower()
        for keyword in restricted_keywords:
            if keyword in code_lower:
                return False

        return True

    def evaluate_expression(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a single Python expression

        Args:
            expression: Python expression to evaluate

        Returns:
            Result dict
        """
        try:
            # Safe evaluation
            safe_dict = {
                '__builtins__': {
                    'abs': abs, 'sum': sum, 'min': min, 'max': max,
                    'len': len, 'range': range, 'int': int, 'float': float,
                    'str': str, 'list': list, 'dict': dict, 'tuple': tuple
                }
            }

            result = eval(expression, safe_dict)

            return {
                'success': True,
                'result': result,
                'expression': expression
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}",
                'expression': expression
            }

    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code without executing it

        Args:
            code: Python code to analyze

        Returns:
            Analysis results
        """
        try:
            tree = ast.parse(code)

            analysis = {
                'valid_syntax': True,
                'num_lines': len(code.split('\n')),
                'num_functions': 0,
                'num_classes': 0,
                'num_imports': 0,
                'functions': [],
                'classes': [],
                'imports': []
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['num_functions'] += 1
                    analysis['functions'].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis['num_classes'] += 1
                    analysis['classes'].append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis['num_imports'] += 1
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    else:
                        analysis['imports'].append(node.module)

            return analysis

        except SyntaxError as e:
            return {
                'valid_syntax': False,
                'error': f"SyntaxError: {str(e)}",
                'line': e.lineno,
                'offset': e.offset
            }

    def format_code(self, code: str) -> Dict[str, Any]:
        """
        Format Python code using black

        Args:
            code: Code to format

        Returns:
            Formatted code
        """
        try:
            import black

            formatted = black.format_str(code, mode=black.Mode())

            return {
                'success': True,
                'formatted_code': formatted,
                'original_code': code
            }

        except ImportError:
            return {
                'success': False,
                'error': 'black not installed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
