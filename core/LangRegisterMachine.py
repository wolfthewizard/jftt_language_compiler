class LangRegisterMachine:

    __registers = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f"
    ]

    def __init__(self):
        self.__marker = 0

    def fetch_register(self):
        register = LangRegisterMachine.__registers[self.__marker]
        self.__marker = (self.__marker + 1) % 6

        return register

    def borrow_register(self):
        return LangRegisterMachine.__registers[self.__marker]

    def borrow_registers(self, number: int):
        ret = []
        i = self.__marker
        for _ in range(number):
            ret.append(LangRegisterMachine.__registers[i])
            i = (i + 1) % 6
        return ret
