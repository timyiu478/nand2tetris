from modules import parser, code_writer, command_type
import re
import sys

commandType = command_type.CommandType

class VMTranslator:

  def __init__(self, vmFileName):
    self.parser = parser.Parser(vmFileName)
    asmFileName = re.sub("vm", "asm", vmFileName)
    self.codeWriter = code_writer.CodeWriter(asmFileName)

  def translate(self):
    while self.parser.hasMoreLines():
      self.parser.advance()
      arg1 = self.parser.arg1()

    if self.parser.commandType() == commandType.C_ARITHMETIC:
        self.codeWriter.writeArithmetic(arg1)

    if self.parser.commandType() == commandType.C_PUSH:
        arg2 = self.parser.arg2()
        self.codeWriter.writePushPop("push", arg1, arg2)

    if self.parser.commandType() == commandType.C_POP:
        arg2 = self.parser.arg2()
        self.codeWriter.writePushPop("pop", arg1, arg2)

    self.codeWriter.close()

if __name__ == "__main__":
  vmTranslator = VMTranslator(sys.argv[1])    
  vmTranslator.translate()
