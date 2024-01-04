from enum import Enum

class TokenType(Enum):
  keyword = 0
  symbol = 1
  intConstant = 2
  stringConstant = 3
  identifier = 4

keyword = r"class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return"
symbol = r"\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|\-|\*|\/|\&|\||\<|\>|\=|\~"
intConstant = r"\d+"
stringConstant = r'"[^\"\n]*"'
identifier = r"[a-zA-Z_][0-9a-zA-Z_]*"
token = r"^{}|{}|{}|{}|{}".format(keyword, symbol, intConstant, stringConstant, identifier)


