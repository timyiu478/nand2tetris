import parser, code_writer, command_type
import os
import re
import sys
import glob

commandType = command_type.CommandType

class VMTranslator:

  def __init__(self, asmFileName):
    self.parser = None
    self.codeWriter = code_writer.CodeWriter(asmFileName)

  def setVMFileName(self, vmFileName):
    self.parser = parser.Parser(vmFileName)
    self.codeWriter.setVMFileName(vmFileName)

  def bootstrap(self):
    self.codeWriter.bootstrap()

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
  
      if self.parser.commandType() == commandType.C_LABEL:
        self.codeWriter.writeLabel(arg1)

      if self.parser.commandType() == commandType.C_GOTO:
        self.codeWriter.writeGoto(arg1)

      if self.parser.commandType() == commandType.C_IF:
        self.codeWriter.writeIf(arg1)

      if self.parser.commandType() == commandType.C_FUNCTION:
        arg2 = self.parser.arg2()
        self.codeWriter.writeFunction(arg1, arg2)

      if self.parser.commandType() == commandType.C_RETURN:
        self.codeWriter.writeReturn()

      if self.parser.commandType() == commandType.C_CALL:
        arg2 = self.parser.arg2()
        self.codeWriter.writeCall(arg1, arg2)
      
  def close(self):
    self.codeWriter.close()

if __name__ == "__main__":
  argv1 = sys.argv[1]
  asmFileName = ""
  vmTranslator = None    

  if ".vm" in argv1:
    asmFileName = re.sub(".vm", ".asm", argv1)
    vmTranslator = VMTranslator(asmFileName)
    vmTranslator.setVMFileName(argv1)
    vmTranslator.translate()
  else:
    asmDirectory = re.sub(r"\W", "", argv1) 
    os.chdir(asmDirectory)
    asmFileName = asmDirectory + ".asm"
    vmTranslator = VMTranslator(asmFileName)
    vmFiles = glob.glob("*.vm")
    sysVM = "Sys.vm"
    if sysVM in vmFiles:
      vmTranslator.bootstrap()
    for vmFile in vmFiles:
      vmTranslator.setVMFileName(vmFile)
      vmTranslator.translate()

  vmTranslator.close()
