from model.errors import *


class LangArray:

    def __init__(self, first, last, adr):
        if last < first:
            raise InvalidRangeError

        if first < 0:
            raise NegativeValueError

        self.__address = adr
        self.__bias = first
        self.__length = last - first + 1
        self.__initialized = False

    def get_address(self, offset=None):
        if not self.__initialized:
            raise VariableUnitilializedError
        elif offset is None:
            raise InvalidReferenceError("Array is not a variable.")
        elif offset - self.__bias >= self.__length:
            raise ArrayOutOfBoundsError
        else:
            return self.__address + offset - self.__bias

    def get_bias(self):
        return self.__bias

    def set_address(self, adr):
        self.__address = adr

    def __len__(self):
        return self.__length

    def is_initialized(self):
        return self.__initialized

    def initialize(self):
        self.__initialized = True
