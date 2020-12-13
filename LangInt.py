from errors import *


class LangInt:

    def __init__(self):
        self.__address = None

    def get_address(self, offset=None):
        if self.__address is None:
            raise VariableUnitilializedError
        elif offset is not None:
            raise InvalidReferenceError("Variable is not an array.")
        else:
            return self.__address

    def set_address(self, adr):
        if self.__address is not None:
            raise SecondInitializationError
        self.__address = adr

    def is_initialized(self):
        return self.__address is not None
