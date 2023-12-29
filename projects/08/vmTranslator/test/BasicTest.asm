// VM Code: add
// D = RAM[SP--]
@SP
AM=M-1
D=M
// A=SP--; RAM[A] = D + RAM[A]
@SP
AM=M-1
D=D+M
@SP
A=M
M=D
// SP++
@SP
M=M+1
