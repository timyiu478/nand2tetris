class SymbolTable:
  def __init__(self, scope):
    self.symbol_table = {}
    self.indexes = {
      "static": -1,
      "field": -1,
      "argument": -1,
      "var": -1,
    }
    self.scope = scope

  def reset(self):
    self.symbol_table = {}
    self.indexes = {
      "static": -1,
      "field": -1,
      "argument": -1,
      "var": -1,
    }
  
  def define(self, name, type, kind):
    self.indexes[kind] += 1
    self.symbol_table[name] = { "type": type, "kind": kind, "index": self.indexes[kind] }

  def varCount(self, kind):
    return self.indexes[kind] + 1

  def kindOf(self, name):
    if name in self.symbol_table:
      if self.symbol_table[name]["kind"] == "field":
          return "this"
      if self.symbol_table[name]["kind"] == "var":
          return "local"
      return self.symbol_table[name]["kind"]

  def typeOf(self, name):
    if name in self.symbol_table:
      return self.symbol_table[name]["type"]

  def indexOf(self, name):
    if name in self.symbol_table:
      return self.symbol_table[name]["index"]
