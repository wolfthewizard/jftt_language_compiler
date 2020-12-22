from core.LangLexer import LangLexer
from core.LangTranslator import LangTranslator
from sly import Parser
from model.nonterminals.Identifier import Identifier
from model.nonterminals.Condition import Condition
from model.nonterminals.Expression import Expression
from model.nonterminals.Value import Value


class LangParser(Parser):

    def __init__(self):
        self.lang_translator = LangTranslator()
        super().__init__()

    tokens = LangLexer.tokens
    literals = LangLexer.literals

    precedence = (
        ('left', "+", "-"),
        ('left', "*", "/", "%")
    )

    @_('DECLARE declarations BEGIN commands END')
    def program(self, t):
        return t[3] + "\nHALT"

    @_('BEGIN commands END')
    def program(self, t):
        return t[1] + "\nHALT"

    @_('declarations "," ID')
    def declarations(self, t):
        self.lang_translator.declare_variable(t[2])

    @_('declarations "," ID "(" NUM ":" NUM ")"')
    def declarations(self, t):
        self.lang_translator.declare_array(t[2], t[4], t[6])

    @_('ID')
    def declarations(self, t):
        self.lang_translator.declare_variable(t[0])

    @_('ID "(" NUM ":" NUM ")"')
    def declarations(self, t):
        self.lang_translator.declare_array(t[0], t[2], t[4])

    @_('commands command')
    def commands(self, t):
        return t[0] + "\n" + t[1]

    @_('command')
    def commands(self, t):
        return t[0]

    @_('identifier ASGN expression ";"')
    def command(self, t):
        return self.lang_translator.assign(t[0], t[2])

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, t):
        return self.lang_translator.if_then_else(t[1], t[3], t[5])

    @_('IF condition THEN commands ENDIF')
    def command(self, t):
        return self.lang_translator.if_then(t[1], t[3])

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, t):
        pass    # todo

    @_('REPEAT commands UNTIL condition ";"')
    def command(self, t):
        pass    # todo

    @_('FOR ID FROM value TO value DO commands ENDFOR')
    def command(self, t):
        pass    # todo

    @_('FOR ID FROM value DOWNTO value DO commands ENDFOR')
    def command(self, t):
        pass    # todo

    @_('READ identifier ";"')
    def command(self, t):
        return self.lang_translator.read(t[1])

    @_('WRITE value ";"')
    def command(self, t):
        return self.lang_translator.write(t[1])

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
