class WmsError(Exception):
    def __init__(self, message, code="INTERNAL_ERROR", status=500, errors=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.errors = errors


class InsufficientStockError(WmsError):
    def __init__(self, message, errors=None):
        super().__init__(message, code="INSUFFICIENT_STOCK", status=409, errors=errors)


class ConflictError(WmsError):
    def __init__(self, message, errors=None):
        super().__init__(message, code="CONFLICT", status=409, errors=errors)


class NotFoundError(WmsError):
    def __init__(self, message="资源不存在"):
        super().__init__(message, code="NOT_FOUND", status=404)


class ValidationError(WmsError):
    def __init__(self, message, errors=None):
        super().__init__(message, code="VALIDATION_ERROR", status=422, errors=errors)


class ForbiddenError(WmsError):
    def __init__(self, message="无权限"):
        super().__init__(message, code="FORBIDDEN", status=403)


class UnauthorizedError(WmsError):
    def __init__(self, message="未登录"):
        super().__init__(message, code="UNAUTHORIZED", status=401)
