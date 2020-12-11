from LangLexer import LangLexer
from sly import Parser


class LangParser(Parser):

    tokens = LangLexer.tokens
    literals = LangLexer.literals

    precedence = (
        ('left', "+", "-"),
        ('left', "*", "/", "%")
    )

    @_('DECLARE declarations BEGIN commands END')
    def program(self, t):
        return t[1] + t[2]

    @_('BEGIN commands END')
    def program(self, t):
        return t[1]

    @_('declarations "," ID')
    def declarations(self, t):
        pass    # todo

    @_('declarations "," ID "(" NUM ":" NUM ")"')
    def declarations(self, t):
        pass    # todo

    @_('ID')
    def declarations(self, t):
        pass    # todo

    @_('ID "(" NUM ":" NUM ")"')
    def declarations(self, t):
        pass    # todo

    @_('commands command')
    def commands(self, t):
        pass    # todo

    @_('command')
    def commands(self, t):
        pass    # todo

    @_('identifier ASGN expression ";"')
    def command(self, t):
        pass    # todo

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, t):
        pass    # todo

    @_('IF condition THEN commands ENDIF')
    def command(self, t):
        pass    # todo

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
        pass    # todo

    @_('WRITE value ";"')
    def command(self, t):
        pass    # todo

    @_('value')
    def expression(self, t):
        pass    # todo

    @_('value "+" value')
    def expression(self, t):
        pass    # todo

    @_('value "-" value')
    def expression(self, t):
        pass    # todo

    @_('value "*" value')
    def expression(self, t):
        pass    # todo

    @_('value "/" value')
    def expression(self, t):
        pass    # todo

    @_('value "%" value')
    def expression(self, t):
        pass    # todo

    @_('value EQ value')
    def condtition(self, t):
        pass    # todo

    @_('value NEQ value')
    def condtition(self, t):
        pass    # todo

    @_('value LT value')
    def condtition(self, t):
        pass    # todo

    @_('value GT value')
    def condtition(self, t):
        pass    # todo

    @_('value LEQ value')
    def condtition(self, t):
        pass    # todo

    @_('value GEQ value')
    def condtition(self, t):
        pass    # todo

    @_('NUM')
    def value(self, t):
        pass    # todo

    @_('identifier')
    def value(self, t):
        pass    # todo

    @_('ID')
    def identifier(self, t):
        pass    # todo

    @_('ID "(" ID ")"')
    def identifier(self, t):
        pass    # todo

    @_('ID "(" NUM ")"')
    def identifier(self, t):
        pass    # todo
