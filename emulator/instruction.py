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

def format_decode(raw_instruction):
    operation_code = raw_instruction[:7]
    upper_sub_instruction = raw_instruction[7:10]
    mid_sub_instruction = raw_instruction[10:13]
    lower_sub_instruction = raw_instruction[13:]

    x = int(operation_code, 2)
    y = int(upper_sub_instruction, 2)
    format_range = {
        0<=x<=6                     : 'XXXXXXXCCCBBBAAA',
        7<=x<=8                     : 'XXXXXXXCCCSSSAAA',
        x==9                        : 'XXXXXXXCCNNNNNNN',
        (10<=x<=13)|((x==14)&(y<5)) : 'XXXXXXXSSSBBBAAA',
        (x==14)&(y>4)               : 'XXXXXXXSSSNNNNNN',
        x==15                       : 'XXXXXXXNNNNNNNNN',
        }
    print(format_range[True])
    if format_range[True] == 'XXXXXXXCCNNNNNNN':
        upper_sub_instruction = raw_instruction[7:9]
        mid_sub_instruction = raw_instruction[9:13]
    print(raw_instruction, operation_code, upper_sub_instruction, mid_sub_instruction, lower_sub_instruction)


format_decode('0001001001111101')
