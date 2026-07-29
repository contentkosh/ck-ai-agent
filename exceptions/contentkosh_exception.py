class ContentKoshException(Exception):
    """
    Base exception for all repository failures.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message