from LangVariableTable import LangVariableTable


class LangTranslator:

    def __init__(self):
        self.variable_table = LangVariableTable()

    def declare_variable(self, name):
        self.variable_table.add_variable(name)

    def declare_array(self, name, first, last):
        self.variable_table.add_array(name, first, last)

    def assign_value(self, variable_name, value):
        code = ""
        address = self.variable_table.init_and_get_address(variable_name)
        code += self.generate_constant(value) + "\n"
        code += self.generate_constant(address, "b") + "\n"
        code += "STORE a b"
        return code

    @staticmethod
    def generate_constant(value, register="a"):
        commands = []
        while value:
            if value % 2:
                commands.append("INC " + register)
                value -= 1
            else:
                commands.append("SHL " + register)
                value //= 2
        commands.append("RESET " + register)
        return "\n".join(commands[::-1])

    def read(self, variable_name):
        code = ""
        address = self.variable_table.init_and_get_address(variable_name)
        code += self.generate_constant(address) + "\n"
        code += "GET a"
        return code

    def write(self, variable_name):
        code = ""
        address = self.variable_table.get_address(variable_name)
        code += self.generate_constant(address) + "\n"
        code += "PUT a"
        return code
