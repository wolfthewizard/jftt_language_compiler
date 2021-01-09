from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from model.nonterminals.Value import Value
from model.nonterminals.Identifier import Identifier


class GenericTranslator:

    def __init__(self, variable_table: LangVariableTable, register_machine: LangRegisterMachine):
        self.variable_table = variable_table
        self.register_machine = register_machine

    @staticmethod
    def line_count(text: str) -> int:
        return text.count("\n") + 1

    def put_value_to_register(self, val: Value, register, ignore_iterator=None) -> str:
        if val.is_int():
            return self.generate_constant(val.core, register)
        else:
            # if it's value is known, and not too big (1mil?) then put it as a constant to register
            code = self.put_address_to_register(val.core, register, ignore_iterator=ignore_iterator)
            code += "\nLOAD {} {}".format(register, register)
            return code

    def put_address_to_register(self, idd: Identifier, register, initialize=False, ignore_iterator=None) -> str:
        if idd.offset is None or type(idd.offset) == int:
            address = self.variable_table.get_address(idd.name, idd.offset, initialize, ignore_iterator)
            code = self.generate_constant(address, register)
            return code
        else:
            bias = self.variable_table.get_bias(idd.name)
            address = self.variable_table.get_address(idd.name, bias, initialize, ignore_iterator)
            reg = self.register_machine.borrow_register()

            code = self.generate_constant(address, register)
            code += "\n" + self.put_value_to_register(Value(Identifier(idd.offset)), register=reg)
            code += "\nADD {} {}".format(register, reg)
            code += "\n" + self.put_value_to_register(Value(bias), register=reg)
            code += "\nSUB {} {}".format(register, reg)
            return code

    @staticmethod
    def copy_register(source_reg: str, dest_reg: str):
        return "RESET {}\nADD {} {}".format(dest_reg, dest_reg, source_reg)

    @staticmethod
    def generate_constant(value: int, register) -> str:
        if value < 0:
            raise ValueError("Stuck upon negative value; please report this error along with stacktrace.")
        commands = []
        while value:
            if value % 2:
                commands.append("INC {}".format(register))
                value -= 1
            else:
                commands.append("SHL {}".format(register))
                value //= 2
        commands.append("RESET {}".format(register))
        return "\n".join(commands[::-1])
