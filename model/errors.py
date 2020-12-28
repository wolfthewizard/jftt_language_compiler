class CodeException(Exception):
    pass


class VariableUnitilializedError(CodeException):

    def __init__(self, msg="error: variable uninitialized at line {}"):
        super().__init__(msg)


class NegativeValueError(CodeException):

    def __init__(self, msg="error: negative value at line {}"):
        super().__init__(msg)


class InvalidRangeError(CodeException):

    def __init__(self, msg="error: invalid array range at line {}"):
        super().__init__(msg)


class InvalidReferenceError(CodeException):

    def __init__(self, msg="error: wrong variable/array reference at line {}"):
        super().__init__(msg)


class SecondInitializationError(CodeException):

    def __init__(self, msg="error: second address assignment at line {}"):
        super().__init__(msg)


class ArrayOutOfBoundsError(CodeException):

    def __init__(self, msg="error: array out of bounds at line {}"):
        super().__init__(msg)


class VariableUndeclaredError(CodeException):

    def __init__(self, msg="error: undeclared variable at line {}"):
        super().__init__(msg)


class SecondDeclarationError(CodeException):

    def __init__(self, msg="error: second declaration at line {}"):
        super().__init__(msg)


class IteratorAssignmentError(CodeException):

    def __init__(self, msg="error: iterator assignment at line {}"):
        super().__init__(msg)
