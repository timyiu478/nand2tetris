import JackTokenizer, Jacklexicon, CompilationEngine
import sys, re, os

def tokenize(file):
  tokenizer = JackTokenizer.JackTokenizer(file)
  tokenizedStr = "<tokens>\n"
  while tokenizer.hasMoreTokens():
    tokenizer.advance()
    if tokenizer.tokenType() == Jacklexicon.TokenType.keyword:
      tokenizedStr += "<keyword> {} </keyword>\n".format(re.sub(r"\s", "", tokenizer.keyword()))
    if tokenizer.tokenType() == Jacklexicon.TokenType.symbol:
      tokenizedStr += "<symbol> {} </symbol>\n".format(tokenizer.symbol())
    if tokenizer.tokenType() == Jacklexicon.TokenType.identifier:
      tokenizedStr += "<identifier> {} </identifier>\n".format(tokenizer.identifier())
    if tokenizer.tokenType() == Jacklexicon.TokenType.intConstant:
      tokenizedStr += "<integerConstant> {} </integerConstant>\n".format(tokenizer.intVal())
    if tokenizer.tokenType() == Jacklexicon.TokenType.stringConstant:
      tokenizedStr += "<stringConstant> {} </stringConstant>\n".format(tokenizer.stringVal())

  tokenizedFileName = re.match(r"(.*).jack", file).group(1) + "T.xml"
  tokenizedStr += "</tokens>\n"
  tokenizedFile = open(tokenizedFileName, "w")
  tokenizedFile.write(tokenizedStr)
  tokenizedFile.close()
  return tokenizedFileName 


if __name__ == "__main__":
  input = sys.argv[1] 
  jackFileFormat = r"^.*.jack$"
  jackFiles = []

  if re.match(jackFileFormat, input) != None: # input is .jack File
    jackFiles.append(input)
  else: # input is directory
    files = os.listdir(input)
    for f in files:
      if re.match(r".*\.jack", f) != None:
        jackFiles.append(f)
    os.chdir(input)

  for jackFile in jackFiles:
    tokenziedFileName = tokenize(jackFile)
    compEngine = CompilationEngine.CompilationEngine(tokenziedFileName)
    compEngine.compileClass()
