import Jacklexicon
import re

class JackTokenizer:
  def __init__(self, file):
    jackFile = open(file, "r")
    jackFileWithoutComment = re.sub(r"\/\/.*|\/\*\*(.|\n)+?\*\/", "", jackFile.read())
    self.tokens = re.findall(Jacklexicon.token, jackFileWithoutComment)
    self.tokenIndex = -1
    self.currentToken = ""

  def hasMoreTokens(self):
    if self.tokenIndex < len(self.tokens) - 1:
      return True

  def advance(self):
   self.tokenIndex += 1
   self.currentToken = self.tokens[self.tokenIndex]

  def tokenType(self):
    if re.match(Jacklexicon.keyword, self.currentToken) != None:
      return Jacklexicon.TokenType.keyword
    if re.match(Jacklexicon.symbol, self.currentToken) != None:
      return Jacklexicon.TokenType.symbol
    if re.match(Jacklexicon.intConstant, self.currentToken) != None:
      return Jacklexicon.TokenType.intConstant
    if re.match(Jacklexicon.stringConstant, self.currentToken) != None:
      return Jacklexicon.TokenType.stringConstant
    if re.match(Jacklexicon.identifier, self.currentToken) != None:
      return Jacklexicon.TokenType.identifier

  def keyword(self):
    return self.currentToken
  def symbol(self):
    if self.currentToken == "<":
      return "&lt;"
    if self.currentToken == ">":
      return "&gt;"
    if self.currentToken == '"':
      return "&quot;"
    if self.currentToken == '&':
      return "&amp;"
    return self.currentToken
  def identifier(self):
    return self.currentToken
  def intVal(self):
    return self.currentToken
  def stringVal(self):
    return re.sub('"',"", self.currentToken)
