# s16-emulator

s16 is a simple ISA, 16-bits, and a project to learn how to make a low level CPU emulation. 

\*\*Currently my focus is 100% on brainstorming/documenting s16's Out of Order/[scheduling](https://github.com/NaCl-5844/s16-emulator/blob/main/docs/brainstorms/dep_matrix_scheduling%5Bsingle_cycle_window%5D.txt) logic which will determine the direction of the project. [current test](https://github.com/NaCl-5844/s16-emulator/blob/main/docs/brainstorms/single_cycle_window(SCW)_testing.txt)\*\* 



Main Goals:
  - Implement main arithmetic, branching and memory instructions
  - Implement simple instruction prefetching.
  - Configurable cache size and replacement algorithms \[currently only LRU\]
  - Implement all instrutions, stress and bug test instructions, memory and cache coherence
  - cycle costs for every insruction, memory location*, cache accesses and stalls
  - configurable prefetching
  - Simple branch prediction and branch target buffer(BTB)
  
  *Access speeds are rarely equal over a given memory structure

Long-Term Goals:
  - Output a file containing changes in memory and functional units each cycle
  - Overhaul replacement algorithms with cycle costs, and add more complex algorithms
  - Peripherals such as a simple screen and user input
  - Code some example demo's and benchmarks
  

## Milestones 
  - Configurable main memory size ✓
  - Take s16 assembly from a file -> assemble microcode -> place in emulator memory ✓
  - Configurable, write-back cache hierarchy with:
    - Level 1 Data and Instruction Caches \[Currently Required\] ✓
    - Level 2 unified cache \(Optional\) ✓
    - [Write-back](https://www.geeksforgeeks.org/write-through-and-write-back-in-cache/) logic should work regardless of a level 2 cache being enabled ✓
