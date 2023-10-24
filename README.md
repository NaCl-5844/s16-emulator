# s16-emulator

s16 is a simple ISA, 16-bits, and a project to learn how to make a low level CPU emulation. 

Main Goals:
  - Implement main arithmetic, branching and memory instructions
  - Implement simple instruction prefetching.
  - Configurable cache size and replacement algorithms \[currently only LRU\]
  - Implement all instrutions, stress and bug test instructions, memory and cache coherence
  - cycle costs for every insruction, memory location*, cache accesses and stalls
  - configurable prefetching and simple/naive branch prediction
  
  *Access speeds are rarely equal over a given memory structure

Long-Term Goals:
  - Overhaul replacement algorithms with cycle costs, and add more complex algorithms
  - Peripherals such as a simple screen and user input
  - Code some example demo's and benchmarks
  

## Milestones 
  - Configurable main memory size ✓
  - Output a file containing changes in memory and functional units each cycle ✓
  - Take s16 assembly from a file -> assemble microcode -> place in emulator memory ✓
  - Configurable, write-back cache hierarchy with:
    - Level 1 Data and Instruction Caches \[Currently Required\] ✓
    - Level 2 unified cache \(Optional\) ✓
    - [Write-back](https://www.geeksforgeeks.org/write-through-and-write-back-in-cache/) logic should work regardless of a level 2 cache being enabled ✓

- - - 

This project aims to give me the tools and knowledge to complete my dream microprocessor [t16(WIP)](https://github.com/NaCl-5844/t16) which will focus on maximum throughput for a (mostly) 16-bit architecture.
I also plan on making much better documentation (once I hit v1.0.0) which will include the implementation of s16's:
  - Instruction set
  - CPU architecture / Pipeline
  - Cache replacement algorithms 
  - Prefetching
  - Branch prediction
