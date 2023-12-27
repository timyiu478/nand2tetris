import re

class CodeWriter:
  def __init__(self, fileName):
    self.staticSegmentAddrPrefix = re.sub(r".asm|\W" , "", fileName)
    self.fileName = fileName
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
      self.asmCodes.append("// RAM[SP] = 0; if not D <= 0, RAM[SP] = 1")
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
      self.asmCodes.append("// RAM[SP] = 0; if not D >= 0, RAM[SP] = 1")
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

  def close(self):
    asmFile = open(self.fileName, "w")
    asmFile.write("\n".join(self.asmCodes) + "\n")
    asmFile.close()
