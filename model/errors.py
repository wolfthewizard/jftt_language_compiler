class CodeException(Exception):
    pass


class VariableUnitilializedError(CodeException):

    def __init__(self, msg="error: variable {} uninitialized", ref=None):
        if ref is None:
            super().__init__(msg)
        else:
            super().__init__(msg.format(ref) + " at line {}")


class InvalidRangeError(CodeException):

    def __init__(self, msg="error: array {} has invalid range", ref=None):
        if ref is None:
            super().__init__(msg)
        else:
            super().__init__(msg.format(ref) + " at line {}")


class ArrayAsVariableReferenceError(CodeException):

    def __init__(self, msg="error: array {} referenced as variable", ref=None):
        if ref is None:
            super().__init__(msg)
        else:
            super().__init__(msg.format(ref) + " at line {}")


class VariableAsArrayReferenceError(CodeException):

    def __init__(self, msg="error: variable {} referenced as array", ref=None):
        if ref is None:
            super().__init__(msg)
        else:
            super().__init__(msg.format(ref) + " at line {}")


class SecondInitializationError(CodeException):

    def __init__(self, msg="internal error: second address assignment"):
        super().__init__(msg)


class ArrayOutOfBoundsError(CodeException):

    def __init__(self, msg="error: array {} referenced out of bounds", ref=None):
        if ref is None:
            super().__init__(msg)
        else:
            super().__init__(msg.format(ref) + " at line {}")


class VariableUndeclaredError(CodeException):

    def __init__(self, msg="error: undeclared variable {}", ref=None):
        if ref is None:
            super().__init__(msg)
        else:
            super().__init__(msg.format(ref) + " at line {}")


class SecondDeclarationError(CodeException):

    def __init__(self, msg="error: {} is declared second time", ref=None):
        if ref is None:
            super().__init__(msg)
        else:
            super().__init__(msg.format(ref) + " at line {}")


class IteratorAssignmentError(CodeException):

    def __init__(self, msg="error: iterator {} is assigned value", ref=None):
        if ref is None:
            super().__init__(msg)
        else:
            super().__init__(msg.format(ref) + " at line {}")
