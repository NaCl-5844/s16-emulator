


"""
[key: x=adressing s=subop, a|b=source, c=dest, n=imm/val]
Operations:

0000 ior 000xxxx-ccc-bbb-aaa
0001 and 000xxxx-ccc-bbb-aaa 
0010 xor 000xxxx-ccc-bbb-aaa
0011 abs 000xxxx-ccc-sss-aaa sss: abs neg sxt two inv 
0100 add 000xxxx-ccc-bbb-aaa
0101 adc 000xxxx-ccc-bbb-aaa
0110 sub 000xxxx-ccc-bbb-aaa
0111 sbb 000xxxx-ccc-bbb-aaa
1000 bsh 000xxxx-sss-bbb-aaa sss: bsl bsr asr csl csr
1001 lim 000xxxx-ccc-nnn-nnn
1010 --- 000xxxx-xxx-xxx-xxx
1011 ls  000xxxx-sss-bbb-aaa sss: ldb ldw stb stw
1100 cmp 000xxxx-sss-bbb-aaa sss: csn clt cle ceq cgt cge cez
1101 tst 000xxxx-sss-bbb-aaa sss: tio tno tan tna txo txn tim tni
1110 jmp 000xxxx-sss-bbb-aaa sss: 
1111 int 000xxxx-nnn-nnn-nnn




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
	
class bus:
"""

"""
	
class execute:
"""

"""
	
class packet:
"""
[Aim]: To hold data, flags, adresses, etc which has been decoded from a given instruction. This packet will live until there are
no more sub operations and/or a "write-back" has occured.

[Variables]: instruction, sub_operation(s), source(s), sink(s/destination). Possibly debugging variables such as age(cycles lived).
"""
	