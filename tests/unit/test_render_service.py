"""
Unit tests for render service.
"""
import pytest
from app.services.render_service import RenderService
from app.core.exceptions import ValidationError


class TestRenderService:
    """Test cases for RenderService."""
    
    def test_validate_dot_syntax_valid(self, sample_dot_code):
        """Test DOT validation with valid code."""
        # Should not raise exception
        RenderService.validate_dot_syntax(sample_dot_code)
    
    def test_validate_dot_syntax_too_short(self):
        """Test DOT validation with too short code."""
        with pytest.raises(ValidationError, match="too short"):
            RenderService.validate_dot_syntax("graph")
    
    def test_validate_dot_syntax_missing_graph(self):
        """Test DOT validation without graph declaration."""
        with pytest.raises(ValidationError, match="must start with"):
            RenderService.validate_dot_syntax("{ A -> B; }")
    
    def test_validate_dot_syntax_unbalanced_braces(self):
        """Test DOT validation with unbalanced braces."""
        with pytest.raises(ValidationError, match="Unbalanced braces"):
            RenderService.validate_dot_syntax("digraph test { A -> B;")
    
    def test_get_format_mime_type_svg(self):
        """Test MIME type for SVG format."""
        mime_type = RenderService.get_format_mime_type("svg")
        assert mime_type == "image/svg+xml"
    
    def test_get_format_mime_type_png(self):
        """Test MIME type for PNG format."""
        mime_type = RenderService.get_format_mime_type("png")
        assert mime_type == "image/png"
    
    def test_get_format_mime_type_unknown(self):
        """Test MIME type for unknown format."""
        mime_type = RenderService.get_format_mime_type("unknown")
        assert mime_type == "application/octet-stream"

