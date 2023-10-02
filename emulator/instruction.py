#!/usr/bin/env python
from decode import register as r

# I need to find a way to incorporate the cycle cost of each instruction... eventually

def s16_ior(cpu, a, b, c):
    cpu.register[r(c)] = f"{int(cpu.register(r(a)), 16) | int(cpu.register(r(b)), 16):04x}"

def s16_and(cpu, instruction):
    pass
def s16_xor(cpu, instruction):
    pass
def s16_abs(cpu, instruction):
    pass
def s16_bs(cpu, instruction):
    pass
def s16_neg(cpu, instruction):
    pass
def s16_sxt(cpu, instruction):
    pass
def s16_two(cpu, instruction):
    pass
def s16_inv(cpu, instruction):
    pass
def s16_add(cpu, instruction):
    pass
def s16_adc(cpu, instruction):
    pass
def s16_sub(cpu, instruction):
    pass
def s16_sbb(cpu, instruction):
    pass
def s16_bsl(cpu, instruction):
    pass
def s16_bsr(cpu, instruction):
    pass
def s16_asr(cpu, instruction):
    pass
def s16_csl(cpu, instruction):
    pass
def s16_csr(cpu, instruction):
    pass
def s16_lzc(cpu, instruction):
    pass
def s16_tzc(cpu, instruction):
    pass
def s16_bc(cpu, instruction):
    pass
def s16_bfm(cpu, instruction):
    pass
def s16_bfl(cpu, instruction):
    pass
def s16_bvl(cpu, instruction):
    pass
def s16_bvm(cpu, instruction):
    pass
def s16_lim(cpu, instruction):
    pass
def s16_ldb(cpu, instruction):
    pass
def s16_ldw(cpu, instruction):
    pass
def s16_ldp(cpu, instruction):
    pass
def s16_stb(cpu, instruction):
    pass
def s16_stw(cpu, instruction):
    pass
def s16_stp(cpu, instruction):
    pass
def s16_mv(cpu, instruction):
    pass
def s16_cmv(cpu, instruction):
    pass
def s16_sn(cpu, instruction):
    pass
def s16_lt(cpu, instruction):
    pass
def s16_le(cpu, instruction):
    pass
def s16_eq(cpu, instruction):
    pass
def s16_gt(cpu, instruction):
    pass
def s16_ge(cpu, instruction):
    pass
def s16_slt(cpu, instruction):
    pass
def s16_sgt(cpu, instruction):
    pass
def s16_tio(cpu, instruction):
    pass
def s16_tno(cpu, instruction):
    pass
def s16_tan(cpu, instruction):
    pass
def s16_tna(cpu, instruction):
    pass
def s16_txn(cpu, instruction):
    pass
def s16_tim(cpu, instruction):
    pass
def s16_tni(cpu, instruction):
    pass
def s16_tfc(cpu, instruction):
    pass
def s16_jal(cpu, instruction):
    pass
def s16_jrr(cpu, instruction):
    pass
def s16_jrd(cpu, instruction):
    pass
def s16_jir(cpu, instruction):
    pass
def s16_cjr(cpu, instruction):
    pass
def s16_cjd(cpu, instruction):
    pass
def s16_cji(cpu, instruction):
    pass
def s16_ret(cpu, instruction):
    pass
def s16_int(cpu, instruction):
    pass

def err():
        raise KeyError('Operation does not exist')

def decode(raw_instruction :bin):
    operation_code = raw_instruction[:7]
    upper_sub_instruction = raw_instruction[7:10]
    mid_sub_instruction = raw_instruction[10:13]
    lower_sub_instruction = raw_instruction[13:]
    c = int(operation_code, 2)
    s = int(upper_sub_instruction, 2)
    format_range = {
        0<=c<=6                     : 'XXXXXXXCCCBBBAAA', # format: 0
        7<=c<=8                     : 'XXXXXXXCCCSSSAAA', # format: 1
        c==9                        : 'XXXXXXXCCNNNNNNN', # format: 2
        (10<=c<=13)|((c==14)&(s<5)) : 'XXXXXXXSSSBBBAAA', # format: 3
        (c==14)&(s>4)               : 'XXXXXXXSSSNNNNNN', # format: 4
        c==15                       : 'XXXXXXXNNNNNNNNN', # format: 5
        }
    print(f"{format_range[True]}\n{raw_instruction}") # [ DEBUG ]
    if format_range[True] == 'XXXXXXXCCNNNNNNN':
        upper_sub_instruction = raw_instruction[7:9]
        mid_sub_instruction = raw_instruction[9:13]
    # print(operation_code, upper_sub_instruction, mid_sub_instruction, lower_sub_instruction) # [ DEBUG ]
    i = operation_code[3:7]
    u = upper_sub_instruction
    m = mid_sub_instruction
    l = lower_sub_instruction

    instruction_decode = { # This is grim, but the most efficient way I can think of decoding ._.
        i=='0000': {True: s16_ior},
        i=='0001': {True: s16_and},
        i=='0010': {True: s16_xor},
        i=='0011': {True: s16_add},
        i=='0100': {True: s16_adc},
        i=='0101': {True: s16_sub},
        i=='0110': {True: s16_sbb},
        i=='0111': {m=='000': s16_abs, m=='001': s16_bs,  m=='010': s16_neg, m=='011': s16_sxt, m=='100': s16_two, m=='101': s16_inv, m=='110': err,     m=='111': err},
        i=='1000': {m=='000': s16_lzc, m=='001': s16_tzc, m=='010': s16_bc,  m=='011': s16_bfm, m=='100': s16_bfl, m=='101': s16_bvm, m=='110': s16_bvl, m=='111': err},
        i=='1001': {True: s16_lim},
        i=='1010': {u=='000': s16_bsl, u=='001': s16_bsr, u=='010': s16_asr, u=='011': s16_csl, u=='100': s16_csr, u=='101': err,     u=='110': err,     u=='111': err},
        i=='1011': {u=='000': s16_ldb, u=='001': s16_ldw, u=='010': s16_ldp, u=='011': s16_stb, u=='100': s16_stw, u=='101': s16_stp, u=='110': s16_mv,  u=='111': s16_cmv},
        i=='1100': {u=='000': s16_sn,  u=='001': s16_lt,  u=='010': s16_le,  u=='011': s16_eq,  u=='100': s16_gt,  u=='101': s16_ge,  u=='110': s16_slt, u=='111': s16_sgt},
        i=='1101': {u=='000': s16_tio, u=='001': s16_tno, u=='010': s16_tan, u=='011': s16_tna, u=='100': s16_txn, u=='101': s16_tim, u=='110': s16_tni, u=='111': s16_tfc},
        i=='1110': {u=='000': s16_jal, u=='001': s16_jrr, u=='010': s16_jrd, u=='011': s16_cjr, u=='100': s16_cjd, u=='101': s16_cji, u=='110': s16_jir, u=='111': s16_ret},
        i=='1111': {True: s16_int},
        }
    return (instruction_decode[True][True], u, m, l)

decode('0000000001111101')


print(r('001'))











