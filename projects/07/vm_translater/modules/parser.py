from modules import command_type
import re

commandType = command_type.CommandType

class Parser:

  def __init__(self, file):
    self.commandIndex = -1
    self.commands = []
    self.arithmeticOrLogicalCommands = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
    self.memorySegments = {"local", "argument", "static", "constant", "this", "that", "pointer", "temp"}
    self.pushCommandSyntax = "^push ({segments}) [0-9]+$".format(segments='|'.join(self.memorySegments))
    self.popCommandSyntax = "^pop ({segments}) [0-9]+$".format(segments='|'.join(self.memorySegments))
    self.currentCommand = ""

    file = open(file, "r")
    fileLines = file.readlines()
    file.close()
    for line in fileLines: 
      command=re.sub("//.*|^(\\s)*$|\\n","", line) 
      if len(command) > 0:
        self.commands.append(command)

  def hasMoreLines(self):
    return self.commandIndex+1 < len(self.commands)

  def advance(self):
    self.commandIndex += 1
    self.currentCommand = self.commands[self.commandIndex]
    return self.currentCommand

  def commandType(self):
    if self.currentCommand in self.arithmeticOrLogicalCommands:
      return commandType.C_ARITHMETIC
    if re.match(self.pushCommandSyntax, self.currentCommand) != None:
      return commandType.C_PUSH
    if re.match(self.popCommandSyntax, self.currentCommand) != None:
      return commandType.C_POP

  def arg1(self):
    if self.commandType() == commandType.C_ARITHMETIC:
      return self.currentCommand
    if self.commandType() == commandType.C_PUSH:
      return re.findall('|'.join(self.memorySegments), self.currentCommand)[0]
    if self.commandType() == commandType.C_POP:
      return re.findall('|'.join(self.memorySegments), self.currentCommand)[0]

  def arg2(self):
    if self.commandType() == commandType.C_PUSH:
      return re.split(" ", self.currentCommand)[-1]
    if self.commandType() == commandType.C_POP:
      return re.split(" ", self.currentCommand)[-1]
