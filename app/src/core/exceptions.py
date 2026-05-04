class PaymentNotFoundError(Exception):
    ...


class IdempotencyConflictError(Exception):
    ...


class PaymentProcessingError(Exception):
    pass
