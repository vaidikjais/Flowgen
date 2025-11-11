"""
Unit tests for hash utilities.
"""
import pytest
from app.utils.hash_utils import hash_prompt, verify_hash, truncate_hash


def test_hash_prompt_deterministic():
    """Test that hash_prompt produces deterministic results."""
    prompt = "Create a flowchart"
    format = "svg"
    layout = "dot"
    
    hash1 = hash_prompt(prompt, format, layout)
    hash2 = hash_prompt(prompt, format, layout)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 produces 64 character hex string


def test_hash_prompt_different_inputs():
    """Test that different inputs produce different hashes."""
    prompt1 = "Create a flowchart"
    prompt2 = "Create a network diagram"
    
    hash1 = hash_prompt(prompt1, "svg", "dot")
    hash2 = hash_prompt(prompt2, "svg", "dot")
    
    assert hash1 != hash2


def test_hash_prompt_case_insensitive():
    """Test that hash is case-insensitive for prompts."""
    hash1 = hash_prompt("Create a Flowchart", "svg", "dot")
    hash2 = hash_prompt("create a flowchart", "svg", "dot")
    
    assert hash1 == hash2


def test_hash_prompt_format_sensitive():
    """Test that hash is sensitive to format changes."""
    prompt = "Create a flowchart"
    
    hash_svg = hash_prompt(prompt, "svg", "dot")
    hash_png = hash_prompt(prompt, "png", "dot")
    
    assert hash_svg != hash_png


def test_verify_hash_correct():
    """Test hash verification with correct hash."""
    prompt = "Create a flowchart"
    format = "svg"
    layout = "dot"
    
    expected_hash = hash_prompt(prompt, format, layout)
    
    assert verify_hash(prompt, format, layout, expected_hash) is True


def test_verify_hash_incorrect():
    """Test hash verification with incorrect hash."""
    prompt = "Create a flowchart"
    format = "svg"
    layout = "dot"
    
    wrong_hash = "0" * 64
    
    assert verify_hash(prompt, format, layout, wrong_hash) is False


def test_truncate_hash():
    """Test hash truncation."""
    full_hash = "a" * 64
    
    truncated = truncate_hash(full_hash, length=8)
    
    assert truncated == "a" * 8
    assert len(truncated) == 8

