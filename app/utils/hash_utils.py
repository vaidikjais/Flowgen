"""
Hash Utilities - Prompt Hashing for Cache Lookup

Provides utilities for creating deterministic hashes of prompts
to enable efficient cache lookup.
"""
import hashlib
from typing import Optional


def hash_prompt(
    prompt: str,
    format: str = "svg",
    layout: str = "dot"
) -> str:
    """
    Create a deterministic SHA-256 hash of a prompt with parameters.
    
    The hash includes the prompt text, format, and layout to ensure
    that different rendering parameters produce different cache keys.
    
    Args:
        prompt: Natural language prompt
        format: Output format (svg or png)
        layout: Graphviz layout engine
        
    Returns:
        Hexadecimal hash string (64 characters)
        
    Example:
        >>> hash_prompt("create a flowchart", "svg", "dot")
        'a1b2c3d4e5f6...'
    """
    # Normalize input
    normalized_prompt = prompt.strip().lower()
    normalized_format = format.lower()
    normalized_layout = layout.lower()
    
    # Combine all parameters into a single string
    cache_key = f"{normalized_prompt}|{normalized_format}|{normalized_layout}"
    
    # Create SHA-256 hash
    hash_object = hashlib.sha256(cache_key.encode('utf-8'))
    return hash_object.hexdigest()


def verify_hash(
    prompt: str,
    format: str,
    layout: str,
    expected_hash: str
) -> bool:
    """
    Verify that a prompt matches an expected hash.
    
    Args:
        prompt: Natural language prompt
        format: Output format
        layout: Graphviz layout engine
        expected_hash: Hash to compare against
        
    Returns:
        True if hash matches, False otherwise
    """
    computed_hash = hash_prompt(prompt, format, layout)
    return computed_hash == expected_hash


def truncate_hash(hash_str: str, length: int = 8) -> str:
    """
    Truncate a hash to a shorter length for display purposes.
    
    Args:
        hash_str: Full hash string
        length: Desired length
        
    Returns:
        Truncated hash string
    """
    return hash_str[:length]

