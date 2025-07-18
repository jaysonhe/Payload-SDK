"""
DJI PSDK Python Binding Exceptions

Custom exception classes for the DJI Payload SDK Python binding.
"""

class PSDKError(Exception):
    """Base exception class for PSDK Python binding"""
    
    def __init__(self, message: str, error_code: int = -1):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        if self.error_code != -1:
            return f"[{self.error_code}] {self.message}"
        return self.message

class PSDKInitError(PSDKError):
    """Exception raised when SDK initialization fails"""
    pass

class PSDKTimeoutError(PSDKError):
    """Exception raised when operations timeout"""
    pass

class PSDKConnectionError(PSDKError):
    """Exception raised when connection to aircraft fails"""
    pass

class PSDKConfigError(PSDKError):
    """Exception raised when configuration is invalid"""
    pass

class PSDKOperationError(PSDKError):
    """Exception raised when operations fail"""
    pass
