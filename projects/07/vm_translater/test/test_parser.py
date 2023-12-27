import sys

sys.path.insert(0, "../") 

from modules import parser, command_type
import unittest

commands = [
"push constant 10",
"pop local 0",
"push constant 21",
"push constant 22",
"pop argument 2",
"pop argument 1",
"push constant 36",
"pop this 6",
"push constant 42",
"push constant 45",
"pop that 5",
"pop that 2",
"push constant 510",
"pop temp 6",
"push local 0",
"push that 5",
"add",
"push argument 1",
"sub",
"push this 6",
"push this 6",
"add",
"sub",
"push temp 6",
"add"
]

commandType = command_type.CommandType

parser = parser.Parser("BasicTest.vm")

class TestParser(unittest.TestCase):


  def test_0_commands(self):
    self.assertEqual(parser.commands, commands)

  def test_1_command_type(self):
    parser.advance()
    self.assertEqual(parser.commandType(), commandType.C_PUSH)
    parser.advance()
    self.assertEqual(parser.commandType(), commandType.C_POP)
  
  def test_2_arg_1_2(self):
    self.assertEqual(parser.arg1(), "local")
    self.assertEqual(parser.arg2(), "0")
    parser.advance()
    self.assertEqual(parser.arg1(), "constant")
    self.assertEqual(parser.arg2(), "21")

if __name__ == "__main__":
  unittest.main()
