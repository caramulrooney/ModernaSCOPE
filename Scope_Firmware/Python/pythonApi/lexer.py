from pygments.lexer import RegexLexer
from pygments.token import *

class CustomLexer(RegexLexer):
    tokens = {
        'root': [
            (r'^[^ ]+', Generic.Heading),
            (r' ([0-9]*[.])?[0-9]+', Literal),
            (r' ([^-])([^ ])*', Literal.String),
            (r'--[^ ]+', Name.Decorator),
            (r' -[^- ]+', Name.Tag),
        ]
    }

class YesNoLexer(RegexLexer):
    tokens = {
        'root': [
            (r'Y', Name.Tag),
            (r'n', Literal.String),
            (r'.*', Literal),
        ]
    }
