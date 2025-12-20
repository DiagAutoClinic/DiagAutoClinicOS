# ai/core/exceptions.py

class ModelLoadError(Exception):
    """Raised when ML model loading fails."""
    pass

class CANDatabaseError(Exception):
    """Raised when CAN database operations fail."""
    pass

class InvalidInputError(Exception):
    """Raised when input data is invalid or malformed."""
    pass

class AIInitializationError(Exception):
    """Raised when AI system initialization fails."""
    pass

class DiagnosticError(Exception):
    """Raised when diagnostic process encounters an error."""
    pass