"""
Custom Exceptions - Application-Specific Errors

Defines custom exception classes for different types of errors
that can occur in the application.
"""


class FlowgenException(Exception):
    """Base exception for all Flowgen errors."""
    
    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class DiagramGenerationError(FlowgenException):
    """Raised when diagram generation fails."""
    pass


class LLMError(FlowgenException):
    """Raised when LLM API call fails."""
    pass


class RenderError(FlowgenException):
    """Raised when Graphviz rendering fails."""
    pass


class ValidationError(FlowgenException):
    """Raised when DOT code validation fails."""
    pass


class ConfigurationError(FlowgenException):
    """Raised when configuration is invalid or missing."""
    pass


class ResourceNotFoundError(FlowgenException):
    """Raised when a requested resource is not found."""
    pass


class RateLimitError(FlowgenException):
    """Raised when rate limit is exceeded."""
    pass