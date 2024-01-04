import xml.etree.ElementTree as ET
import re
import Jacklexicon
from xml.dom.minidom import parse, parseString

class CompilationEngine:
  def __init__(self, file):
    self.tokens = ET.parse(file).getroot()
    self.tokenIndex = 0
    self.parseTree = None
    self.parsedFile = re.sub("T.xml", ".xml", file)
    self.className = ""

  def processToken(self, element, parseTree, text=""): 
    token = self.tokens[0]
    if token.tag != element:
      raise Exception(f"token.tag({token.tag}) != tag({element})")
    if text == "" or token.text == text:
      subElement = ET.SubElement(parseTree, element)
      subElement.text = token.text
      self.tokens.remove(token)
    else:
      raise Exception(f"token.text({token.text} != text({text})")

  def compileClass(self):
    # Grammer: class identifier { classVarDec* subroutineDec* }
    self.parseTree = ET.Element("class")
    self.processToken("keyword", self.parseTree, " class ")
    self.className = self.tokens[0].text
    self.processToken("identifier", self.parseTree, "")
    self.processToken("symbol", self.parseTree, " { ")
    while self.compileClassVarDec():
      pass
    while self.compileSubroutine():
      pass
    self.processToken("symbol", self.parseTree, " } ")
    file = open(self.parsedFile, "w")
    xmlStr = ET.tostring(self.parseTree, short_empty_elements=False)
    dom = parseString(xmlStr)
    dom = dom.toprettyxml(indent="  ")
    f = re.sub(r"\n.*\<emptyElement\/\>.*", "", dom)
    f = re.sub(r"\<\?xml.*\n", "", f)
    file.write(f)
    file.close()

  def compileClassVarDec(self):
    # Grammer: (static|field) type varName (, varName)* ;
    token = self.tokens[0]
    if token.text == " static " or token.text == " field ":
      classVarDec= ET.SubElement(self.parseTree, 'classVarDec')
      self.processToken("keyword", classVarDec, token.text)
      # type
      type = self.tokens[0]
      if type.text == " int " or type.text == " char " or type.text == " boolean ":
        self.processToken("keyword", classVarDec, type.text)
      else:
        self.processToken("identifier", classVarDec, "")
      # varName
      self.processToken("identifier", classVarDec, "")
      # , varName
      while self.tokens[0].text == " , ":
          self.processToken("symbol", classVarDec, " , ")
          self.processToken("identifier", classVarDec, "")
      # ;
      self.processToken("symbol", classVarDec, " ; ")
      return True;
    else:
      return False;
     
  def compileSubroutine(self):
    # Grammer: (constructor|function|method) (void|type) subroutineName ( parameterlist ) subroutineBody
    # (constructor|function|method)
    token = self.tokens[0]
    if token.text == " constructor " or token.text == " function " or token.text == " method ":
      subroutineDec= ET.SubElement(self.parseTree, 'subroutineDec')
      self.processToken("keyword", subroutineDec, token.text)
    else:
       return False
    # (void|type)
    token = self.tokens[0]
    if token.text == " void " or token.text == " int " or token.text == " char " or token.text == " boolean ":
      self.processToken("keyword", subroutineDec, token.text)
    elif self.tokens[0].text == self.className:
      self.processToken("identifier", subroutineDec, self.className)
    # subroutineName
    self.processToken("identifier", subroutineDec)
    # symbol
    self.processToken("symbol", subroutineDec, " ( ")
    # parameterList
    self.compileParameterList(subroutineDec)
    # symbol
    self.processToken("symbol", subroutineDec, " ) ")
    # subroutine body
    self.compileSubroutineBody(subroutineDec)
    return True
     
  def compileParameterList(self, parseTree):
    parameterList = ET.SubElement(parseTree, 'parameterList')
    # type
    token = self.tokens[0]
    if token.text == " int " or token.text == " char " or token.text == " boolean ":
      self.processToken("keyword", parameterList, token.text)
    elif self.tokens[0].text == self.className:
      self.processToken("identifier", parameterList, token.text)
    else:
      emptyElement = ET.SubElement(parameterList, 'emptyElement')
      return # no parameter
    # varName
    self.processToken("identifier", parameterList, "")
    # , type varName
    while self.tokens[0].text == " , ":
      self.processToken("symbol", parameterList, " , ") # ,
      token = self.tokens[0]
      if token.text == " int " or token.text == " char " or token.text == " boolean ":
        self.processToken("keyword", parameterList, token.text) # type
      elif self.tokens[0].text == self.className:
        self.processToken("identifier", parameterList) # type
      self.processToken("identifier", parameterList, "") # varName
     
  def compileSubroutineBody(self, parseTree):
    subroutineBody= ET.SubElement(parseTree, 'subroutineBody')
    self.processToken("symbol", subroutineBody, " { ")
    self.compileVarDec(subroutineBody)
    self.compileStatements(subroutineBody)
    self.processToken("symbol", subroutineBody, " } ")

  def compileVarDec(self, parseTree):
    while self.tokens[0].text == " var ":
      varDec = ET.SubElement(parseTree, 'varDec')
      self.processToken("keyword", varDec, " var ")
      # type
      token = self.tokens[0]
      if token.text == " int " or token.text == " char " or token.text == " boolean ":
        self.processToken("keyword", varDec, token.text)
      else:
        self.processToken("identifier", varDec, token.text)
      # varName
      self.processToken("identifier", varDec, "")
      # (, varName)*
      while self.tokens[0].text == " , ":
        self.processToken("symbol", varDec, " , ") # ,
        self.processToken("identifier", varDec, "") # varName
      self.processToken("symbol", varDec, " ; ")

  def compileStatements(self, parseTree):
    statements = ET.SubElement(parseTree, 'statements')
    while True:
      token = self.tokens[0]
      if token.text == " let ":
        self.compileLet(statements)
        continue
      if token.text == " if ":
        self.compileIf(statements)
        continue
      if token.text == " while ":
        self.compileWhile(statements)
        continue
      if token.text == " do ":
        self.compileDo(statements)
        continue
      if token.text == " return ":
        self.compileReturn(statements)
        continue
      break

  def compileLet(self, parseTree):
    letStatement= ET.SubElement(parseTree, 'letStatement')
    self.processToken("keyword", letStatement, " let ")
    self.processToken("identifier", letStatement, "")
    if self.tokens[0].text == " [ ":
      self.processToken("symbol", letStatement, " [ ")
      self.compileExpression(letStatement)
      self.processToken("symbol", letStatement, " ] ")
    self.processToken("symbol", letStatement, " = ")
    self.compileExpression(letStatement)
    self.processToken("symbol", letStatement, " ; ")

  def compileIf(self, parseTree):
    ifStatement= ET.SubElement(parseTree, 'ifStatement')
    self.processToken("keyword", ifStatement, " if ")
    self.processToken("symbol", ifStatement, " ( ")
    self.compileExpression(ifStatement)
    self.processToken("symbol", ifStatement, " ) ")
    self.processToken("symbol", ifStatement, " { ")
    self.compileStatements(ifStatement)
    self.processToken("symbol", ifStatement, " } ")
    if self.tokens[0].text == " else ":
      self.processToken("keyword", ifStatement, " else ")
      self.processToken("symbol", ifStatement, " { ")
      self.compileStatements(ifStatement)
      self.processToken("symbol", ifStatement, " } ")
      
  def compileWhile(self, parseTree):
    whileStatement= ET.SubElement(parseTree, 'whileStatement')
    self.processToken("keyword", whileStatement, " while ")
    self.processToken("symbol", whileStatement, " ( ")
    self.compileExpression(whileStatement)
    self.processToken("symbol", whileStatement, " ) ")
    self.processToken("symbol", whileStatement, " { ")
    self.compileStatements(whileStatement)
    self.processToken("symbol", whileStatement, " } ")
  def compileDo(self, parseTree):
    doStatement= ET.SubElement(parseTree, 'doStatement')
    self.processToken("keyword", doStatement, " do ")
    self.processToken("identifier", doStatement)
    token = self.tokens[0]
    if token.text == " ( ":
      self.processToken("symbol", doStatement, " ( ")
      self.compileExpressionList(doStatement)
      self.processToken("symbol", doStatement, " ) ")
    elif token.text == " . ":
      self.processToken("symbol", doStatement, " . ")
      self.processToken("identifier", doStatement)
      self.processToken("symbol", doStatement, " ( ")
      self.compileExpressionList(doStatement)
      self.processToken("symbol", doStatement, " ) ")
    self.processToken("symbol", doStatement, " ; ")

  def compileReturn(self, parseTree):
    r = ET.SubElement(parseTree, 'returnStatement')
    self.processToken("keyword", r, " return ")
    if self.tokens[0].text != " ; ":
      self.compileExpression(r)
    self.processToken("symbol", r, " ; ")

  def compileExpression(self, parseTree):
    # Grammer: term (op term)*
    term = self.tokens[0]
    if re.match(r"(integerConstant|stringConstant|keyword|identifier)", term.tag) or \
       re.match(r" (\-|\~|\() ", term.text):
      expression = ET.SubElement(parseTree, 'expression')
      self.compileTerm(expression)
      while re.match(r" (\+|\-|\*|\/|\&|\||\<|\>|\=) ", self.tokens[0].text) != None:
        self.processToken("symbol", expression)
        self.compileTerm(expression)

  def compileTerm(self, parseTree): 
    term = ET.SubElement(parseTree, 'term')
    token = self.tokens[0]
    if token.tag == "integerConstant":
      self.processToken("integerConstant", term)
    elif token.tag == "stringConstant":
      self.processToken("stringConstant", term)
    elif token.tag == "keyword":
      self.processToken("keyword", term)
    elif token.tag == "identifier":
      self.processToken("identifier", term)
      token = self.tokens[0]
      if token.text == " [ ":
        self.processToken("symbol", term, " [ ")
        self.compileExpression(term)
        self.processToken("symbol", term, " ] ")
      elif token.text == " ( ":
        self.processToken("symbol", term, " ( ")
        self.compileExpressionList(term)
        self.processToken("symbol", term, " ) ")
      elif token.text == " . ":
        self.processToken("symbol", term, " . ")
        self.processToken("identifier", term)
        self.processToken("symbol", term, " ( ")
        self.compileExpressionList(term)
        self.processToken("symbol", term, " ) ")
    elif token.text == " - " or token.text == " ~ ":
      self.processToken("symbol", term)
      self.compileTerm(term)
    elif token.text == " ( ":
      self.processToken("symbol", term, " ( ")
      self.compileExpression(term)
      self.processToken("symbol", term, " ) ")

  def compileExpressionList(self, parseTree):
    expressionList = ET.SubElement(parseTree, 'expressionList')
    emptyElement = ET.SubElement(expressionList, 'emptyElement')
    self.compileExpression(expressionList)
    while self.tokens[0].text == " , ":
      self.processToken("symbol", expressionList, " , ")
      self.compileExpression(expressionList)
