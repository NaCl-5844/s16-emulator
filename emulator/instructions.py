class Instruction: # I need to find a way to incorporate the cycle cost of each instruction... eventually
# "i16..." -> 16-bit instruction / also fixes built-in function clashes

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


def i16_ior(i_packet):
    a = i_packet["a"]
    b = i_packet["b"]
    out_i_packet = {}
    out_i_packet["c"] = a | b
    # copy <packet>, except from ["a"] and ["b"], to <outbound_packet> using whatever func to merge dictionaries
    return out_i_packet


    # def i16_and(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a & b
        # 	return out_i_packet
    # def i16_xor(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a ^ b
        # 	return out_i_packet
    # def i16_abs(i_packet):
        # 	a = i_packet["a"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = abs(a)
        # 	return out_i_packet
    # def i16_add(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a + b
        # 	return out_i_packet
    # def i16_adc(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a & b
        # 	return out_i_packet
    # def i16_sub(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a & b
        # 	return out_i_packet
    # def i16_sbb(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a & b
        # 	return out_i_packet
    # def i16_bsh(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a & b
        # 	return out_i_packet
    # def i16_bd(i_packet):

        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a & b
        # 	return out_i_packet
    # def i16_lim(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a & b
        # 	return out_i_packet
    # def i16_ls(i_packet):

        # 	return out_i_packet
    # def i16_cmp(i_packet):
        # 	a = i_packet["a"]
        # 	b = i_packet["b"]
        # 	out_i_packet = {}
        # 	out_i_packet["c"] = a & b
        # 	return out_i_packet
    # def i16_tst(i_packet):
        # 	return 0
    # def i16_jmp(i_packet):
        # 	return 0
    # def i16_int(i_packet):
        # 	return 0
