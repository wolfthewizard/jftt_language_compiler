from model.errors import *


class LangArray:

    def __init__(self, first, last, adr):
        if last < first:
            raise InvalidRangeError

        self.__address = adr
        self.__bias = first
        self.__length = last - first + 1
        self.__initialized = True
        self.__values = [None] * self.__length

    def __str__(self):
        val_str = "[" + ", ".join(
            [str(self.__values[i]) if self.__values[i] is not None else "?" for i in range(self.__length)]) + "]"
        return val_str

    def __repr__(self):
        return str(self)

    def get_address(self, offset=None):
        if not self.__initialized:
            raise VariableUnitilializedError
        elif offset is None:
            raise InvalidReferenceError
        elif offset - self.__bias >= self.__length or offset - self.__bias < 0:
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

    def get_value(self, offset=None):
        if offset is None:
            return None
        elif offset - self.__bias >= self.__length or offset - self.__bias < 0:
            return None     # it's an exception, but it will be handled later
        else:
            return self.__values[offset - self.__bias]

    def set_value(self, value, offset=None):
        if offset is None:
            self.__values = [None] * self.__length
        elif offset - self.__bias >= self.__length or offset - self.__bias < 0:
            raise None     # it's an exception, but it will be handled later
        else:
            self.__values[offset - self.__bias] = value

    def merge(self, other):
        new = LangArray(self.__bias, self.__bias + self.__length - 1, self.__address)
        for i, val in enumerate(self.__values):
            new.__values[i] = val if val == other.__values[i] else None
        return new
