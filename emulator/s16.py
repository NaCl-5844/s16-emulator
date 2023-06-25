#!/usr/bin/env python
from pprint import pprint # Pretty Print -- may create own print functions
# import math

#----[Global Functions]----#

def cache_print(cache, name):
    tag_count = 0
    print(f"\n{name}",'{')
    for way in cache:
        print(way, end="")
        for t in range(len(cache[way]['tag'])):
            print(f"\t{cache[way]['tag'][t]} [{' '.join(list(cache[way]['data'][t].values()))}]")
    print('}')

def mem_print(memory, name):
    memory.pop('cost')
    print(f"\n{name}",'{')
    rows = len(memory) >> 3 # x >> 3 == x/2**3
    for r in range(rows):
        try:
            print(f"\t{' '.join(list(memory.values())[r*8:(r+1)*8])}")
        except KeyError:
            0
    print('}')
#--------------------------#

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



class s16:
    # "i16..." -> 16-bit instruction / also fixes built-in function clashes
    def i16_ior(i_packet):
        a = i_packet["a"]
        b = i_packet["b"]
        out_i_packet = {}
        out_i_packet["c"] = a | b
        # copy <packet>, except from ["a"] and ["b"], to <outbound_packet> using hatever func to merge dictionaries
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

# class control:
    """
    [Aim]: To decode, schedule, clock, interupts and monitor all "in-flight" operations
    
    [Varables/Objects?]: count/program_counter, clock, instruction_decode, ...
    """
    
class memory:
    """
    [Aim]: To generate the various memory structures in a dynamic way which allows
    a lot of testing and debugging.
    
    [varables/Objects?]: capacity=x/direct_memory, capacity=x/ways=y/algorithm=z/cache_memory
    """

    # call variables

    def __init__(self, page_size):
        self.page_size = page_size

    @classmethod
    def lru(cache, way, entry): # Least Recently Used
        """
        I think this needs to be its own class
        
        OR
        
        Coded alongside memory.read()
        """
        target_way = cache[way]
        target_way['addr'].insert(0, target_way['addr'].pop(entry['addr']))
        target_way['data'].insert(0, target_way['data'].pop(entry['data']))
        
        return target_way
    

    def generate_cache(self, byte_capacity, ways, replacement_algorithm, cost):
        """
        x-way set-associative describes how the replacement algorithm is split across all entries of the cache.
        -- fully associative means the algorithm would act on all entries as a single set.
        -- 2-way set-associative means if one half is accessed and an entry is replaced, due to the 2-way addressing the other half would not be effected.
        -- 4-way ... etc, etc.
        The pros and cons of speed and complexity decide the specific type of a replacment algorithm.
        [E.g. For # of ways: LRU is simple and fast for low # of ways, Random Replacement(RR) is trivial and combined algorithms, like ARC, are slower but more efficient]
        """
        cache = {} # cache decoding: way | tag | offset
        total_tag_count = int((byte_capacity >> 1) / self.page_size) # use self.page_size # Shifting right divides by powers of 2 (x>>1 == x/2**1)
        tags_per_way = int(total_tag_count / ways)
        print('total_tag_count:', total_tag_count, '\ntags_per_way:', tags_per_way)
        if ways < 2:
            cache['way_0'] = {'tag': [], 'data': []}
            for a in range(total_tag_count):
                cache['way_0']['tag'].insert(0, '0000')
                cache['way_0']['data'].insert(0, {f"{offset:0{self.page_size.bit_length()-4}x}": '0000' for offset in range(self.page_size)})
        else:
            for w in range(ways): # ways, as in, x-way set-associative
                cache[f'way_{w:x}'] = {'tag': [], 'data': []}
                for a in range(tags_per_way):
                    cache[f"way_{w:x}"]['tag'].insert(0, '0000')
                    cache[f"way_{w:x}"]['data'].insert(0, {f"{offset:0{self.page_size.bit_length()-4}x}": '0000' for offset in range(self.page_size)})
        return cache # cache['way_x']['tag'/'data']


    def generate_memory(self, byte_capacity, cost):
        address_count = byte_capacity >> 1
        memory = {}
        for a in range(address_count): # building the memory
            memory[f"{a:0{address_count.bit_length()-4}x}"] = '0000' # Hex formatting -- address_count.bit_length()-4 == log2(x)-4
        memory["cost"] = [cost]
        return memory

    def generate_reorder_buffer():
        0
   
    # Memory read/write functions seem unnecessary 
    
    # def read_memory(memory, address, data):
    #     updated_memory = {}
    #     return updated_memory
    
    # def write_memory(memory, address, data):
    #     updated_memory = {}
    #     return updated_memory
    
    def read_cache(cache, address, data):
        # < split address into (set,tag) >
        # < search set >
        # entry = {'addr': address, 'data': data}
        # < if entry['addr'] in cache['way']: >
        # <     read cache['way']['address'] >
        # <     cache['replacement_algorithm'](cache, cache['way']. entry) # lru(cache, way, entry)
            
        updated_cache = {}
        return updated_cache
    
    def write_cache(cache, address, data):
        updated_cache = {}
        return updated_cache

# class interconnect: 
# """
# [Aim]: to allow communication between peripheral components connected to the CPU.

# [Variables]: bus_address, communication_type?

# """
    
# # class execute:
# """
# [Aim]: stores all instructions and sub operations that are mapped to functions. The functions
# must act on/the default data type will be hexadecimal.

# [Objects] arithmetic_unit, control_unit, memory_buffer
# """
    
# # class packet:
# """
# [Aim]: To hold data, flags, adresses, etc which has been decoded from a given instruction. This packet will live until there are
# no more sub operations and/or a "write-back" has occured.

# [Variables]: instruction, sub_operation(s), source(s), sink(s/destination). Possibly debugging variables such as age(cycles lived).

# [Info]
# Maximum packet side

# """
    


#----Testing----#
mem = memory(16)
gp_registers = mem.generate_memory(64, 2)
l1_data_cache = mem.generate_cache(64, 2, memory.lru, 4)

gp_registers['00'] = 'ffff'


mem_print(gp_registers, 'GPR')
cache_print(l1_data_cache, 'L1 Cache')
