from modules import instruction_type
import re

InstructionType = instruction_type.InstructionType

class Parser:
  def __init__(self, file):
    self.instructionIndex = -1
    self.instructions=[]

    file = open(file, "r")
    fileLines = file.readlines()
    file.close()
    for line in fileLines:
      instruction=re.sub("//.*| |\\n","", line) 
      if len(instruction) > 0:
        self.instructions.append(instruction)

  def hasMoreLines(self):
    return self.instructionIndex+1 < len(self.instructions)

  def advance(self):
    self.instructionIndex += 1
    return self.instructions[self.instructionIndex]

  def instructionType(self):
    if self.instructions[self.instructionIndex][0] == "@":
      return InstructionType.A_INSTRUCTION 
    elif self.instructions[self.instructionIndex][0] == "(":
      return InstructionType.L_INSTRUCTION 
    else:
      return InstructionType.C_INSTRUCTION 
      

  def symbol(self):
    if self.instructionType() == InstructionType.A_INSTRUCTION:
      return self.instructions[self.instructionIndex][1:] 
    if self.instructionType() == InstructionType.L_INSTRUCTION:
      return self.instructions[self.instructionIndex][1:-1] 

  def dest(self):
    if self.instructionType() == InstructionType.C_INSTRUCTION:
      if re.search("=", self.instructions[self.instructionIndex]):
        return re.sub("=.*", "", self.instructions[self.instructionIndex])
      else:
        return "null"

  def comp(self):
    if self.instructionType() == InstructionType.C_INSTRUCTION:
      return re.sub(".*=|;.*", "", self.instructions[self.instructionIndex])

  def jump(self):
    if self.instructionType() == InstructionType.C_INSTRUCTION:
      if re.search(".*;.*", self.instructions[self.instructionIndex]) == None:
        return "null"
      else:
        return re.sub(".*;", "", self.instructions[self.instructionIndex])
