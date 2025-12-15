"""
Tests for filename sanitization to ensure special characters don't cause issues
with GCS uploads and eeu_data insertion.
"""
import pytest
from utils import sanitize_filename


class TestFilenameSanitization:
    """Test cases for sanitize_filename function"""
    
    def test_basic_filename(self):
        """Test that basic filenames pass through unchanged"""
        assert sanitize_filename("test_file.pdf") == "test_file.pdf"
        assert sanitize_filename("report.xlsx") == "report.xlsx"
    
    def test_parentheses(self):
        """Test that parentheses are replaced with underscores"""
        result = sanitize_filename("file (with parentheses).xlsx")
        assert "(" not in result
        assert ")" not in result
        assert result == "file_with_parentheses.xlsx"
    
    def test_spaces(self):
        """Test that spaces are replaced with underscores"""
        result = sanitize_filename("file with spaces.xlsx")
        assert " " not in result
        assert result == "file_with_spaces.xlsx"
    
    def test_dashes_preserved(self):
        """Test that dashes are preserved"""
        assert sanitize_filename("file-with-dashes.pdf") == "file-with-dashes.pdf"
    
    def test_underscores_preserved(self):
        """Test that underscores are preserved"""
        assert sanitize_filename("file_with_underscores.pdf") == "file_with_underscores.pdf"
    
    def test_complex_filename(self):
        """Test a complex filename with multiple special characters"""
        result = sanitize_filename("My Report (Draft-2023).pdf")
        # Should replace parentheses with underscores, preserve dashes
        assert "(" not in result
        assert ")" not in result
        assert result == "My_Report_Draft-2023.pdf"
    
    def test_multiple_consecutive_underscores(self):
        """Test that multiple consecutive underscores are collapsed"""
        result = sanitize_filename("Test___Multiple___Underscores.xlsx")
        assert "___" not in result
        assert result == "Test_Multiple_Underscores.xlsx"
    
    def test_special_url_characters(self):
        """Test that special URL characters are properly encoded"""
        result = sanitize_filename("file#with%special@chars.pdf")
        # These should be URL encoded
        assert "#" not in result or result.find("%23") != -1
        assert result == "file%23with%25special%40chars.pdf"
    
    def test_brackets(self):
        """Test that brackets are replaced"""
        result = sanitize_filename("file[with]brackets.pdf")
        assert "[" not in result
        assert "]" not in result
        assert result == "file_with_brackets.pdf"
    
    def test_leading_trailing_underscores_removed(self):
        """Test that leading and trailing underscores are removed"""
        assert sanitize_filename("_file_.pdf") == "file.pdf"
        assert sanitize_filename("__file__.pdf") == "file.pdf"
    
    def test_empty_basename(self):
        """Test that empty basenames get a default name"""
        result = sanitize_filename(".pdf")
        assert result == "file.pdf"
    
    def test_invalid_path_characters(self):
        """Test that path-related characters are removed"""
        result = sanitize_filename("file/with\\invalid:chars?.pdf")
        assert "/" not in result
        assert "\\" not in result
        assert ":" not in result
        assert "?" not in result
        # Should be: filewith invalid chars.pdf -> filewithinvalidchars.pdf
        assert result == "filewithinvalidchars.pdf"
    
    def test_preserves_extension(self):
        """Test that file extensions are preserved"""
        assert sanitize_filename("test.pdf").endswith(".pdf")
        assert sanitize_filename("test.xlsx").endswith(".xlsx")
        assert sanitize_filename("complex (file).txt").endswith(".txt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

