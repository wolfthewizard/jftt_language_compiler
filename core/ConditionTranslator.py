from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from core.GenericTranslator import GenericTranslator


class ConditionTranslator:

    def __init__(self, variable_table: LangVariableTable, register_machine: LangRegisterMachine,
                 generic_translator: GenericTranslator):
        self.variable_table = variable_table
        self.register_machine = register_machine
        self.generic_translator = generic_translator

    def perform_comparison(self, reg1: str, reg2: str, comparison: str):
        if comparison == "=":
            return self.__perform_equality(reg1, reg2)
        elif comparison == "!=":
            return self.__perform_inequality(reg1, reg2)
        elif comparison == "<":
            return self.__perform_less(reg1, reg2)
        elif comparison == ">":
            return self.__perform_more(reg1, reg2)
        elif comparison == "<=":
            return self.__perform_less_equal(reg1, reg2)
        else:
            return self.__perform_more_equal(reg1, reg2)

    def __perform_equality(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 5"
        code += "\n" + self.generic_translator.copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code

    def __perform_inequality(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 7"
        code += "\n" + self.generic_translator.copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP 2"
        code += "\nJUMP {}"
        return code

    def __perform_less(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.generic_translator.copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {}".format(condition_reg) + " {}"
        return code

    def __perform_more(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {}".format(condition_reg) + " {}"
        return code

    def __perform_less_equal(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.generic_translator.copy_register(reg1, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg2)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code

    def __perform_more_equal(self, reg1: str, reg2: str):
        condition_reg = self.register_machine.borrow_register()
        code = self.generic_translator.copy_register(reg2, condition_reg)
        code += "\nSUB {} {}".format(condition_reg, reg1)
        code += "\nJZERO {} 2".format(condition_reg)
        code += "\nJUMP {}"
        return code
