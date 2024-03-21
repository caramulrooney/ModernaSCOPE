from pygments.lexer import RegexLexer
from pygments.token import *

from pygments.style import Style
from pygments.token import Token

class CliStyle(Style):
    styles = {
        Token.Command:  'bold #CC0000',
        Token.Number: '#00CC88',
        Token.ElectrodeRange.Range: '#FFCC00',
        Token.ElectrodeRange.SelectionType: 'italic ansibrightyellow',
        Token.ShortFlag:'bold #00FF00',
        Token.LongFlag: 'italic #005500',
    }

class YesNoStyle(Style):
    styles = {
        Token.YesNo.Yes: 'bold #00CC88',
        Token.YesNo.No: 'bold #CC0000',
        Token.Invalid: '#888888',
    }

class CliLexer(RegexLexer):
    tokens = {
        'root': [
            (r'^[^ ]+', Token.Command),
            (r',', Token.ElectrodeRange.SelectionType),
            (r'(?<= )[0-9.]+(?=( ?))', Token.Number),
            (r'[a-hA-H]1?[0-9](-[a-hA-H]1?[0-9])?', Token.ElectrodeRange.Range),
            (r'((?<=[, ])[rceRCE].*?:)|(:[rceRCE][^, ]*)', Token.ElectrodeRange.SelectionType),
            (r'--[^ ]+', Token.LongFlag),
            (r'(?<= )-[^- ]+', Token.ShortFlag),
        ]
    }

class YesNoLexer(RegexLexer):
    tokens = {
        'root': [
            (r'[^yYnN].*', Token.Invalid),
            (r'[yY]', Token.YesNo.Yes),
            (r'[nN]', Token.YesNo.No),
        ]
    }
