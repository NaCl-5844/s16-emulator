from functools import cache
from decode import register as r


# I need to find a way to incorporate the cycle cost of each instruction... eventually

def noop(cpu, u, m, l):
    pass

def s16_ior(cpu, u, m, l):
    cpu.register[r(m)] = f"{int(cpu.register(r(m)), 16) | int(cpu.register(r(l)), 16):04x}"

def s16_nor(cpu, instruction):
    pass
def s16_and(cpu, instruction):
    pass
def s16_nan(cpu, instruction):
    pass
def s16_xor(cpu, instruction):
    pass
def s16_xno(cpu, instruction):
    pass
def s16_nim(cpu, instruction):
    pass
def s16_imp(cpu, instruction):
    pass
def s16_abs(cpu, instruction):
    pass
def s16_neg(cpu, instruction):
    pass
def s16_sxt(cpu, instruction):
    pass
def s16_two(cpu, instruction):
    pass
def s16_inv(cpu, instruction):
    pass
def s16_inc(cpu, instruction):
    pass
def s16_avr(cpu, instruction):
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
def s16_bc(cpu, instruction):
    pass
def s16_brs(cpu, instruction):
    pass
def s16_bst(cpu, instruction):
    pass
def s16_lzc(cpu, instruction):
    pass
def s16_tzc(cpu, instruction):
    pass
def s16_bfm(cpu, instruction):
    pass
def s16_bfl(cpu, instruction):
    pass
def s16_bvl(cpu, instruction):
    pass
def s16_bvm(cpu, instruction):
    pass

def s16_adc(cpu, instruction):
    pass
def s16_sbb(cpu, instruction):
    pass
def s16_mulb(cpu, instruction):
    pass
def s16_mul(cpu, instruction):
    pass

def s16_add(cpu, instruction):
    pass

def s16_sub(cpu, instruction):
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
def s16_cmvz(cpu, instruction):
    pass
def s16_cmvnz(cpu, instruction):
    pass
def s16_cmvc(cpu, instruction):
    pass
def s16_cmvcz(cpu, instruction):
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

def s16_jir(cpu, instruction):
    pass
def s16_jrr(cpu, instruction):
    pass
def s16_jrd(cpu, instruction):
    pass
def s16_brz(cpu, instruction):
    pass
def s16_brc(cpu, instruction):
    pass
def s16_brcz(cpu, instruction):
    pass
def s16_bdz(cpu, instruction):
    pass
def s16_bdc(cpu, instruction):
    pass
def s16_bdcz(cpu, instruction):
    pass
def s16_mrc(cpu, instruction):
    pass
def s16_mrz(cpu, instruction):
    pass
def s16_mrcz(cpu, instruction):
    pass

def s16_jlr(cpu, instruction):
    pass
def s16_jld(cpu, instruction):
    pass
def s16_ret(cpu, instruction):
    pass

def s16_lpc(cpu, instruction):
    pass
def s16_lsr(cpu, instruction):
    pass
def s16_lcr(cpu, instruction):
    pass
def s16_scr(cpu, instruction):
    pass

def s16_int(cpu, instruction):
    pass

def err():
    raise KeyError('Operation does not exist')

@cache
def decode(instruction :hex):
    print(f"instruction: {instruction}")
    raw_instruction = f"{(int(instruction, 16)):0{16}b}"
    operation_code = raw_instruction[:4] # from here
    upper_sub_instruction = raw_instruction[4:8]
    mid_sub_instruction = raw_instruction[8:12]
    lower_sub_instruction = raw_instruction[12:]
    c = int(operation_code, 2)
    s = int(upper_sub_instruction, 2)

    format_range = { # "It ain't much, but it's honest work"
        ((2>=c>=0) or (c==14 and 15>=s>=13)) : 'XXXXSSSSAAAANNNN', #
        (4>=c>=3)                            : 'XXXXCCCCBBBBAAAA', #
        (c==11)                              : 'XXXXCCCNNNNNNNNN', #
        ((15>=s>=12) and (not((c==14 and 15>=s>=13)or((c==14) and (s==0))or(c==15 and s==15)))) : 'XXXXSSSSBBBBAAAA', #
        ((c==14) and (s==0))                 : 'XXXXSSSSNNNNNNNN'} #

    print(f"{format_range[True]}\n{raw_instruction}") # [ DEBUG ]
    if format_range[True] == 'XXXXCCCNNNNNNNNN':
        upper_sub_instruction = raw_instruction[7:9]
        mid_sub_instruction = raw_instruction[9:13]
    # print(operation_code, upper_sub_instruction, mid_sub_instruction, lower_sub_instruction) # [ DEBUG ]
    i = operation_code
    u = upper_sub_instruction
    m = mid_sub_instruction
    l = lower_sub_instruction

    instruction_decode = { # This is grim, but the most efficient way I can think of decoding ._. + pasting into columbs is easier
        (i=='0000'): {
            (u=='0000'): (s16_ior, 1),
            (u=='0001'): (s16_nor, 1),
            (u=='0010'): (s16_and, 1),
            (u=='0011'): (s16_nan, 1),
            (u=='0100'): (s16_xor, 1),
            (u=='0101'): (s16_xno, 1),
            (u=='0110'): (s16_abs, 1),
            (u=='0111'): (s16_neg, 1),
            (u=='1000'): (s16_sxt, 1),
            (u=='1001'): (s16_two, 1),
            (u=='1010'): (s16_inv, 1),
            (u=='1011'): (s16_avr, 1),
            (u=='1100'): (s16_inc, 1),
            (u=='1101'): (s16_dec, 1),
            (u=='1110'): err(),
            (u=='1111'): err()},
        (i=='0001'): {
            (u=='0000'): (s16_bsl, 2),
            (u=='0001'): (s16_bsr, 2),
            (u=='0010'): (s16_asr, 2),
            (u=='0011'): (s16_csl, 3),
            (u=='0100'): (s16_csr, 3),
            (u=='0101'): (s16_bc, 3),
            (u=='0110'): (s16_brs, 1),
            (u=='0111'): (s16_bst, 1),
            (u=='1000'): (s16_lzc, 3),
            (u=='1001'): (s16_tzc, 3),
            (u=='1010'): (s16_bfm, 2),
            (u=='1011'): (s16_bfl, 2),
            (u=='1100'): (s16_bvl, 2),
            (u=='1101'): (s16_bvm, 2),
            (u=='1110'): err(),
            (u=='1111'): err()},
        (i=='0010'): {
            (u=='0000'): (s16_adc , 1),
            (u=='0001'): (s16_sbb , 1),
            (u=='0010'): (s16_mulb, 3),
            (u=='0011'): (s16_mul , 4),
            (u=='0100'): err(),
            (u=='0101'): err(),
            (u=='0110'): err(),
            (u=='0111'): err(),
            (u=='1000'): err(),
            (u=='1001'): err(),
            (u=='1010'): err(),
            (u=='1011'): err(),
            (u=='1100'): err(),
            (u=='1101'): err(),
            (u=='1110'): err(),
            (u=='1111'): err()},
        (i=='0011'): {True: (s16_add, 1)},
        (i=='0100'): {True: (s16_sub, 1)},
        (i=='0101'): {True: err()},
        (i=='0110'): {True: err()},
        (i=='0111'): {True: err()},
        (i=='1000'): {True: err()},
        (i=='1001'): {True: err()},
        (i=='1010'): {True: err()},
        (i=='1011'): {True: (s16_lim, 1)},
        (i=='1100'): {
            (u=='0000'): (s16_ldb, 8),
            (u=='0001'): (s16_ldw, 8),
            (u=='0010'): (s16_ldp, 8),
            (u=='0011'): (s16_stb, 8),
            (u=='0100'): (s16_stw, 8),
            (u=='0101'): (s16_stp, 8),
            (u=='0110'): (s16_mv, 1),
            (u=='0111'): (s16_cmvz, 1),
            (u=='1000'): (s16_cmvnz, 1),
            (u=='1001'): (s16_cmvc, 1),
            (u=='1010'): (s16_cmvcz, 1),
            (u=='1011'): err(),
            (u=='1100'): err(),
            (u=='1101'): err(),
            (u=='1110'): err(),
            (u=='1111'): err()},
        (i=='1101'): {
            (u=='0000'): (s16_tio, 1),
            (u=='0001'): (s16_tno, 1),
            (u=='0010'): (s16_tan, 1),
            (u=='0011'): (s16_tna, 1),
            (u=='0100'): (s16_txn, 1),
            (u=='0101'): (s16_tim, 1),
            (u=='0110'): (s16_tni, 1),
            (u=='0111'): (s16_tfc, 1),
            (u=='1000'): (s16_sn, 1),
            (u=='1001'): (s16_lt, 1),
            (u=='1010'): (s16_le, 1),
            (u=='1011'): (s16_eq, 1),
            (u=='1100'): (s16_gt, 1),
            (u=='1101'): (s16_ge, 1),
            (u=='1110'): (s16_slt, 1),
            (u=='1111'): (s16_sgt, 1)},
        (i=='1110'): {
            (u=='0000'): (s16_jir, 1),
            (u=='0001'): (s16_jrr, 1),
            (u=='0010'): (s16_jrd, 1),
            (u=='0011'): (s16_brz, 1),
            (u=='0100'): (s16_brc, 1),
            (u=='0101'): (s16_brcz, 1),
            (u=='0110'): (s16_bdz, 1),
            (u=='0111'): (s16_bdc, 1),
            (u=='1000'): (s16_bdcz, 1),
            (u=='1001'): (s16_mrc, 1),
            (u=='1010'): (s16_mrz, 1),
            (u=='1011'): (s16_mdc, 1),
            (u=='1100'): (s16_mdz, 1),
            (u=='1101'): (s16_jlr, 1),
            (u=='1110'): (s16_jld, 1),
            (u=='1111'): (s16_ret, 1)},
        (i=='1111'): {
            (u=='0000'): (s16_lpc, 1), # [l]oad [p]rogram [c]ounter
            (u=='0001'): (s16_lsr, 1), # [l]oad [s]tatus [r]egister
            (u=='0010'): (s16_lcr, 1), # [l]oad [c]ontrol [r]egister
            (u=='0011'): (s16_scr, 1), # [s]tore [c]ontrol [r]egister
            (u=='0100'): (s16_clr, 1), # [cl]ear [r]egisters
            (u=='0101'): err(),
            (u=='0110'): err(),
            (u=='0111'): err(),
            (u=='1000'): err(),
            (u=='1001'): err(),
            (u=='1010'): err(),
            (u=='1011'): err(),
            (u=='1100'): err(),
            (u=='1101'): err(),
            (u=='1110'): err(),
            (u=='1111'): (s16_int, 1)}}
    if u==m==l and u=='0000':
        return (noop, 1, u, m, l)
    else:
        return (instruction_decode[True][True] + (u, m, l))













