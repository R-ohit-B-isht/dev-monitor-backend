import pytest
from app.ai_service import analyze_code_complexity, analyze_code_readability
from datetime import datetime

def test_analyze_code_complexity_empty():
    """Test complexity analysis with empty input"""
    score = analyze_code_complexity("")
    assert score == 100  # Empty code should have perfect complexity score

def test_analyze_code_complexity_simple():
    """Test complexity analysis with simple code"""
    code = """
def simple_function():
    x = 1
    y = 2
    return x + y
"""
    score = analyze_code_complexity(code)
    assert score >= 90  # Simple code should have high score

def test_analyze_code_complexity_nested():
    """Test complexity analysis with nested structures"""
    code = """
def nested_function():
    for i in range(10):
        if i > 5:
            while True:
                try:
                    with open('file.txt') as f:
                        if f.read():
                            for line in f:
                                if line.strip():
                                    return line
                except:
                    pass
"""
    score = analyze_code_complexity(code)
    assert score <= 50  # Heavily nested code should have low score

def test_analyze_readability_empty():
    """Test readability analysis with empty input"""
    score = analyze_code_readability("")
    assert score == 0  # Empty code should have zero readability score

def test_analyze_readability_good_practices():
    """Test readability analysis with good coding practices"""
    code = """
def calculate_average(numbers):
    # Calculate the average of a list of numbers
    total = sum(numbers)
    count = len(numbers)
    
    # Avoid division by zero
    if count == 0:
        return 0
        
    return total / count
"""
    score = analyze_code_readability(code)
    assert score >= 80  # Well-documented code should have high score

def test_analyze_readability_poor_practices():
    """Test readability analysis with poor coding practices"""
    code = """
def x(y):
    z=0
    for i in y:z+=i
    return z/len(y) if len(y)>0 else 0
"""
    score = analyze_code_readability(code)
    assert score <= 60  # Poor practices should have low score

def test_analyze_readability_line_length():
    """Test readability analysis with long lines"""
    code = """
def very_long_function_name_that_exceeds_recommended_length_and_makes_code_harder_to_read_and_maintain(extremely_long_parameter_name_that_should_be_split_into_multiple_lines):
    return extremely_long_parameter_name_that_should_be_split_into_multiple_lines + 1
"""
    score = analyze_code_readability(code)
    assert score <= 70  # Long lines should reduce readability score

def test_analyze_readability_naming():
    """Test readability analysis with different naming conventions"""
    code = """
def calculate_total_price(base_price, tax_rate):
    # Good naming
    final_price = base_price * (1 + tax_rate)
    return final_price

def ctp(bp, tr):
    # Poor naming
    fp = bp * (1 + tr)
    return fp
"""
    good_score = analyze_code_readability(code.split('\n')[1:4])
    poor_score = analyze_code_readability(code.split('\n')[6:])
    assert good_score > poor_score  # Better naming should score higher

def test_analyze_readability_comments():
    """Test readability analysis with varying comment levels"""
    code_with_comments = """
# Function to calculate factorial
def factorial(n):
    # Base case
    if n == 0:
        return 1
    # Recursive case
    return n * factorial(n - 1)
"""
    code_without_comments = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""
    score_with_comments = analyze_code_readability(code_with_comments)
    score_without_comments = analyze_code_readability(code_without_comments)
    assert score_with_comments > score_without_comments  # Comments should improve score
