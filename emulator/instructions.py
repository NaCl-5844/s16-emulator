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



ior 0000000-CCC-BBB-AAA XXXXXXX-CCC-BBB-AAA
and 0000001-CCC-BBB-AAA XXXXXXX-CCC-BBB-AAA
xor 0000010-CCC-BBB-AAA XXXXXXX-CCC-BBB-AAA

abs 0000011-CCC-000-AAA XXXXXXX-CCC-SSS-AAA
bs  0000011-CCC-001-AAA XXXXXXX-CCC-SSS-AAA
neg 0000011-CCC-010-AAA XXXXXXX-CCC-SSS-AAA
sxt 0000011-CCC-011-AAA XXXXXXX-CCC-SSS-AAA
two 0000011-CCC-100-AAA XXXXXXX-CCC-SSS-AAA
inv 0000011-CCC-101-AAA XXXXXXX-CCC-SSS-AAA

add 0000100-CCC-BBB-AAA XXXXXXX-CCC-BBB-AAA
adc 0000101-CCC-BBB-AAA XXXXXXX-CCC-BBB-AAA
sub 0000110-CCC-BBB-AAA XXXXXXX-CCC-BBB-AAA
sbb 0000111-CCC-BBB-AAA XXXXXXX-CCC-BBB-AAA

bsl 0001000-000-BBB-AAA XXXXXXX-SSS-BBB-AAA
bsr 0001000-001-BBB-AAA XXXXXXX-SSS-BBB-AAA
asr 0001000-010-BBB-AAA XXXXXXX-SSS-BBB-AAA
csl 0001000-011-BBB-AAA XXXXXXX-SSS-BBB-AAA
csr 0001000-100-BBB-AAA XXXXXXX-SSS-BBB-AAA

lzc 0001001-CCC-000-AAA XXXXXXX-CCC-SSS-AAA
tzc 0001001-CCC-001-AAA XXXXXXX-CCC-SSS-AAA
bc  0001001-CCC-010-AAA XXXXXXX-CCC-SSS-AAA
bfm 0001001-CCC-011-AAA XXXXXXX-CCC-SSS-AAA
bfl 0001001-CCC-100-AAA XXXXXXX-CCC-SSS-AAA
bvl 0001001-CCC-101-AAA XXXXXXX-CCC-SSS-AAA
bvm 0001001-CCC-110-AAA XXXXXXX-CCC-SSS-AAA

lim 0001010-CCN-NNN-NNN XXXXXXX-CCN-NNN-NNN

ldb 0001011-000-BBB-AAA XXXXXXX-SSS-BBB-AAA
ldw 0001011-001-BBB-AAA XXXXXXX-SSS-BBB-AAA
ldp 0001011-010-BBB-AAA XXXXXXX-SSS-BBB-AAA
stb 0001011-011-BBB-AAA XXXXXXX-SSS-BBB-AAA
stw 0001011-100-BBB-AAA XXXXXXX-SSS-BBB-AAA
stp 0001011-100-BBB-AAA XXXXXXX-SSS-BBB-AAA
mv  0001011-110-BBB-AAA XXXXXXX-SSS-BBB-AAA
cmv 0001011-111-BBB-AAA XXXXXXX-SSS-BBB-AAA

sn  0001100-000-BBB-AAA XXXXXXX-SSS-BBB-AAA
lt  0001100-001-BBB-AAA XXXXXXX-SSS-BBB-AAA
le  0001100-010-BBB-AAA XXXXXXX-SSS-BBB-AAA
eq  0001100-011-BBB-AAA XXXXXXX-SSS-BBB-AAA
gt  0001100-100-BBB-AAA XXXXXXX-SSS-BBB-AAA
ge  0001100-101-BBB-AAA XXXXXXX-SSS-BBB-AAA
slt 0001100-110-BBB-AAA XXXXXXX-SSS-BBB-AAA
sgt 0001100-111-BBB-AAA XXXXXXX-SSS-BBB-AAA

tio 0001101-000-BBB-AAA XXXXXXX-SSS-BBB-AAA
tno 0001101-001-BBB-AAA XXXXXXX-SSS-BBB-AAA
tan 0001101-010-BBB-AAA XXXXXXX-SSS-BBB-AAA
tna 0001101-011-BBB-AAA XXXXXXX-SSS-BBB-AAA
txn 0001101-100-BBB-AAA XXXXXXX-SSS-BBB-AAA
tim 0001101-101-BBB-AAA XXXXXXX-SSS-BBB-AAA
tni 0001101-110-BBB-AAA XXXXXXX-SSS-BBB-AAA
tfc 0001101-111-BBB-AAA XXXXXXX-SSS-BBB-AAA

jal 0001110-000-BBB-AAA XXXXXXX-SSS-BBB-AAA
jrr 0001110-001-BBB-AAA XXXXXXX-SSS-BBB-AAA
jrd 0001110-010-BBB-AAA XXXXXXX-SSS-BBB-AAA
jir 0001110-011-NNN-NNN XXXXXXX-SSS-NNN-NNN
cjr 0001110-100-BBB-AAA XXXXXXX-SSS-BBB-AAA
cjd 0001110-101-BBB-AAA XXXXXXX-SSS-BBB-AAA
cji 0001110-110-NNN-NNN XXXXXXX-SSS-NNN-NNN
ret 0001110-111-NNN-NNN XXXXXXX-SSS-NNN-NNN

int 0001111-NNN-NNN-NNN XXXXXXX-NNN-NNN-NNN

"""


def s16_ior:
    pass
def s16_and:
    pass
def s16_xor:
    pass
def s16_abs:
    pass
def s16_bs:
    pass
def s16_neg:
    pass
def s16_sxt:
    pass
def s16_two:
    pass
def s16_inv:
    pass
def s16_add:
    pass
def s16_adc:
    pass
def s16_sub:
    pass
def s16_sbb:
    pass
def s16_bsl:
    pass
def s16_bsr:
    pass
def s16_asr:
    pass
def s16_csl:
    pass
def s16_csr:
    pass
def s16_lzc:
    pass
def s16_tzc:
    pass
def s16_bc:
    pass
def s16_bfm:
    pass
def s16_bfl:
    pass
def s16_bvl:
    pass
def s16_bvm:
    pass
def s16_lim:
    pass
def s16_ldb:
    pass
def s16_ldw:
    pass
def s16_ldp:
    pass
def s16_stb:
    pass
def s16_stw:
    pass
def s16_stp:
    pass
def s16_mv:
    pass
def s16_cmv:
    pass
def s16_sn:
    pass
def s16_lt:
    pass
def s16_le:
    pass
def s16_eq:
    pass
def s16_gt:
    pass
def s16_ge:
    pass
def s16_slt:
    pass
def s16_sgt:
    pass
def s16_tio:
    pass
def s16_tno:
    pass
def s16_tan:
    pass
def s16_tna:
    pass
def s16_txn:
    pass
def s16_tim:
    pass
def s16_tni:
    pass
def s16_tfc:
    pass
def s16_jal:
    pass
def s16_jrr:
    pass
def s16_jrd:
    pass
def s16_jir:
    pass
def s16_cjr:
    pass
def s16_cjd:
    pass
def s16_cji:
    pass
def s16_ret:
    pass
def s16_int:
    pass



