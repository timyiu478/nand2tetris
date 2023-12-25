from lib import parser, code, instruction_type, symbol_table
import sys
import re

InstructionType = instruction_type.InstructionType

def decimalToBinary(n):
  binary = bin(int(n)).replace("0b", "")
  while len(binary) < 16:
    binary = "0" + binary
  return binary

class HackAssembler:

  def __init__(self, file):
    self.file = file
    self.freeMemoryAddress = 16
    self.symbolTable = symbol_table.SymbolTable()
    self.code = code.Code()
  
  def addLabelsToSymbolTable(self):
    p = parser.Parser(self.file)
    instructionAddress = -1 
    while p.hasMoreLines():
      p.advance()
      instructionAddress += 1
      if p.instructionType() != InstructionType.L_INSTRUCTION:
        continue
      self.symbolTable.addEntry(p.symbol(), instructionAddress)
      instructionAddress -= 1

  def toMachineCode(self):
    p = parser.Parser(self.file)
    hackFileStr = ""
    while p.hasMoreLines():
      p.advance()
      if p.instructionType() == InstructionType.A_INSTRUCTION:
        if re.match("^\\d+$", p.symbol()) == None:
          if self.symbolTable.contains(p.symbol()) == False:
            self.symbolTable.addEntry(p.symbol(), self.freeMemoryAddress)
            self.freeMemoryAddress += 1
          hackFileStr += decimalToBinary(self.symbolTable.getAddress(p.symbol()))
        else:
          hackFileStr += decimalToBinary(p.symbol())
      if p.instructionType() == InstructionType.C_INSTRUCTION:
        hackFileStr += "111"
        hackFileStr += self.code.comp(p.comp())
        if p.dest() == "null":
          hackFileStr += self.code.dest(p.dest())
        else:
          hackFileStr += self.code.dest(''.join(sorted(p.dest())))
        hackFileStr += self.code.jump(p.jump())
      if p.instructionType() != InstructionType.L_INSTRUCTION:
        hackFileStr += "\n"
    hackFile = open(re.sub(".asm", ".hack", self.file), "w")
    hackFile.write(hackFileStr)
    hackFile.close()

if __name__ == "__main__":
  file = sys.argv[1]
  hackAssembler = HackAssembler(file)
  hackAssembler.addLabelsToSymbolTable()
  hackAssembler.toMachineCode()
