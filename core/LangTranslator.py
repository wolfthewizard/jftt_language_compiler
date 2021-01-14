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

    LOOP_EXPANSION_THRESHOLD = 32

    def __init__(self, variable_table: LangVariableTable, register_machine: LangRegisterMachine,
                 operation_translator: OperationTranslator, condition_translator: ConditionTranslator,
                 generic_translator: GenericTranslator):
        self.variable_table = variable_table
        self.register_machine = register_machine
        self.operation_translator = operation_translator
        self.condition_translator = condition_translator
        self.generic_translator = generic_translator

    def __set_variable_table(self, variable_table: LangVariableTable):
        self.variable_table = variable_table
        self.operation_translator.variable_table = variable_table
        self.condition_translator.variable_table = variable_table
        self.generic_translator.variable_table = variable_table

    def __set_register_machine(self, register_machine: LangRegisterMachine):
        self.register_machine = register_machine
        self.operation_translator.register_machine = register_machine
        self.condition_translator.register_machine = register_machine
        self.generic_translator.register_machine = register_machine

    def translate_program(self, program: LangProgram):
        for declaration in program.get_variable_and_unary_array_declarations():
            self.__declare(declaration)
        for declaration in program.get_non_unary_array_declarations():
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

        val = self.generic_translator.reflect_on_value(assigned_value)
        if val.is_int():
            self.variable_table.set_value(val.core, changed_identifier.name, changed_identifier.offset)
            code = self.generic_translator.put_value_to_register(assigned_value, register=value_reg)
        else:
            self.variable_table.set_value(None, changed_identifier.name, changed_identifier.offset)
            code = self.generic_translator.put_value_to_register(assigned_value, register=value_reg)
        code += "\n" + self.generic_translator.put_address_to_register(changed_identifier, register=address_reg,
                                                                       initialize=True)
        code += "\nSTORE {} {}".format(value_reg, address_reg)
        return code

    def __assign_expression(self, changed_identifier: Identifier, assigned_expression: Expression) -> str:
        address_reg = self.register_machine.fetch_register()

        code = self.generic_translator.put_address_to_register(changed_identifier, register=address_reg,
                                                               initialize=True)
        val1 = self.generic_translator.reflect_on_value(assigned_expression.val1)
        val2 = self.generic_translator.reflect_on_value(assigned_expression.val2)
        feedback = self.operation_translator.perform_operation(val1, val2, operation=assigned_expression.operation,
                                                               changed_identifier=changed_identifier)
        code += "\n" + feedback.code
        code += "\nSTORE {} {}".format(feedback.register, address_reg)
        return code

    def __if_then_else(self, condition: Condition, positive_commands: list, negative_commands: list) -> str:
        original_var_table = self.variable_table
        branch1_var_table = self.variable_table.clone()
        branch2_var_table = self.variable_table.clone()
        self.__set_variable_table(branch1_var_table)
        positive_commands_code = self.__generate_code(positive_commands)
        self.__set_variable_table(branch2_var_table)
        negative_commands_code = self.__generate_code(negative_commands)
        self.__set_variable_table(original_var_table)
        self.variable_table.merge_from_two(branch1_var_table, branch2_var_table)

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
        original_var_table = self.variable_table
        branch_var_table = self.variable_table.clone()
        self.__set_variable_table(branch_var_table)
        commands_code = self.__generate_code(commands)
        self.__set_variable_table(original_var_table)
        self.variable_table.merge_from_one(branch_var_table)

        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.generic_translator.put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.condition_translator.perform_comparison(val1_reg, val2_reg, condition.comparison).format(
            self.generic_translator.line_count(commands_code) + 1)
        code += "\n" + commands_code
        return code

    def __while_do(self, condition: Condition, commands: list) -> str:
        # code has to be generated before fetching registers because condition check requires registers to be freshly
        # fetched; in other case borrowed register inside check may be one of assigned registers
        changed_identifiers = self.generic_translator.get_changed_identifiers(commands)
        self.variable_table.unset_from_list(changed_identifiers)
        commands_code = self.__generate_code(commands)
        self.variable_table.unset_from_list(changed_identifiers)
        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = self.generic_translator.put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.generic_translator.put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.condition_translator.perform_comparison(val1_reg, val2_reg, condition.comparison).format(
            self.generic_translator.line_count(commands_code) + 2)
        code += "\n" + commands_code
        code += "\nJUMP {}".format(-self.generic_translator.line_count(code))
        return code

    def __repeat_until(self, commands: list, condition: Condition) -> str:
        changed_identifiers = self.generic_translator.get_changed_identifiers(commands)
        self.variable_table.unset_from_list(changed_identifiers)
        commands_code = self.__generate_code(commands)
        self.variable_table.unset_from_list(changed_identifiers)

        val1_reg = self.register_machine.fetch_register()
        val2_reg = self.register_machine.fetch_register()

        code = commands_code
        code += "\n" + self.generic_translator.put_value_to_register(condition.val1, register=val1_reg)
        code += "\n" + self.generic_translator.put_value_to_register(condition.val2, register=val2_reg)
        code += "\n" + self.condition_translator.perform_comparison(val1_reg, val2_reg, condition.comparison)
        code = code.format(-self.generic_translator.line_count(code) + 1)
        return code

    def __for_to(self, idd: str, from_value: Value, to_value: Value, commands: list):
        from_value = self.generic_translator.reflect_on_value(from_value)
        to_value = self.generic_translator.reflect_on_value(to_value)
        delimiter_has_unknown_value = not to_value.is_int() or \
            to_value.core > self.generic_translator.KNOWN_VARIABLE_LOAD_THRESHOLD
        self.variable_table.add_iterator(idd)
        limit = self.variable_table.fetch_random_variable() if delimiter_has_unknown_value else None

        changed_identifiers = self.generic_translator.get_changed_identifiers(commands)
        self.variable_table.unset_from_list(changed_identifiers)
        commands_code = self.__generate_code(commands)
        self.variable_table.unset_from_list(changed_identifiers)

        if from_value.is_int() and to_value.is_int() and \
                to_value.core - from_value.core <= LangTranslator.LOOP_EXPANSION_THRESHOLD:
            iterator = from_value

            reg1 = self.register_machine.fetch_register()
            reg2 = self.register_machine.fetch_register()

            pre_run_code = self.generic_translator.put_value_to_register(from_value, reg1, ignore_iterator=idd)
            pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), reg2)
            pre_run_code += "\nSTORE {} {}".format(reg1, reg2)

            code = ""
            while to_value.core - iterator.core >= 0:
                code += "\n" + commands_code if code else commands_code
                code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), reg2)
                code += "\nLOAD {} {}".format(reg1, reg2)
                code += "\nINC {}".format(reg1)
                code += "\nSTORE {} {}".format(reg1, reg2)
                iterator.core += 1
        else:
            reg1 = self.register_machine.fetch_register()
            reg2 = self.register_machine.fetch_register()
            reg3 = self.register_machine.fetch_register()

            pre_run_code = self.generic_translator.put_value_to_register(from_value, reg1, ignore_iterator=idd)
            pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), reg2)
            pre_run_code += "\nSTORE {} {}".format(reg1, reg2)
            if delimiter_has_unknown_value:
                pre_run_code += "\n" + self.generic_translator.put_value_to_register(to_value, reg2,
                                                                                     ignore_iterator=idd)
                pre_run_code += "\nINC {}".format(reg2)
                pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(limit), reg3)
                pre_run_code += "\nSTORE {} {}".format(reg2, reg3)
            else:
                to_value.core += 1
                pre_run_code += "\n" + self.generic_translator.put_value_to_register(to_value, reg2)
            pre_run_code += "\nSUB {} {}".format(reg2, reg1)

            code = "JZERO {}".format(reg2) + " {}"
            code += "\n" + commands_code
            code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), reg2)
            code += "\nLOAD {} {}".format(reg1, reg2)
            code += "\nINC {}".format(reg1)
            code += "\nSTORE {} {}".format(reg1, reg2)
            if delimiter_has_unknown_value:
                code += "\n" + self.generic_translator.put_address_to_register(Identifier(limit), reg3)
                code += "\nLOAD {} {}".format(reg2, reg3)
            else:
                code += "\n" + self.generic_translator.put_value_to_register(to_value, reg2)
            code += "\nSUB {} {}".format(reg2, reg1)
            code += "\nJUMP {}".format(-self.generic_translator.line_count(code))
            code = code.format(self.generic_translator.line_count(code))

        if limit is not None:
            self.variable_table.remove_variable(limit)
        self.variable_table.remove_iterator(idd)
        return pre_run_code + "\n" + code if code else pre_run_code

    def __for_downto(self, idd: str, from_value: Value, downto_value: Value, commands: list):
        from_value = self.generic_translator.reflect_on_value(from_value)
        downto_value = self.generic_translator.reflect_on_value(downto_value)
        delimiter_has_unknown_value = not downto_value.is_int() or \
            downto_value.core > self.generic_translator.KNOWN_VARIABLE_LOAD_THRESHOLD
        self.variable_table.add_iterator(idd)
        limit = self.variable_table.fetch_random_variable() if delimiter_has_unknown_value else None

        changed_identifiers = self.generic_translator.get_changed_identifiers(commands)
        self.variable_table.unset_from_list(changed_identifiers)
        commands_code = self.__generate_code(commands)
        self.variable_table.unset_from_list(changed_identifiers)

        if from_value.is_int() and downto_value.is_int() and \
                from_value.core - downto_value.core <= LangTranslator.LOOP_EXPANSION_THRESHOLD:
            iterator = from_value

            reg1 = self.register_machine.fetch_register()
            reg2 = self.register_machine.fetch_register()

            pre_run_code = self.generic_translator.put_value_to_register(from_value, reg1, ignore_iterator=idd)
            pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), reg2)
            pre_run_code += "\nSTORE {} {}".format(reg1, reg2)

            code = ""
            while iterator.core - downto_value.core >= 0:
                code += "\n" + commands_code if code else commands_code
                code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), reg2)
                code += "\nLOAD {} {}".format(reg1, reg2)
                code += "\nDEC {}".format(reg1)
                code += "\nSTORE {} {}".format(reg1, reg2)
                iterator.core -= 1
        else:
            reg1 = self.register_machine.fetch_register()
            reg2 = self.register_machine.fetch_register()
            reg3 = self.register_machine.fetch_register()
            reg4 = self.register_machine.fetch_register()

            pre_run_code = self.generic_translator.put_value_to_register(downto_value, reg1, ignore_iterator=idd)
            if delimiter_has_unknown_value:
                pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(limit), reg3)
                pre_run_code += "\nSTORE {} {}".format(reg1, reg3)
            pre_run_code += "\n" + self.generic_translator.put_value_to_register(from_value, reg2, ignore_iterator=idd)
            pre_run_code += "\nINC {}".format(reg2)
            pre_run_code += "\n" + self.generic_translator.copy_register(source_reg=reg2, dest_reg=reg4)
            pre_run_code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), reg3)
            pre_run_code += "\nSUB {} {}".format(reg2, reg1)

            code = "JZERO {}".format(reg2) + " {}"
            code += "\nDEC {}".format(reg4)
            code += "\nSTORE {} {}".format(reg4, reg3)
            code += "\n" + commands_code
            code += "\n" + self.generic_translator.put_address_to_register(Identifier(idd), reg3)
            code += "\nLOAD {} {}".format(reg2, reg3)
            code += "\n" + self.generic_translator.copy_register(source_reg=reg2, dest_reg=reg4)
            if delimiter_has_unknown_value:
                code += "\n" + self.generic_translator.put_value_to_register(Value(Identifier(limit)), reg1)
            else:
                code += "\n" + self.generic_translator.put_value_to_register(downto_value, reg1)
            code += "\nSUB {} {}".format(reg2, reg1)
            code += "\nJUMP {}".format(-self.generic_translator.line_count(code))
            code = code.format(self.generic_translator.line_count(code))

        if limit is not None:
            self.variable_table.remove_variable(limit)
        self.variable_table.remove_iterator(idd)
        return pre_run_code + "\n" + code if code else pre_run_code

    def __read(self, idd: Identifier) -> str:
        self.variable_table.set_value(None, idd.name, idd.offset)
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
