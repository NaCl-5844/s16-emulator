#!/usr/bin/env python
# I need to find a way to incorporate the cycle cost of each instruction... eventually

def s16_ior():
    pass
def s16_and():
    pass
def s16_xor():
    pass
def s16_abs():
    pass
def s16_bs():
    pass
def s16_neg():
    pass
def s16_sxt():
    pass
def s16_two():
    pass
def s16_inv():
    pass
def s16_add():
    pass
def s16_adc():
    pass
def s16_sub():
    pass
def s16_sbb():
    pass
def s16_bsl():
    pass
def s16_bsr():
    pass
def s16_asr():
    pass
def s16_csl():
    pass
def s16_csr():
    pass
def s16_lzc():
    pass
def s16_tzc():
    pass
def s16_bc():
    pass
def s16_bfm():
    pass
def s16_bfl():
    pass
def s16_bvl():
    pass
def s16_bvm():
    pass
def s16_lim():
    pass
def s16_ldb():
    pass
def s16_ldw():
    pass
def s16_ldp():
    pass
def s16_stb():
    pass
def s16_stw():
    pass
def s16_stp():
    pass
def s16_mv():
    pass
def s16_cmv():
    pass
def s16_sn():
    pass
def s16_lt():
    pass
def s16_le():
    pass
def s16_eq():
    pass
def s16_gt():
    pass
def s16_ge():
    pass
def s16_slt():
    pass
def s16_sgt():
    pass
def s16_tio():
    pass
def s16_tno():
    pass
def s16_tan():
    pass
def s16_tna():
    pass
def s16_txn():
    pass
def s16_tim():
    pass
def s16_tni():
    pass
def s16_tfc():
    pass
def s16_jal():
    pass
def s16_jrr():
    pass
def s16_jrd():
    pass
def s16_jir():
    pass
def s16_cjr():
    pass
def s16_cjd():
    pass
def s16_cji():
    pass
def s16_ret():
    pass
def s16_int():
    pass


# formats = {
#     0: 'XXXXXXXCCCBBBAAA',
#     1: 'XXXXXXXCCCSSSAAA',
#     2: 'XXXXXXXCCNNNNNNN',
#     3: 'XXXXXXXSSSBBBAAA',
#     4: 'XXXXXXXSSSNNNNNN',
#     5: 'XXXXXXXNNNNNNNNN',
#     }
def err():
        raise KeyError('Operation does not exist')

def format_decode(raw_instruction):
    operation_code = raw_instruction[:7]
    upper_sub_instruction = raw_instruction[7:10]
    mid_sub_instruction = raw_instruction[10:13]
    lower_sub_instruction = raw_instruction[13:]

    c = int(operation_code, 2)
    s = int(upper_sub_instruction, 2)
    format_range = {
        0<=c<=6                     : 'XXXXXXXCCCBBBAAA',
        7<=c<=8                     : 'XXXXXXXCCCSSSAAA',
        c==9                        : 'XXXXXXXCCNNNNNNN',
        (10<=c<=13)|((c==14)&(s<5)) : 'XXXXXXXSSSBBBAAA',
        (c==14)&(s>4)               : 'XXXXXXXSSSNNNNNN',
        c==15                       : 'XXXXXXXNNNNNNNNN',
        }

    print(format_range[True])
    if format_range[True] == 'XXXXXXXCCNNNNNNN':
        upper_sub_instruction = raw_instruction[7:9]
        mid_sub_instruction = raw_instruction[9:13]
    print(raw_instruction, operation_code, upper_sub_instruction, mid_sub_instruction, lower_sub_instruction)

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
        i=='0111': {m=='000': s16_abs ,m=='001': s16_bs ,m=='010': s16_neg ,m=='011': s16_sxt ,m=='100': s16_two ,m=='101': s16_inv ,m=='110': err ,m=='111': err},
        i=='1000': {m=='000': s16_lzc ,m=='001': s16_tzc ,m=='010': s16_bc ,m=='011': s16_bfm ,m=='100': s16_bfl ,m=='101': s16_bvm ,m=='110': s16_bvl ,m=='111': err},
        i=='1001': {True: s16_lim},
        i=='1010': {u=='000': s16_bsl ,u=='001': s16_bsr ,u=='010': s16_asr ,u=='011': s16_csl ,u=='100': s16_csr ,u=='101': err ,u=='110': err ,u=='111': err},
        i=='1011': {u=='000': s16_ldb ,u=='001': s16_ldw ,u=='010': s16_ldp ,u=='011': s16_stb ,u=='100': s16_stw ,u=='101': s16_stp ,u=='110': s16_mv ,u=='111': s16_cmv},
        i=='1100': {u=='000': s16_sn ,u=='001': s16_lt ,u=='010': s16_le ,u=='011': s16_eq ,u=='100': s16_gt ,u=='101': s16_ge ,u=='110': s16_slt ,u=='111': s16_sgt},
        i=='1101': {u=='000': s16_tio ,u=='001': s16_tno ,u=='010': s16_tan ,u=='011': s16_tna ,u=='100': s16_txn ,u=='101': s16_tim ,u=='110': s16_tni ,u=='111': s16_tfc},
        i=='1110': {u=='000': s16_jal ,u=='001': s16_jrr ,u=='010': s16_jrd ,u=='011': s16_cjr ,u=='100': s16_cjd ,u=='101': s16_cji ,u=='110': s16_jir ,u=='111': s16_ret},
        i=='1111': {True: s16_int},
        }
    print(instruction_decode[True][True])
    print(instruction_decode)


format_decode('0001001001111101')







# '000':  ,'001':  ,'010':  ,'011':  ,'100':  ,'101':  ,'110':  ,'111':









