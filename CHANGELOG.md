# Changelog

## [Unreleased] - 2024

### Fixed
- **PDF Text Extraction**: Fixed issue where English words in PDFs were being recognized as individual spaced characters
  - Implemented PyMuPDF (fitz) as primary PDF extraction library with better text quality
  - Added PyPDF2 as fallback for compatibility
  - Implemented regex-based post-processing to remove excessive spacing (e.g., "h e l l o" → "hello")
  - Enhanced text preprocessing to handle mixed Chinese-English documents

### Changed
- **Type Hints**: Modernized type annotations to use Python 3.10+ style (e.g., `list[str]` instead of `List[str]`)
- **Error Handling**: Improved error logging throughout the application
  - All exceptions are now logged before being handled
  - Better error messages for debugging file processing issues
- **Dependencies**: Added PyMuPDF for better PDF text extraction

### Added
- **Environment Configuration**: Added `.env.example` file with documented configuration options
- **Tests**: Added comprehensive tests for PDF text preprocessing and character spacing fixes

## Usage Notes

### PDF Text Extraction
The system now uses PyMuPDF (fitz) as the primary library for extracting text from PDF files. This provides:
- Better text quality and formatting preservation
- Improved handling of spaced characters in English text
- Better support for mixed language documents (Chinese + English)

If PyMuPDF is not available, the system will automatically fall back to PyPDF2.

### Configuration
Copy `.env.example` to `.env` and configure your API keys and preferences:
```bash
cp .env.example .env
# Edit .env with your actual configuration
```
