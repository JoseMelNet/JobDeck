"""Application-specific exceptions."""


class ApplicationError(Exception):
    """Base application error."""


class ValidationError(ApplicationError):
    """Raised when input data is invalid."""


class RepositoryError(ApplicationError):
    """Raised when a persistence operation fails."""


class AnalysisError(ApplicationError):
    """Raised when vacancy analysis fails."""
