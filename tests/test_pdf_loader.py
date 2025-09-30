import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from src.data_processing.loader import DataLoader
from src.data_processing.preprocessor import Preprocessor


def test_preprocessor_fixes_spaced_characters():
    """Test that the preprocessor correctly fixes space-separated characters."""
    preprocessor = Preprocessor(keep_spaces=True, keep_numbers=True)
    
    # Test case 1: English words with spaces between characters
    text_with_spaces = "h e l l o w o r l d"
    cleaned = preprocessor.clean_text(text_with_spaces)
    assert "helloworld" in cleaned or "hello world" in cleaned
    
    # Test case 2: Mixed Chinese and English with spacing issues
    text_mixed = "这是 t e s t 测试"
    cleaned = preprocessor.clean_text(text_mixed)
    assert "test" in cleaned
    
    # Test case 3: Multiple spaces
    text_multi_space = "This   has    multiple     spaces"
    cleaned = preprocessor.clean_text(text_multi_space)
    assert "  " not in cleaned  # No double spaces should remain
    
    # Test case 4: Normal text should remain unchanged
    normal_text = "This is a normal sentence"
    cleaned = preprocessor.clean_text(normal_text)
    assert "This is a normal sentence" == cleaned


def test_preprocessor_preserves_chinese_text():
    """Test that Chinese text is preserved correctly."""
    preprocessor = Preprocessor(keep_spaces=True)
    
    chinese_text = "这是一个中文测试文本。包含标点符号！"
    cleaned = preprocessor.clean_text(chinese_text)
    assert "这是一个中文测试文本" in cleaned
    assert "包含标点符号" in cleaned


def test_loader_instantiation():
    """Test that DataLoader can be instantiated."""
    loader = DataLoader()
    assert loader is not None
    assert loader.SUPPORTED_EXTS == {'.pdf', '.docx', '.doc', '.wav', '.mp3'}


def test_loader_unsupported_file():
    """Test that DataLoader raises ValueError for unsupported file types."""
    loader = DataLoader()
    with pytest.raises(ValueError, match="Unsupported file type"):
        loader.load("/tmp/test.xyz")
