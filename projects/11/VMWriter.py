class VMWriter:
  def __init__(self, file):
    self.vmFile = open(file, "w")
    self.vmFile.close()
    self.vmFile = open(file, "a")

  def writePush(self, segment, index):
    self.vmFile.write(f"push {segment} {index}\n")

  def writePop(self, segment, index):
    self.vmFile.write(f"pop {segment} {index}\n")

  def writeArithmetic(self, command):
    self.vmFile.write(f"{command}\n")

  def writeLabel(self, label):
    self.vmFile.write(f"label {label}\n")

  def writeGoto(self, label):
    self.vmFile.write(f"goto {label}\n")

  def writeIf(self, label):
    self.vmFile.write(f"if-goto {label}\n")

  def writeCall(self, name, nArgs):
    self.vmFile.write(f"call {name} {nArgs}\n")

  def writeFunction(self, name, nVars):
    self.vmFile.write(f"function {name} {nVars}\n")

  def writeReturn(self):
    self.vmFile.write(f"return\n")

  def close(self):
    self.vmFile.close()
