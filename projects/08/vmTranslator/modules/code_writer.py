import re

class CodeWriter:
  def __init__(self, fileName):
    self.staticSegmentAddrPrefix =  ""
    self.fileName = fileName
    self.vmFileName = ""
    self.vmFileName = ""
    self.currentFunctionName = ""
    self.asmCodes = []
    self.segmentBaseAddresses = {
     "local": "LCL",
     "argument": "ARG",
     "this": "THIS",
     "that": "THAT",
    }
    self.neqIndex = 0
    self.ngtIndex = 0
    self.nltIndex = 0
    self.retAddrIndex = {}

  def setVMFileName(self, vmFileName):
    self.vmFileName = vmFileName
    self.staticSegmentAddrPrefix = re.sub(r".vm|\W" , "", vmFileName)

  def writePush(self, command, segment, index):
    if segment == "constant":
      self.asmCodes.append("// D = {}".format(index))
      self.asmCodes.append("@{}".format(index))
      self.asmCodes.append("D=A")

    if segment in self.segmentBaseAddresses:
      addr = self.segmentBaseAddresses[segment]
      self.asmCodes.append("// D = {}".format(index))
      self.asmCodes.append("@{}".format(index))
      self.asmCodes.append("D=A")
      self.asmCodes.append("// D = RAM[{}+{}]".format(addr, index))
      self.asmCodes.append("@{}".format(addr))
      self.asmCodes.append("A=D+M")
      self.asmCodes.append("D=M")

    if segment == "static":
      addr = "{}.{}".format(self.staticSegmentAddrPrefix, index)
      print(addr)
      self.asmCodes.append("// D = {}".format(addr))
      self.asmCodes.append("@{}".format(addr))
      self.asmCodes.append("D=M")

    if segment == "temp":
      addr = "R{}".format(int(index)+5)
      self.asmCodes.append("// D = {}".format(addr))
      self.asmCodes.append("@{}".format(addr))
      self.asmCodes.append("D=M")

    if segment == "pointer":
      if index == "0":
          addr = self.segmentBaseAddresses["this"]
      if index == "1":
          addr = self.segmentBaseAddresses["that"]
      self.asmCodes.append("// D = {}".format(addr))
      self.asmCodes.append("@{}".format(addr))
      self.asmCodes.append("D=M")

    self.asmCodes.append("// RAM[SP]=D")
    self.asmCodes.append("@SP")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// SP++")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=M+1")

  def writePop(self, command, segment, index):

    if segment == "constant":
      self.asmCodes.append("// A = {}".format(index))
      self.asmCodes.append("@{}".format(index))

    if segment in self.segmentBaseAddresses:
      addr = self.segmentBaseAddresses[segment]
      self.asmCodes.append("// D = {}".format(index))
      self.asmCodes.append("@{}".format(index))
      self.asmCodes.append("D=A")
      self.asmCodes.append("// A = RAM[{}+{}]".format(addr, index))
      self.asmCodes.append("@{}".format(addr))
      self.asmCodes.append("A=D+M")

    if segment == "static":
      addr = "{}.{}".format(self.staticSegmentAddrPrefix, index)
      self.asmCodes.append("// A = {}".format(addr))
      self.asmCodes.append("@{}".format(addr))

    if segment == "temp":
      addr = "R{}".format(int(index)+5)
      self.asmCodes.append("// A = {}".format(addr))
      self.asmCodes.append("@{}".format(addr))

    if segment == "pointer":
      if index == "0":
          addr = self.segmentBaseAddresses["this"]
      if index == "1":
          addr = self.segmentBaseAddresses["that"]
      self.asmCodes.append("// A = {}".format(addr))
      self.asmCodes.append("@{}".format(addr))
    
    self.asmCodes.append("// @R13 = A")
    self.asmCodes.append("D=A")
    self.asmCodes.append("@R13")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// SP--")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=M-1")
    self.asmCodes.append("// RAM[R13] = RAM[SP]")
    self.asmCodes.append("A=M")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@R13")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=D")

  def writePushPop(self, command, segment, index):
    self.asmCodes.append("// VM Code: {} {} {}".format(command, segment, index))
    if command == "push":
      self.writePush(command, segment, index)
    if command == "pop":
      self.writePop(command, segment, index)

  def writeArithmetic(self, command):
    self.asmCodes.append("// VM Code: {}".format(command))
    self.asmCodes.append("// D = RAM[SP--]")
    self.asmCodes.append("@SP")
    self.asmCodes.append("AM=M-1")
    self.asmCodes.append("D=M")

    if command == "add":
      self.asmCodes.append("// A=SP--; RAM[A] = D + RAM[A]")
      self.asmCodes.append("@SP")
      self.asmCodes.append("AM=M-1")
      self.asmCodes.append("D=D+M")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=D")

    if command == "sub":
      self.asmCodes.append("// A=SP--; RAM[A] = RAM[A] - D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("AM=M-1")
      self.asmCodes.append("D=M-D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=D")

    if command == "neg":
      self.asmCodes.append("// RAM[SP] = -D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=-D")

    if command == "eq":
      self.asmCodes.append("// A=SP--; RAM[A] = RAM[A] - D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("AM=M-1")
      self.asmCodes.append("D=M-D")
      self.asmCodes.append("// RAM[SP] = 0; if not D != 0, RAM[SP] = 1")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=0")
      self.asmCodes.append("@NEQ.{}".format(self.neqIndex))
      self.asmCodes.append("M=D;JNE")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=-1")
      self.asmCodes.append("(NEQ.{})".format(self.neqIndex))
      self.neqIndex += 1
      
    if command == "gt":
      self.asmCodes.append("// A=SP--; RAM[A] = RAM[A] - D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("AM=M-1")
      self.asmCodes.append("D=M-D")
      self.asmCodes.append("// RAM[SP] = 0; if not D <= 0, RAM[SP] = -1")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=0")
      self.asmCodes.append("@NGT.{}".format(self.ngtIndex))
      self.asmCodes.append("M=D;JLE")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=-1")
      self.asmCodes.append("(NGT.{})".format(self.ngtIndex))
      self.ngtIndex += 1

    if command == "lt":
      self.asmCodes.append("// A=SP--; RAM[A] = RAM[A] - D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("AM=M-1")
      self.asmCodes.append("D=M-D")
      self.asmCodes.append("// RAM[SP] = 0; if not D >= 0, RAM[SP] = -1")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=0")
      self.asmCodes.append("@NLT.{}".format(self.nltIndex))
      self.asmCodes.append("M=D;JGE")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=-1")
      self.asmCodes.append("(NLT.{})".format(self.nltIndex))
      self.nltIndex += 1

    if command == "and":
      self.asmCodes.append("// A=SP--; D = D & RAM[A]")
      self.asmCodes.append("@SP")
      self.asmCodes.append("AM=M-1")
      self.asmCodes.append("D=D&M")
      self.asmCodes.append("// RAM[SP] = D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=D")

    if command == "or":
      self.asmCodes.append("// A=SP--; D = D | RAM[A]")
      self.asmCodes.append("@SP")
      self.asmCodes.append("AM=M-1")
      self.asmCodes.append("D=D|M")
      self.asmCodes.append("// RAM[SP] = D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=D")

    if command == "not":
      self.asmCodes.append("// RAM[SP] = !D")
      self.asmCodes.append("@SP")
      self.asmCodes.append("A=M")
      self.asmCodes.append("M=!D")

    self.asmCodes.append("// SP++")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=M+1")

  def writeLabel(self, label):
    self.asmCodes.append("// VM Code: label {}".format(label))
    self.asmCodes.append("({}${})".format(self.currentFunctionName, label))

  def writeGoto(self, label):
    self.asmCodes.append("// VM Code: goto {}".format(label))
    self.asmCodes.append("@{}${}".format(self.currentFunctionName, label))
    self.asmCodes.append("0;JMP")

  def writeIf(self, label):
    self.asmCodes.append("// VM Code: if-goto {}".format(label))
    self.asmCodes.append("// D = RAM[SP--]")
    self.asmCodes.append("@SP")
    self.asmCodes.append("AM=M-1")
    self.asmCodes.append("D=M")
    self.asmCodes.append("// jump if D != 0")
    self.asmCodes.append("@{}${}".format(self.currentFunctionName, label))
    self.asmCodes.append("D;JNE")

  def bootstrap(self):
      self.asmCodes.append("// Bootstrap Code")
      self.asmCodes.append("// SP = 256")
      self.asmCodes.append("@256")
      self.asmCodes.append("D=A")
      self.asmCodes.append("@SP")
      self.asmCodes.append("M=D")
      self.asmCodes.append("// LCL = 0")
      self.asmCodes.append("D=0")
      self.asmCodes.append("@LCL")
      self.asmCodes.append("M=D")
      self.asmCodes.append("// ARG = 0")
      self.asmCodes.append("D=0")
      self.asmCodes.append("@ARG")
      self.asmCodes.append("M=D")
      self.asmCodes.append("// THIS = 0")
      self.asmCodes.append("D=0")
      self.asmCodes.append("@THIS")
      self.asmCodes.append("M=D")
      self.asmCodes.append("// THAT = 0")
      self.asmCodes.append("D=0")
      self.asmCodes.append("@THAT")
      self.asmCodes.append("M=D")

      self.currentFunctionName = "Bootstrap.init" 
      self.writeCall("Sys.init", 0)

  def writeFunction(self, functionName, nVars):
    self.currentFunctionName = functionName
    self.asmCodes.append("// VM Code: function {} {}".format(functionName, nVars))
    self.asmCodes.append("// inject an entry point label into the code")
    self.asmCodes.append("({})".format(functionName))
    self.asmCodes.append("// initialize the local segment of the callee")
    self.asmCodes.append("@LCL")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=0")
    for i in range(1, int(nVars)):
      self.asmCodes.append("@{}".format(i))
      self.asmCodes.append("D=A")
      self.asmCodes.append("@LCL")
      self.asmCodes.append("A=M")
      self.asmCodes.append("A=D+A")
      self.asmCodes.append("M=0")
    self.asmCodes.append("// Update SP = SP + nVars")
    self.asmCodes.append("@{}".format(nVars))
    self.asmCodes.append("D=A")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=D+M")

  def writeCall(self, functionName, nArgs):
    if self.currentFunctionName not in self.retAddrIndex:
      self.retAddrIndex[self.currentFunctionName] = -1
    self.retAddrIndex[self.currentFunctionName] += 1
    self.asmCodes.append("// VM Code: call {} {}".format(functionName, nArgs))
    self.asmCodes.append("// push return address to stack")
    self.asmCodes.append("@{}$ret.{}".format(self.currentFunctionName, self.retAddrIndex[self.currentFunctionName]))
    self.asmCodes.append("D=A")
    self.asmCodes.append("@SP")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=D")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=M+1")
    self.asmCodes.append("// push LCL")
    self.asmCodes.append("@LCL")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@SP")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=D")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=M+1")
    self.asmCodes.append("// push ARG")
    self.asmCodes.append("@ARG")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@SP")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=D")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=M+1")
    self.asmCodes.append("// push THIS")
    self.asmCodes.append("@THIS")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@SP")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=D")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=M+1")
    self.asmCodes.append("// push THAT")
    self.asmCodes.append("@THAT")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@SP")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=D")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=M+1")
    self.asmCodes.append("// repositions ARG, ARG = SP - 5 - nArgs")
    self.asmCodes.append("@SP")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@5")
    self.asmCodes.append("D=D-A")
    self.asmCodes.append("@{}".format(nArgs))
    self.asmCodes.append("D=D-A")
    self.asmCodes.append("@ARG")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// repositions LCL, LCL = SP")
    self.asmCodes.append("@SP")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@LCL")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// goto {}".format(functionName))
    self.asmCodes.append("@{}".format(functionName))
    self.asmCodes.append("0;JMP")
    self.asmCodes.append("// inject return address label into the code")
    self.asmCodes.append("({}$ret.{})".format(self.currentFunctionName, self.retAddrIndex[self.currentFunctionName]))

  def writeReturn(self):
    self.asmCodes.append("// VM Code: return")
    self.asmCodes.append("// R13 = LCL")
    self.asmCodes.append("@LCL")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@R13")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// R14 = RAM[R13 - 5] = return address")
    self.asmCodes.append("@5")
    self.asmCodes.append("D=A")
    self.asmCodes.append("@R13")
    self.asmCodes.append("D=M-D")
    self.asmCodes.append("A=D")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@R14")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// RAM[ARG] = RAM[SP--]")
    self.asmCodes.append("@SP")
    self.asmCodes.append("MD=M-1")
    self.asmCodes.append("A=D")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@ARG")
    self.asmCodes.append("A=M")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// SP = ARG + 1")
    self.asmCodes.append("@ARG")
    self.asmCodes.append("D=M+1")
    self.asmCodes.append("@SP")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// restores THAT = RAM[R13 - 1]")
    self.asmCodes.append("@1")
    self.asmCodes.append("D=A")
    self.asmCodes.append("@R13")
    self.asmCodes.append("A=M-D")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@THAT")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// restores THIS = RAM[R13 - 2]")
    self.asmCodes.append("@2")
    self.asmCodes.append("D=A")
    self.asmCodes.append("@R13")
    self.asmCodes.append("A=M-D")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@THIS")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// restores ARG = RAM[R13 - 3]")
    self.asmCodes.append("@3")
    self.asmCodes.append("D=A")
    self.asmCodes.append("@R13")
    self.asmCodes.append("A=M-D")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@ARG")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// restores LCL = RAM[R13 - 4]")
    self.asmCodes.append("@4")
    self.asmCodes.append("D=A")
    self.asmCodes.append("@R13")
    self.asmCodes.append("A=M-D")
    self.asmCodes.append("D=M")
    self.asmCodes.append("@LCL")
    self.asmCodes.append("M=D")
    self.asmCodes.append("// goto RAM[R14] = return address")
    self.asmCodes.append("@R14")
    self.asmCodes.append("A=M")
    self.asmCodes.append("0;JMP")

  def close(self):
    asmFile = open(self.fileName, "w")
    asmFile.write("\n".join(self.asmCodes) + "\n")
    asmFile.close()
