// Computes RAM[2]=RAM[0]*RAM[1]

  @2
  M=0 // sum=0
  @0
  D=M // D=RAM[0]
  @END
  D; JEQ // jump to END if RAM[0]=0
  @1
  D=M // D=RAM[1]
  @END
  D; JEQ // jump to END if RAM[1]=0
  @i
  M=D // i=RAM[1]

(LOOP)
  @i
  M=M-1 // i=i-1
  @0
  D=M // D=RAM[0]
  @2
  M=M+D // sum=sum+RAM[0]
  @i
  D=M // D=i
  @LOOP
  D;JGT // jump to LOOP if i>0

(END)
  @END
  0;JMP
