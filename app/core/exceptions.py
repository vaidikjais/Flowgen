"""
Custom Exceptions - Application-Specific Errors

Defines custom exception classes for different types of errors
that can occur in the application.
"""


class DiagramGPTException(Exception):
    """Base exception for all DiagramGPT errors."""
    
    def __init__(self, message: str, detail: str = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class DiagramGenerationError(DiagramGPTException):
    """Raised when diagram generation fails."""
    pass


class LLMError(DiagramGPTException):
    """Raised when LLM API call fails."""
    pass


class RenderError(DiagramGPTException):
    """Raised when Graphviz rendering fails."""
    pass


class ValidationError(DiagramGPTException):
    """Raised when DOT code validation fails."""
    pass


class ConfigurationError(DiagramGPTException):
    """Raised when configuration is invalid or missing."""
    pass


class ResourceNotFoundError(DiagramGPTException):
    """Raised when a requested resource is not found."""
    pass


class RateLimitError(DiagramGPTException):
    """Raised when rate limit is exceeded."""
    pass

