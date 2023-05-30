


"""
[key: x=opcode s=subop, a|b=source, c=dest, n=imm/val]
Operations:

xxxx|op-|format-------------
0000 ior 000xxxx-ccc-bbb-aaa <ior r0 r0 r0> == noop -- special case
0001 and 000xxxx-ccc-bbb-aaa 
0010 xor 000xxxx-ccc-bbb-aaa
0011 abs 000xxxx-ccc-sss-aaa sss: abs neg sxt two inv 
0100 add 000xxxx-ccc-bbb-aaa
0101 adc 000xxxx-ccc-bbb-aaa
0110 sub 000xxxx-ccc-bbb-aaa
0111 sbb 000xxxx-ccc-bbb-aaa
1000 bsh 000xxxx-sss-bbb-aaa sss: bsl bsr asr csl csr
1001 bd  000xxxx-ccc-sss-aaa sss: lzc tzc bc  bfm bfl bvl bvm / bd: bit data / bf[l/m]: find [l/m]sb / bv[l/m]: value [l/m]sb
1010 lim 000xxxx-cnn-nnn-nnn   c: r0,r4 / n..: sign extended ±127
1011 ls  000xxxx-sss-bbb-aaa sss: ldb ldw ldp stb stw stp mv  cmv / [b]yte [w]ord=2B [p]age=2B*8
1100 cmp 000xxxx-sss-bbb-aaa sss: sn  lt  le  eq  gt  ge  slt sgt / return: false=0 true=1 / 
1101 tst 000xxxx-sss-bbb-aaa sss: tio tno tan tna txo txn tim tni / return: false=0 true=1
1110 jmp 000xxxx-sss-bbb-aaa sss: jal jr  jd  ji  cjr cjd cji ret / bbb: ađdr / aaa: cmp to true=1
1111 int 000xxxx-nnn-nnn-nnn n..: interupt code, data or address [wip]


"""



class control:
"""
[Aim]: To decode, schedule, clock, interupts and monitor all "in-flight" operations

[Varables/Objects?]: count/program_counter, clock, instruction_decode, ...
"""
	
class memory:
"""
[Aim]: To generate the various memory structures in a dynamic method which allows
a lot of testing and debugging.

[varables/Objects?]: capacity=x/direct_memory, capacity=x/ways=y/algorithm=z/cache_memory
"""
	
class interconnect:
"""
[Aim]: to allow communication between peripheral components connected to the CPU.

[Variables]: bus_address, communication_type?

"""
	
class execute:
"""
[Aim]: stores all instructions and sub operations that are mapped to functions. The functions
must act on/the default data type will be hexadecimal.

[Objects] arithmetic_unit, control_unit, memory_buffer
"""
	
class packet:
"""
[Aim]: To hold data, flags, adresses, etc which has been decoded from a given instruction. This packet will live until there are
no more sub operations and/or a "write-back" has occured.

[Variables]: instruction, sub_operation(s), source(s), sink(s/destination). Possibly debugging variables such as age(cycles lived).

[Info]
Maximum packet side

"""


