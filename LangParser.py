from LangLexer import LangLexer
from LangTranslator import LangTranslator
from sly import Parser


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
        return t[3]

    @_('BEGIN commands END')
    def program(self, t):
        return t[1]

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
        return self.lang_translator.assign_value(t[0], t[2])

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
        return self.lang_translator.read(t[1])

    @_('WRITE value ";"')
    def command(self, t):
        return self.lang_translator.write(t[1])

    @_('value')
    def expression(self, t):
        return t[0]

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
    def condition(self, t):
        pass    # todo

    @_('value NEQ value')
    def condition(self, t):
        pass    # todo

    @_('value LT value')
    def condition(self, t):
        pass    # todo

    @_('value GT value')
    def condition(self, t):
        pass    # todo

    @_('value LEQ value')
    def condition(self, t):
        pass    # todo

    @_('value GEQ value')
    def condition(self, t):
        pass    # todo

    @_('NUM')
    def value(self, t):
        return t[0]

    @_('identifier')
    def value(self, t):
        return t[0]

    @_('ID')
    def identifier(self, t):
        return t[0]

    @_('ID "(" ID ")"')
    def identifier(self, t):
        pass    # todo

    @_('ID "(" NUM ")"')
    def identifier(self, t):
        pass    # todo
