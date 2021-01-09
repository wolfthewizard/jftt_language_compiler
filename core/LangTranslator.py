from core.LangVariableTable import LangVariableTable
from core.LangRegisterMachine import LangRegisterMachine
from core.OperationTranslator import OperationTranslator
from core.ConditionTranslator import ConditionTranslator
from core.GenericTranslator import GenericTranslator
from model.internal.LangProgram import LangProgram
from model.nonterminals.Expression import Expression
from model.nonterminals.Value import Value
from model.nonterminals.Identifier import Identifier
from model.nonterminals.Condition import Condition
from model.commands.Assign import Assign
from model.commands.DeclareVariable import DeclareVariable
from model.commands.ForDownto import ForDownto
from model.commands.ForTo import ForTo
from model.commands.If import If
from model.commands.IfElse import IfElse
from model.commands.Read import Read
from model.commands.RepeatUntil import RepeatUntil
from model.commands.While import While
from model.errors import *


class LangTranslator:

    def __init__(self, variable_table: LangVariableTable, register_machine: LangRegisterMachine,
                 generic_translator: GenericTranslator):
        self.variable_table = variable_table
        self.register_machine = register_machine

        self.operation_translator = OperationTranslator(variable_table, register_machine, generic_translator)
        self.condition_translator = ConditionTranslator(variable_table, register_machine, generic_translator)
        self.generic_translator = GenericTranslator(variable_table, register_machine)

    def translate_program(self, program: LangProgram):
        for declaration in program.declarations:
            self.__declare(declaration)
        code = self.__generate_code(program.commands)
        code += "\nHALT"
        return code

    def __declare(self, declaration):
        try:
            if type(declaration) == DeclareVariable:
                self.__declare_variable(declaration.name)
            else:
                self.__declare_array(declaration.name, declaration.first, declaration.last)
        except CodeException as e:
            raise type(e)(e.args[0].format(declaration.lineno))

    def __generate_code(self, commands: list) -> str:
        command_codes = []
        for command in commands:
            command_codes.append(self.__unwrap_command(command))
        code = "\n".join(command_codes)
        return code

    def __unwrap_command(self, command) -> str:
        try:
            if type(command) == Assign:
                return self.__assign(command.changed_identifier, command.assigned_expression)
            elif type(command) == If:
                return self.__if_then(command.condition, command.commands)
            elif type(command) == IfElse:
                return self.__if_then_else(command.condition, command.positive_commands, command.negative_commands)
            elif type(command) == While:
                return self.__while_do(command.condition, command.commands)
            elif type(command) == RepeatUntil:
                return self.__repeat_until(command.commands, command.condition)
            elif type(command) == ForTo:
                return self.__for_to(command.idd, command.from_value, command.to_value, command.commands)
            elif type(command) == ForDownto:
                return self.__for_downto(command.idd, command.from_value, command.downto_value, command.commands)
            elif type(command) == Read:
                return self.__read(command.idd)
            else:
                return self.__write(command.value)
        except CodeException as e:
            raise type(e)(e.args[0].format(command.lineno))

    def __declare_variable(self, name):
        self.variable_table.add_variable(name)

    def __declare_array(self, name, first, last):
        self.variable_table.add_array(name, first, last)

    def __assign(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        if assigned_expression.is_value():
            return self.__assign_value(changed_identifier, assigned_expression.val1)
        else:
            return self.__assign_expression(changed_identifier, assigned_expression)

    def __assign_value(self, changed_identifier: Identifier, assigned_value: Value) -> str:
        value_reg = self.register_machine.fetch_register()
        address_reg = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(assigned_value, register=value_reg)
        code += "\n" + self.generic_translator.put_address_to_register(changed_identifier, register=address_reg,
                                                                       initialize=True)
        code += "\nSTORE {} {}".format(value_reg, address_reg)
        return code

    def __assign_expression(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        address_reg = self.register_machine.fetch_register()

        code = self.generic_translator.put_address_to_register(changed_identifier, register=address_reg,
                                                               initialize=True)
        feedback = self.operation_translator.perform_operation(assigned_expression.val1, assigned_expression.val2,
                                                               operation=assigned_expression.operation)
        code += "\n" + feedback.code
        code += "\nSTORE {} {}".format(feedback.register, address_reg)
        return code

    def __if_then_else(self, condition: Condition, positive_commands: list, negative_commands: list) -> str:
        positive_commands_code = self.__generate_code(positive_commands)
        negative_commands_code = self.__generate_code(negative_commands)
        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.generic_translator.put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.condition_translator.perform_comparison(val1_reg, val2_reg, condition.comparison).format(
            self.generic_translator.line_count(positive_commands_code) + 2)
        code += "\n" + positive_commands_code
        code += "\nJUMP {}".format(self.generic_translator.line_count(negative_commands_code) + 1)
        code += "\n" + negative_commands_code
        return code

    def __if_then(self, condition: Condition, commands: list) -> str:
        commands_code = self.__generate_code(commands)
        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.generic_translator.put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.condition_translator.perform_comparison(val1_reg, val2_reg, condition.comparison).format(
            self.generic_translator.line_count(commands_code) + 1)
        code += "\n" + commands_code
        return code

    def __while_do(self, condition: Condition, commands: list) -> str:
        commands_code = self.__generate_code(commands)        # code has to be generated before fetching registers
        val1_reg = self.register_machine.fetch_register()   # because condition check requires registers to be freshly
        val2_reg = self.register_machine.fetch_register()   # fetched; in other case borrowed register inside check
        # may be one of assigned registers
        code = self.generic_translator.put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.generic_translator.put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.condition_translator.perform_comparison(val1_reg, val2_reg, condition.comparison).format(
            self.generic_translator.line_count(commands_code) + 2)
        code += "\n" + commands_code
        code += "\nJUMP {}".format(-self.generic_translator.line_count(code))
        return code

    def __repeat_until(self, commands: list, condition: Condition) -> str:
        commands_code = self.__generate_code(commands)
        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = commands_code
        code += "\n" + self.generic_translator.put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.generic_translator.put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.condition_translator.perform_comparison(val1_reg, val2_reg, condition.comparison)
        code = code.format(-self.generic_translator.line_count(code) + 1)
        return code

    def __for_to(self, idd: str, from_value: Value, to_value: Value, commands: list):
        self.variable_table.add_iterator(idd)
        counter = self.variable_table.fetch_random_variable()
        commands_code = self.__generate_code(commands)
        iterator_reg = self.register_machine.fetch_register()
        counter_reg = self.register_machine.fetch_register()
        temp_reg = self.register_machine.fetch_register()

        pre_run_code = self.generic_translator.put_value_to_register(from_value, iterator_reg, ignore_iterator=idd)
        pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), temp_reg)
        pre_run_code += "\nSTORE {} {}".format(iterator_reg, temp_reg)
        pre_run_code += "\n" + self.generic_translator.put_value_to_register(to_value, counter_reg, ignore_iterator=idd)
        pre_run_code += "\nINC {}".format(counter_reg)
        pre_run_code += "\nSUB {} {}".format(counter_reg, iterator_reg)
        pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(counter), temp_reg,
                                                                               initialize=True)

        code = "JZERO {}".format(counter_reg) + " {}"
        code += "\nSTORE {} {}".format(counter_reg, temp_reg)
        code += "\n" + commands_code
        code += "\n" + self.generic_translator.generate_constant(self.variable_table.get_address(idd), temp_reg)
        code += "\nLOAD {} {}".format(iterator_reg, temp_reg)
        code += "\nINC {}".format(iterator_reg)
        code += "\nSTORE {} {}".format(iterator_reg, temp_reg)
        code += "\n" + self.generic_translator.put_address_to_register(Identifier(counter), temp_reg)
        code += "\nLOAD {} {}".format(counter_reg, temp_reg)
        code += "\nDEC {}".format(counter_reg)
        code += "\nJUMP {}".format(-self.generic_translator.line_count(code))
        code = code.format(self.generic_translator.line_count(code))

        self.variable_table.remove_variable(counter)
        self.variable_table.remove_iterator(idd)
        return pre_run_code + "\n" + code

    def __for_downto(self, idd: str, from_value: Value, downto_value: Value, commands: list):
        self.variable_table.add_iterator(idd)
        counter = self.variable_table.fetch_random_variable()
        commands_code = self.__generate_code(commands)
        iterator_reg = self.register_machine.fetch_register()
        counter_reg = self.register_machine.fetch_register()
        temp_reg = self.register_machine.fetch_register()

        pre_run_code = self.generic_translator.put_value_to_register(from_value, iterator_reg, ignore_iterator=idd)
        pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), temp_reg)
        pre_run_code += "\nSTORE {} {}".format(iterator_reg, temp_reg)
        pre_run_code += "\n" + self.generic_translator.copy_register(iterator_reg, counter_reg)
        pre_run_code += "\nINC {}".format(counter_reg)
        pre_run_code += "\n" + self.generic_translator.put_value_to_register(downto_value, temp_reg,
                                                                             ignore_iterator=idd)
        pre_run_code += "\nSUB {} {}".format(counter_reg, temp_reg)
        pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(counter), temp_reg,
                                                                               initialize=True)

        code = "JZERO {}".format(counter_reg) + " {}"
        code += "\nSTORE {} {}".format(counter_reg, temp_reg)
        code += "\n" + commands_code
        code += "\n" + self.generic_translator.generate_constant(self.variable_table.get_address(idd), temp_reg)
        code += "\nLOAD {} {}".format(iterator_reg, temp_reg)
        code += "\nDEC {}".format(iterator_reg)
        code += "\nSTORE {} {}".format(iterator_reg, temp_reg)
        code += "\n" + self.generic_translator.put_address_to_register(Identifier(counter), temp_reg)
        code += "\nLOAD {} {}".format(counter_reg, temp_reg)
        code += "\nDEC {}".format(counter_reg)
        code += "\nJUMP {}".format(-self.generic_translator.line_count(code))
        code = code.format(self.generic_translator.line_count(code))

        self.variable_table.remove_iterator(idd)
        self.variable_table.remove_variable(counter)
        return pre_run_code + "\n" + code

    def __read(self, idd: Identifier) -> str:
        reg = self.register_machine.fetch_register()
        code = self.generic_translator.put_address_to_register(idd, register=reg, initialize=True)
        code += "\nGET {}".format(reg)
        return code

    def __write(self, val: Value) -> str:
        reg = self.register_machine.fetch_register()
        if val.is_int():
            reg2 = self.register_machine.fetch_register()
            code = self.generic_translator.put_value_to_register(val, register=reg)
            code += "\n" + self.generic_translator.generate_constant(self.variable_table.get_marker(), reg2)
            code += "\nSTORE {} {}".format(reg, reg2)
            code += "\nPUT {}".format(reg2)
        else:
            code = self.generic_translator.put_address_to_register(val.core, register=reg)
            code += "\nPUT {}".format(reg)
        return code
