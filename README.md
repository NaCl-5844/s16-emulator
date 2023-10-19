# s16-emulator

s16 is a simple ISA, 16-bit and a project to learn how to make a low level CPU emulation. 

Main Goals:
  - Configurable, write-back cache hierarchy with:
      - level 1 Data and Instruction Caches \[Currently Required\]
      - Level 2 unified cache \(Optional\)
      - [Write-back](https://www.geeksforgeeks.org/write-through-and-write-back-in-cache/) logic should work regardless of a level 2 cache being enabled
  - Implement main arithmetic, branching and memory instructions
  - Implement simple instruction prefetching.
  - Configurable cache size and replacement algorithms \[currently onlyh LRU\]
  - Implement all instrutions, stress and bug test instructions, memory and cache coherence. 


Secondary Goals:
  - cycle costs for every insruction, memory location*, cache accesses and stalls
  - configurable prefetching and simple/naive branch prediction
  

Long-Term Goals:
  - Peripherals such as a simple screen and user input

*Access speeds are rarely equal over a given memory structure

## Milestones 
  - Configurable main memory size ✓
  - Output a file containing changes in memory and functional units each cycle ✓
  - Take s16 assembly from a file -> assemble microcode -> place in emulator memory ✓

- - - 

This project aims to give me the tools and knowledge to complete my dream microprocessor [t16(WIP)](https://github.com/NaCl-5844/t16) which will focus on maximum throughput for a (mostly) 16-bit architecture 
