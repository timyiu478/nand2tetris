from enum import Enum

class CommandType(Enum):
 C_ARITHMETIC = 0 
 C_PUSH = 1 
 C_POP = 2 
 C_LABEL = 3
 C_GOTO = 4
 C_IF = 5
 C_FUNCTION = 6
 C_RETURN = 7
 C_CALL = 8
