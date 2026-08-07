class ContentKoshException(Exception):
    """
    Base exception for all repository failures.
    """
    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.cause = cause