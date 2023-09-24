# s16-emulator

s16 is a simple ISA, 16-bit and a project to learn how to make a low level CPU emulation.

Main Goals:
  - Configurable main memory size
  - Configurable cache size and replacement algorithms
  - Output a file containing changes in memory and functional units each cycle
  - Take s16 assembly from a file -> assemble microcode -> place in emulator memory

Secondary Goals:
  - cycle costs for every insruction, memory location*, cache accesses and stalls
  - Peripherals such as a simple screen and keyboard

Long-Term Goals:
  - Code and assemble in the command-line/shell, store the bin file and/or directly run the assemly code

*Access speeds are rarely equal over a given memory structure
