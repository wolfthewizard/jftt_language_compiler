from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from model.nonterminals.Expression import Expression
from model.nonterminals.Value import Value
from model.nonterminals.Identifier import Identifier
from model.nonterminals.Condition import Condition


class LangTranslator:

    def __init__(self):
        self.variable_table = LangVariableTable()
        self.register_machine = LangRegisterMachine()

    def __put_value_to_register(self, val: Value, register, initialize=False) -> str:
        if val.is_int():
            return self.__generate_constant(val.core, register)
        else:
            code = self.__put_address_to_register(val.core, register, initialize)
            code += "\n" + "LOAD {} {}".format(register, register)
            return code

    def __put_address_to_register(self, idd: Identifier, register, initialize=False) -> str:
        if idd.offset is None or type(idd.offset) == int:
            address = self.variable_table.get_address(idd.name, idd.offset, initialize)
            code = self.__generate_constant(address, register)
            return code
        else:
            bias = self.variable_table.get_bias(idd.name)
            address = self.variable_table.get_address(idd.name, bias, initialize)
            reg = self.register_machine.borrow_register()

            code = self.__generate_constant(address, register)
            code += "\n" + self.__put_value_to_register(Value(Identifier(idd.offset)), register=reg)
            code += "\nADD {} {}".format(register, reg)
            code += "\n" + self.__put_value_to_register(Value(bias), register=reg)
            code += "\nSUB {} {}".format(register, reg)
            return code

    @staticmethod
    def __generate_constant(value: int, register) -> str:
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

    def declare_variable(self, name):
        self.variable_table.add_variable(name)

    def declare_array(self, name, first, last):
        self.variable_table.add_array(name, first, last)

    def assign(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        if assigned_expression.is_value():
            return self.__assign_value(changed_identifier, assigned_expression.val1)
        else:
            pass    # todo: implement handling operations (will probably split method)

    def __assign_value(self, changed_identifier: Identifier, assigned_value: Value) -> str:
        reg1 = self.register_machine.fetch_register()
        reg2 = self.register_machine.fetch_register()
        code = self.__put_value_to_register(assigned_value, register=reg1)
        code += "\n" + self.__put_address_to_register(changed_identifier, register=reg2, initialize=True)
        code += "\nSTORE {} {}".format(reg1, reg2)
        return code

    def read(self, idd: Identifier) -> str:
        reg = self.register_machine.fetch_register()
        code = self.__put_address_to_register(idd, register=reg, initialize=True)
        code += "\nGET {}".format(reg)
        return code

    def write(self, val: Value) -> str:
        reg = self.register_machine.fetch_register()
        if val.is_int():
            reg2 = self.register_machine.fetch_register()
            code = self.__put_value_to_register(val, register=reg)
            code += "\nRESET {}".format(reg2)
            code += "\nSTORE {} {}".format(reg, reg2)
            code += "\nPUT {}".format(reg2)
        else:
            code = self.__put_address_to_register(val.core, register=reg)
            code += "\nPUT {}".format(reg)
        return code
