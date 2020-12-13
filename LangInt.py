from errors import *


class LangInt:

    def __init__(self, adr):
        self.__address = adr
        self.__initialized = False

    def get_address(self, offset=None):
        if not self.__initialized:
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
        return self.__initialized

    def initialize(self):
        self.__initialized = True
