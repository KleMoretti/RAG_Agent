#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstration script to show the PDF text extraction fix.
This script tests the text preprocessing functionality without requiring dependencies.
"""

import re


def clean_text(text: str) -> str:
    """
    Standalone version of the clean_text function for demonstration.
    This mirrors the implementation in src/data_processing/preprocessor.py
    """
    if not text:
        return ""

    # Fix space-separated characters (common PDF extraction issue)
    # Match patterns like "h e l l o" and convert to "hello"
    text = re.sub(r'\b(\w) (?=\w\b)', r'\1', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Normalize line breaks and spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def print_separator(char='=', width=70):
    """Print a separator line."""
    print(char * width)


def test_preprocessing():
    """Demonstrate the text preprocessing fix for spaced characters."""
    
    print_separator()
    print("PDF TEXT EXTRACTION FIX - DEMONSTRATION")
    print_separator()
    print()
    
    # Test cases simulating problematic PDF extraction
    test_cases = [
        {
            "name": "English words with spaced characters",
            "input": "M a c h i n e   L e a r n i n g is the future",
            "expected": "Machine Learning is the future"
        },
        {
            "name": "Mixed Chinese and English",
            "input": "这是 D e e p   L e a r n i n g 深度学习的应用",
            "expected": "这是 Deep Learning 深度学习的应用"
        },
        {
            "name": "Multiple consecutive spaces",
            "input": "This    document     has      many       spaces",
            "expected": "This document has many spaces"
        },
        {
            "name": "PDF extraction artifact simulation",
            "input": "P D F  text  e x t r a c t i o n  error",
            "expected": "PDF text extraction error"
        },
        {
            "name": "Normal text (should remain unchanged)",
            "input": "Normal text without spacing issues",
            "expected": "Normal text without spacing issues"
        },
        {
            "name": "Chinese text preservation",
            "input": "这是一个正常的中文文本。没有问题！",
            "expected": "这是一个正常的中文文本。没有问题！"
        }
    ]
    
    # Run tests and display results
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print("-" * 70)
        
        # Process the text using standalone clean_text function
        result = clean_text(test['input'])
        
        # Check if it matches expected (approximately)
        # We normalize spaces for comparison since clean_text might produce slightly different spacing
        result_normalized = ' '.join(result.split())
        expected_normalized = ' '.join(test['expected'].split())
        
        is_pass = result_normalized == expected_normalized or result == test['expected']
        status = "✅ PASS" if is_pass else "❌ FAIL"
        
        if is_pass:
            passed += 1
        else:
            failed += 1
        
        print(f"Input:    {test['input']}")
        print(f"Output:   {result}")
        print(f"Expected: {test['expected']}")
        print(f"Status:   {status}")
        print()
    
    # Summary
    print_separator()
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print_separator()
    print()
    
    if failed == 0:
        print("✅ All tests passed! The PDF text extraction fix is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review the output above.")
    
    print()
    print("Note: The fix uses two regex patterns:")
    print("  1. r'\\b(\\w) (?=\\w\\b)' - Removes spaces between single characters")
    print("  2. r' {2,}' - Consolidates multiple spaces to single space")
    print()
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = test_preprocessing()
    sys.exit(0 if success else 1)
