class DomainError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictError(DomainError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class BadRequestError(DomainError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class UnauthorizedError(DomainError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=401)
