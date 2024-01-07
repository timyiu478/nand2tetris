import xml.etree.ElementTree as ET
import re
import Jacklexicon
import SymbolTable
import VMWriter
from xml.dom.minidom import parse, parseString

class CompilationEngine:
  def __init__(self, file):
    self.tokens = ET.parse(file).getroot()
    self.tokenIndex = 0
    self.parseTree = None
    self.parsedFile = re.sub("T.xml", ".xml", file)
    self.className = ""
    self.keyword = ""
    self.subroutineName = ""
    self.subroutineType = ""
    self.functionType = ""
    self.classSymbolTable = SymbolTable.SymbolTable("class")
    self.subroutineSymbolTable = SymbolTable.SymbolTable("subroutine")
    self.vmWriter = VMWriter.VMWriter(re.sub("T.xml", ".vm", file))
    self.labelIndex = 0

  def processToken(self, element, parseTree, text=""): 
    token = self.tokens[0]
    if token.tag != element:
      raise Exception(f"token.tag({token.tag}) != tag({element}), {token.text}")
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
    self.vmWriter.close()

  def compileClassVarDec(self):
    # Grammer: (static|field) type varName (, varName)* ;
    token = self.tokens[0]
    if token.text == " static " or token.text == " field ":
      varKind = re.sub(r"\s", "", token.text)
      classVarDec= ET.SubElement(self.parseTree, 'classVarDec')
      self.processToken("keyword", classVarDec, token.text)
      # type
      type = self.tokens[0]
      varType = re.sub(r"\s", "", type.text)
      if type.text == " int " or type.text == " char " or type.text == " boolean ":
        self.processToken("keyword", classVarDec, type.text)
      else:
        self.processToken("identifier", classVarDec, "")
      # varName
      varName = re.sub(r"\s", "", self.tokens[0].text)
      self.classSymbolTable.define(varName, varType, varKind)
      self.processToken("identifier", classVarDec, "")
      # , varName
      while self.tokens[0].text == " , ":
          self.processToken("symbol", classVarDec, " , ")
          varName = re.sub(r"\s", "", self.tokens[0].text)
          self.classSymbolTable.define(varName, varType, varKind)
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
      self.subroutineType = re.sub(r"\s", "", token.text)
      subroutineDec= ET.SubElement(self.parseTree, 'subroutineDec')
      self.processToken("keyword", subroutineDec, token.text)
      if self.subroutineType == "method":
        self.subroutineSymbolTable.define("this", self.className, "argument")
    else:
       return False
    # (void|type)
    token = self.tokens[0]
    self.functionType = re.sub(r"\s", "", token.text)
    if token.text == " void " or token.text == " int " or token.text == " char " or token.text == " boolean ":
      self.processToken("keyword", subroutineDec, token.text)
    elif self.tokens[0].text == self.className:
      self.processToken("identifier", subroutineDec, self.className)
    self.subroutineName = re.sub(r"\s", "", self.tokens[0].text)
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
    self.subroutineSymbolTable.reset() 
    return True
     
  def compileParameterList(self, parseTree):
    parameterList = ET.SubElement(parseTree, 'parameterList')
    # type
    token = self.tokens[0]
    varType = re.sub(r"\s", "", token.text)
    if token.text == " int " or token.text == " char " or token.text == " boolean ":
      self.processToken("keyword", parameterList, token.text)
    elif token.text == " ) ":
      emptyElement = ET.SubElement(parameterList, 'emptyElement')
      return # no parameter
    else:
      self.processToken("identifier", parameterList, token.text)
    # varName
    varName = re.sub(r"\s", "", self.tokens[0].text)
    self.subroutineSymbolTable.define(varName, varType, "argument")
    self.processToken("identifier", parameterList, "")
    # , type varName
    while self.tokens[0].text == " , ":
      self.processToken("symbol", parameterList, " , ") # ,
      token = self.tokens[0]
      if token.text == " int " or token.text == " char " or token.text == " boolean ":
        varType = re.sub(r"\s", "", token.text)
        self.processToken("keyword", parameterList, token.text) # type
      elif self.tokens[0].text == self.className:
        varType = re.sub(r"\s", "", token.text)
        self.processToken("identifier", parameterList) # type
      varName = re.sub(r"\s", "", self.tokens[0].text)
      self.subroutineSymbolTable.define(varName, varType, "argument")
      self.processToken("identifier", parameterList, "") # varName
     
  def compileSubroutineBody(self, parseTree):
    subroutineBody= ET.SubElement(parseTree, 'subroutineBody')
    self.processToken("symbol", subroutineBody, " { ")
    self.compileVarDec(subroutineBody)
    className = re.sub(r"\s", "", self.className)
    self.vmWriter.writeFunction(f"{className}.{self.subroutineName}", self.subroutineSymbolTable.varCount("var"))
    if self.subroutineType == "constructor" and self.subroutineName == "new":
      self.vmWriter.writePush("constant", self.classSymbolTable.varCount("field"))
      self.vmWriter.writeCall("Memory.alloc", "1") 
      self.vmWriter.writePop("pointer", "0")
    elif self.subroutineType == "method":
      # pointer 0 to argument 0
      self.vmWriter.writePush("argument", "0")
      self.vmWriter.writePop("pointer", "0")
    self.compileStatements(subroutineBody)
    self.processToken("symbol", subroutineBody, " } ")

  def compileVarDec(self, parseTree):
    while self.tokens[0].text == " var ":
      varDec = ET.SubElement(parseTree, 'varDec')
      self.processToken("keyword", varDec, " var ")
      # type
      token = self.tokens[0]
      varType = re.sub(r"\s", "", token.text)
      if token.text == " int " or token.text == " char " or token.text == " boolean ":
        self.processToken("keyword", varDec, token.text)
      else:
        self.processToken("identifier", varDec, token.text)
      # varName
      varName = re.sub(r"\s", "", self.tokens[0].text)
      self.subroutineSymbolTable.define(varName, varType, "var")
      self.processToken("identifier", varDec, "")
      # (, varName)*
      while self.tokens[0].text == " , ":
        self.processToken("symbol", varDec, " , ") # ,
        varName = re.sub(r"\s", "", self.tokens[0].text)
        self.subroutineSymbolTable.define(varName, varType, "var")
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
    varName = re.sub(r"\s", "", self.tokens[0].text)
    self.processToken("identifier", letStatement, "")
    token = self.tokens[0]
    if token.text == " [ ":
      if varName in self.subroutineSymbolTable.symbol_table:
        segment = self.subroutineSymbolTable.kindOf(varName)
        index = self.subroutineSymbolTable.indexOf(varName)
      elif varName in self.classSymbolTable.symbol_table:
        segment = self.classSymbolTable.kindOf(varName)
        index = self.classSymbolTable.indexOf(varName)
      self.vmWriter.writePush(segment, index)
      self.processToken("symbol", letStatement, " [ ")
      self.compileExpression(letStatement)
      self.processToken("symbol", letStatement, " ] ")
      self.vmWriter.writeArithmetic("add")
    self.processToken("symbol", letStatement, " = ")
    self.compileExpression(letStatement)
    self.processToken("symbol", letStatement, " ; ")
    if self.subroutineSymbolTable.typeOf(varName) == "Array" and token.text == " [ ":
      self.vmWriter.writePop("temp", "0")
      self.vmWriter.writePop("pointer", "1")
      self.vmWriter.writePush("temp", "0")
      self.vmWriter.writePop("that", "0")
    else:
      if varName in self.subroutineSymbolTable.symbol_table:
        segment = self.subroutineSymbolTable.kindOf(varName)
        index = self.subroutineSymbolTable.indexOf(varName)
      elif varName in self.classSymbolTable.symbol_table:
        segment = self.classSymbolTable.kindOf(varName)
        index = self.classSymbolTable.indexOf(varName)
      self.vmWriter.writePop(segment, index)

  def compileIf(self, parseTree):
    self.labelIndex += 1
    labelIndex = self.labelIndex
    ifStatement= ET.SubElement(parseTree, 'ifStatement')
    self.processToken("keyword", ifStatement, " if ")
    self.processToken("symbol", ifStatement, " ( ")
    self.compileExpression(ifStatement)
    self.processToken("symbol", ifStatement, " ) ")
    self.vmWriter.writeArithmetic("not")
    self.vmWriter.writeIf(f"L_IF{labelIndex}1")
    self.processToken("symbol", ifStatement, " { ")
    self.compileStatements(ifStatement)
    self.processToken("symbol", ifStatement, " } ")
    self.vmWriter.writeGoto(f"L_IF{labelIndex}2")
    self.vmWriter.writeLabel(f"L_IF{labelIndex}1")
    if self.tokens[0].text == " else ":
      self.processToken("keyword", ifStatement, " else ")
      self.processToken("symbol", ifStatement, " { ")
      self.compileStatements(ifStatement)
      self.processToken("symbol", ifStatement, " } ")
    self.vmWriter.writeLabel(f"L_IF{labelIndex}2")
      
  def compileWhile(self, parseTree):
    self.labelIndex += 1
    labelIndex = self.labelIndex
    whileStatement= ET.SubElement(parseTree, 'whileStatement')
    self.processToken("keyword", whileStatement, " while ")
    self.processToken("symbol", whileStatement, " ( ")
    self.vmWriter.writeLabel(f"L_WHILE{labelIndex}1")
    self.compileExpression(whileStatement)
    self.vmWriter.writeArithmetic("not")
    self.vmWriter.writeIf(f"L_WHILE{labelIndex}2")
    self.processToken("symbol", whileStatement, " ) ")
    self.processToken("symbol", whileStatement, " { ")
    self.compileStatements(whileStatement)
    self.processToken("symbol", whileStatement, " } ")
    self.vmWriter.writeGoto(f"L_WHILE{labelIndex}1")
    self.vmWriter.writeLabel(f"L_WHILE{labelIndex}2")

  def compileDo(self, parseTree):
    doStatement= ET.SubElement(parseTree, 'doStatement')
    self.processToken("keyword", doStatement, " do ")
    name = re.sub(r"\s", "", self.tokens[0].text)
    self.processToken("identifier", doStatement)
    token = self.tokens[0]
    if token.text == " ( ":
      self.vmWriter.writePush("pointer", "0")
      self.processToken("symbol", doStatement, " ( ")
      nArgs = self.compileExpressionList(doStatement)
      self.processToken("symbol", doStatement, " ) ")
      className = re.sub(r"\s", "", self.className)
      self.vmWriter.writeCall(f"{className}.{name}", nArgs+1)
    elif token.text == " . ":
      if name in self.subroutineSymbolTable.symbol_table:
        segment = self.subroutineSymbolTable.kindOf(name)
        index = self.subroutineSymbolTable.indexOf(name)
        self.vmWriter.writePush(segment, index)
      elif name in self.classSymbolTable.symbol_table:
        segment = self.classSymbolTable.kindOf(name)
        index = self.classSymbolTable.indexOf(name)
        self.vmWriter.writePush(segment, index)
      self.processToken("symbol", doStatement, " . ")
      subrountineName = re.sub(r"\s", "", self.tokens[0].text) 
      self.processToken("identifier", doStatement)
      self.processToken("symbol", doStatement, " ( ")
      nArgs = self.compileExpressionList(doStatement)
      self.processToken("symbol", doStatement, " ) ")
      if name in self.subroutineSymbolTable.symbol_table:
        type = self.subroutineSymbolTable.typeOf(name)
        self.vmWriter.writeCall(f"{type}.{subrountineName}", nArgs+1)
      elif name in self.classSymbolTable.symbol_table:
        type = self.classSymbolTable.typeOf(name)
        self.vmWriter.writeCall(f"{type}.{subrountineName}", nArgs+1)
      else:
        self.vmWriter.writeCall(f"{name}.{subrountineName}", nArgs)
    self.processToken("symbol", doStatement, " ; ")
    # gets rid of the return value
    self.vmWriter.writePop("temp", 0)

  def compileReturn(self, parseTree):
    r = ET.SubElement(parseTree, 'returnStatement')
    self.processToken("keyword", r, " return ")
    if self.tokens[0].text != " ; ":
      self.compileExpression(r)
    self.processToken("symbol", r, " ; ")
    if self.functionType == "void":
      self.vmWriter.writePush("constant", "0")
    self.vmWriter.writeReturn();

  def compileExpression(self, parseTree):
    # Grammer: term (op term)*
    term = self.tokens[0]
    if re.match(r"(integerConstant|stringConstant|keyword|identifier)", term.tag) or \
       re.match(r" (\-|\~|\() ", term.text):
      expression = ET.SubElement(parseTree, 'expression')
      self.compileTerm(expression)
      while re.match(r" (\+|\-|\*|\/|\&|\||\<|\>|\=) ", self.tokens[0].text) != None:
        opCode = re.sub(r"\s", "", self.tokens[0].text)
        self.processToken("symbol", expression)
        self.compileTerm(expression)
        if opCode == "+":
          self.vmWriter.writeArithmetic("add")
        if opCode == "-":
          self.vmWriter.writeArithmetic("sub")
        if opCode == "*":
          self.vmWriter.writeCall("Math.multiply", "2")
        if opCode == "/":
          self.vmWriter.writeCall("Math.divide", "2")
        if opCode == ">":
          self.vmWriter.writeArithmetic("gt")
        if opCode == "<":
          self.vmWriter.writeArithmetic("lt")
        if opCode == "&":
          self.vmWriter.writeArithmetic("and")
        if opCode == "|":
          self.vmWriter.writeArithmetic("or")
        if opCode == "=":
          self.vmWriter.writeArithmetic("eq")
      return 1
    return 0

  def compileTerm(self, parseTree): 
    term = ET.SubElement(parseTree, 'term')
    token = self.tokens[0]
    varName = re.sub(r"\s", "", token.text)
    if token.tag == "integerConstant":
      self.processToken("integerConstant", term)
      self.vmWriter.writePush("constant", varName)
    elif token.tag == "stringConstant":
      self.processToken("stringConstant", term)
      string = token.text[1:-1]
      self.vmWriter.writePush("constant", len(string))
      self.vmWriter.writeCall("String.new", "1")
      for char in string:
        self.vmWriter.writePush("constant", ord(char))
        self.vmWriter.writeCall("String.appendChar", "2")
    elif token.tag == "keyword":
      if token.text == " true ":
        self.vmWriter.writePush("constant", "0")
        self.vmWriter.writeArithmetic("not")
      elif re.match(r" (false|null) ", token.text) != None :
        self.vmWriter.writePush("constant", "0")
      elif token.text == " this ":
        self.vmWriter.writePush("pointer", "0")
      self.processToken("keyword", term)
    elif token.tag == "identifier":
      segment, index = "", ""
      if varName in self.subroutineSymbolTable.symbol_table:
        segment = self.subroutineSymbolTable.kindOf(varName)
        index = self.subroutineSymbolTable.indexOf(varName)
        self.vmWriter.writePush(segment, index)
      elif varName in self.classSymbolTable.symbol_table:
        segment = self.classSymbolTable.kindOf(varName)
        index = self.classSymbolTable.indexOf(varName)
        self.vmWriter.writePush(segment, index)
      self.processToken("identifier", term)
      token = self.tokens[0]
      if token.text == " [ ":
        self.processToken("symbol", term, " [ ")
        self.compileExpression(term)
        self.processToken("symbol", term, " ] ")
        self.vmWriter.writeArithmetic("add")
        self.vmWriter.writePop("pointer", "1")
        self.vmWriter.writePush("that", "0")
      elif token.text == " ( ":
        self.processToken("symbol", term, " ( ")
        nArgs = self.compileExpressionList(term)
        self.processToken("symbol", term, " ) ")
      elif token.text == " . ":
        self.processToken("symbol", term, " . ")
        functionName = re.sub(r"\s", "", self.tokens[0].text)
        self.processToken("identifier", term)
        self.processToken("symbol", term, " ( ")
        nArgs = self.compileExpressionList(term)
        self.processToken("symbol", term, " ) ")
        if varName in self.subroutineSymbolTable.symbol_table:
          type = self.subroutineSymbolTable.typeOf(varName)
          self.vmWriter.writeCall(f"{type}.{functionName}", nArgs+1)
        elif varName in self.classSymbolTable.symbol_table:
          type = self.classSymbolTable.typeOf(varName)
          self.vmWriter.writeCall(f"{type}.{functionName}", nArgs+1)
        else:
          self.vmWriter.writeCall(f"{varName}.{functionName}", nArgs)
    elif token.text == " - " or token.text == " ~ ":
      self.processToken("symbol", term)
      self.compileTerm(term)
      if token.text == " - ":
        self.vmWriter.writeArithmetic("neg")
      if token.text == " ~ ":
        self.vmWriter.writeArithmetic("not")
    elif token.text == " ( ":
      self.processToken("symbol", term, " ( ")
      self.compileExpression(term)
      self.processToken("symbol", term, " ) ")

  def compileExpressionList(self, parseTree):
    expressionList = ET.SubElement(parseTree, 'expressionList')
    emptyElement = ET.SubElement(expressionList, 'emptyElement')
    nArgs = self.compileExpression(expressionList)
    while self.tokens[0].text == " , ":
      self.processToken("symbol", expressionList, " , ")
      nArgs += self.compileExpression(expressionList)
    return nArgs
