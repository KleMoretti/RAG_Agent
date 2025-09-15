import re

class Preprocessor:
    """A class to preprocess text data."""
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)  # Remove punctuation
        return text.strip()

    def split_sentences(self, text: str) -> list:
        sentences = re.split(r'[。！？]', text)
        return [s.strip() for s in sentences if s.strip()]