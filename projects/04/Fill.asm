// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//// Replace this comment with your code.
(LOOPSCREEN)
  @8192
  D=A // D=8192
  @i
  M=D // i=8192
(LOOPPIXEL)
  @i
  D=M-1 // D=M[i]-1
  M=D 
  @LOOPSCREEN
  D;JLT // jump to LOOPSCREEN if i < 0
  @SCREEN
  D=D+A // D=i+SCREEN
  @PIXEL
  M=D // PIXEL=i+SCREEN
  @KBD
  D=M // D=KBD's value
  @BLACK
  D;JNE // jump to BLACK if D != 0
  @PIXEL
  D=M
  A=D
  M=0 // M[PIXEL]=0
  @LOOPPIXEL
  0;JMP 
(BLACK)
  @PIXEL
  D=M
  A=D
  M=-1 // M[PIXEL]=-1
  @LOOPPIXEL
  0;JMP 
