from model.commands.DeclareVariable import DeclareVariable
from model.commands.DeclareArray import DeclareArray


class LangProgram:

    def __init__(self, declarations: list, commands: list):
        self.declarations = declarations
        self.commands = commands

    def get_variable_declarations(self):
        return [d for d in self.declarations if type(d) == DeclareVariable]

    def get_array_declarations(self):
        return [d for d in self.declarations if type(d) == DeclareArray]

    def get_variable_and_unary_array_declarations(self):
        return [d for d in self.declarations if type(d) == DeclareVariable or d.first == d.last]

    def get_non_unary_array_declarations(self):
        return [d for d in self.declarations if type(d) == DeclareArray and d.first != d.last]
