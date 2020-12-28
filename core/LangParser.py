from core.LangLexer import LangLexer
from sly import Parser
from model.internal.LangProgram import LangProgram
from model.nonterminals.Identifier import Identifier
from model.nonterminals.Condition import Condition
from model.nonterminals.Expression import Expression
from model.nonterminals.Value import Value
from model.commands.Assign import Assign
from model.commands.DeclareVariable import DeclareVariable
from model.commands.DeclareArray import DeclareArray
from model.commands.ForDownto import ForDownto
from model.commands.ForTo import ForTo
from model.commands.If import If
from model.commands.IfElse import IfElse
from model.commands.Read import Read
from model.commands.RepeatUntil import RepeatUntil
from model.commands.While import While
from model.commands.Write import Write


class LangParser(Parser):

    tokens = LangLexer.tokens
    literals = LangLexer.literals

    precedence = (
        ('left', "+", "-"),
        ('left', "*", "/", "%")
    )

    @_('DECLARE declarations BEGIN commands END')
    def program(self, t):
        return LangProgram(t[1], t[3])

    @_('BEGIN commands END')
    def program(self, t):
        return LangProgram([], t[1])

    def error(self, t):
        print("syntax error at line {}".format(t.lineno))
        exit(1)

    @_('declarations "," ID')
    def declarations(self, t):
        t[0].append(DeclareVariable(t[2], t.lineno))
        return t[0]

    @_('declarations "," ID "(" NUM ":" NUM ")"')
    def declarations(self, t):
        t[0].append(DeclareArray(t[2], t[4], t[6], t.lineno))
        return t[0]

    @_('ID')
    def declarations(self, t):
        return [DeclareVariable(t[0], t.lineno)]

    @_('ID "(" NUM ":" NUM ")"')
    def declarations(self, t):
        return [DeclareArray(t[0], t[2], t[4], t.lineno)]

    @_('commands command')
    def commands(self, t):
        t[0].append(t[1])
        return t[0]

    @_('command')
    def commands(self, t):
        return [t[0]]

    @_('identifier ASGN expression ";"')
    def command(self, t):
        return Assign(t[0], t[2], t.lineno)

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, t):
        return IfElse(t[1], t[3], t[5], t.lineno)

    @_('IF condition THEN commands ENDIF')
    def command(self, t):
        return If(t[1], t[3], t.lineno)

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, t):
        return While(t[1], t[3], t.lineno)

    @_('REPEAT commands UNTIL condition ";"')
    def command(self, t):
        return RepeatUntil(t[1], t[3], t.lineno)

    @_('FOR ID FROM value TO value DO commands ENDFOR')
    def command(self, t):
        return ForTo(t[1], t[3], t[5], t[7], t.lineno)

    @_('FOR ID FROM value DOWNTO value DO commands ENDFOR')
    def command(self, t):
        return ForDownto(t[1], t[3], t[5], t[7], t.lineno)

    @_('READ identifier ";"')
    def command(self, t):
        return Read(t[1], t.lineno)

    @_('WRITE value ";"')
    def command(self, t):
        return Write(t[1], t.lineno)

    @_('value')
    def expression(self, t):
        return Expression(t[0])

    @_('value "+" value',
       'value "-" value',
       'value "*" value',
       'value "/" value',
       'value "%" value')
    def expression(self, t):
        return Expression(val1=t[0], val2=t[2], operation=t[1])

    @_('value EQ value',
       'value NEQ value',
       'value LT value',
       'value GT value',
       'value LEQ value',
       'value GEQ value')
    def condition(self, t):
        return Condition(val1=t[0], val2=t[2], comparison=t[1])

    @_('NUM',
       'identifier')
    def value(self, t):
        return Value(t[0])

    @_('ID')
    def identifier(self, t):
        return Identifier(t[0])

    @_('ID "(" ID ")"',
       'ID "(" NUM ")"')
    def identifier(self, t):
        return Identifier(t[0], t[2])
