#!/usr/bin/env python
# from pprint import pprint # Pretty Print -- may create own print functions
# import math

##----[Note]----##

# s16 = Simple 16
# Page = Block of 32 Bytes = (16-bits*16)/8

#----[Custom Pretty Print class]----#

class pprint:

    def cache_horiz(cache, name):
        print(f"{name}","{\n\n","\t\t\b\b0x0  0x1  0x2  0x3  0x4  0x5  0x6  0x7  0x8  0x9  0xa  0xb  0xc  0xd  0xe  0xf\n") # Hardcoded for simplicity
        for way in cache:
            print(way.replace('ay_', ''), end='')
            for t in range(len(cache[way]['tag'])):
                print(f"\t{cache[way]['tag'][t]} [{' '.join(list(cache[way]['data'][t].values()))}]")
        print("}\n")

    def cache_vert(cache, name):
        columns = range(len(cache))
        print(f"{name}","{\n") # Title
        for x_axis_ways in columns: # Display "ways", or sets, along the x axis in a table format
            print(f"\tw{x_axis_ways}", end='')
        print()
        for x_axis_tags in cache:  # Display "tags", along the x axis in a table format
            print(f"\t{cache[x_axis_tags]['tag'][0]}", end='')
        print("\n")
        for offset, data in enumerate(cache['way_0']['data'][0]): # A page's offset is the fine-grain address to access a given word(s16 -> 16-bit -> 2 bytes)
            print(hex(offset),"\t", end='')
            for pages in range(len(cache['way_0']['data'])): # Pages/blocks/cachelines are blocks of data which increaces the efficientcy of data movement
                for ways in columns: # or sets -- x-way set-associative
                    print(cache[f"way_{ways}"]['data'][pages][f"{offset:x}"],"\t",end='')
            print()
        print("}\n")

    def mem(memory, name):
        print(f"{name}","{\n") # \n = newline
        rows = len(memory) >> 3 # x >> 3 == x/2**3 == x/8
        rows_bitlen = rows.bit_length()
        print(f"{' '*rows_bitlen}\t0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity -- Added {' '*rows_bitlen} incase of large caches messing stuff up
        for r in range(rows):
            try:
                print(f"0x{(r*16):0{rows_bitlen >> 1}x}\t{' '.join(list(memory.values())[r*8:(r+1)*8])}") # \f = form feed, \t = tab

            except KeyError:
                0
        print("}\n")

#----[Replacement Algorithms]----#

def lru(cache, way, entry): # Least Recently Used
    target_way = cache[way]
    target_way['addr'].insert(0, target_way['addr'].pop(entry['addr'])) # Remove entry_address[-1] and insert into position [0], i.e. remove least recent and move into most recent
    target_way['data'].insert(0, target_way['data'].pop(entry['data'])) # Remove entry_data[-1] and insert into position [0], i.e. remove least recent and move into most recent
    return target_way

def lfu(cache, way, entry): # least frequently used
    return 0

def plru(cache, way, entry): # pseudo-lru
    return 0

#----[]----#

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



class s16: # I need to find a way to incorporate the cycle cost of each instruction... eventually
    # "i16..." -> 16-bit instruction / also fixes built-in function clashes
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

# class control:
    """
    [Aim]: To decode, schedule, clock, interupts and monitor all "in-flight" operations

    [Varables/Objects?]: count/program_counter, clock, instruction_decode, ...
    """

class generate_memory:
    """
    [Aim]: To generate the various memory structures in a dynamic way which allows
    a lot of testing and debugging.

    [varables/Objects?]: capacity=x/direct_memory, capacity=x/ways=y/algorithm=z/cache_memory
    """

    # call variables

    def __init__(self, page_size):
        self.page_size = page_size # I like to call cachelines pages >:D

    def cache(self, byte_capacity, ways, replacement_algorithm):
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
        if ways < 2: # Other functions require, at least, a 'way_0' key to access the data inside a cache
            cache['way_0'] = {'tag': [], 'data': []}
            for a in range(total_tag_count): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                cache['way_0']['tag'].insert(0, '0000')
                cache['way_0']['data'].insert(0, {f"{offset:0{self.page_size.bit_length()-4}x}": '0000' for offset in range(self.page_size)})
        else:
            for w in range(ways): # ways, as in, x-way set-associative
                cache[f'way_{w:x}'] = {'tag': [], 'data': []}
                for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                    cache[f"way_{w:x}"]['tag'].insert(0, '0000')
                    cache[f"way_{w:x}"]['data'].insert(0, {f"{offset:0{self.page_size.bit_length()-4}x}": '0000' for offset in range(self.page_size)})
        return cache # cache['way_x']['tag'/'data']


    def memory(self, byte_capacity):
        address_count = byte_capacity >> 1
        memory = {}
        for a in range(address_count): # building the memory
            memory[f"{a:0{address_count.bit_length()-4}x}"] = '0000' # Hex formatting -- address_count.bit_length()-4 == log2(x)-4
        return memory

    def reorder_buffer():
        0
    def memory_buffer():
        0

class read: # Memory(simple dict look-up) read/write functions seem unnecessary but it should make the moce more readable

    def memory(memory, address):
        return memory[address]

    def cache(cache, main_memory, address, data): # upon a "miss", data must be reteived from main memory
        # < split address into (set,tag) >
        # < search set >
        # entry = {'addr': address, 'data': data}
        # < if entry['addr'] in cache['way']: >
        # <     read cache['way']['address'] >
        # <     cache['replacement_algorithm'](cache, cache['way']. entry) # lru(cache, way, entry)

        updated_cache = {}
        return updated_cache

class write:

    def memory(memory, address, data):
        memory[address] = data # Modifies 'memory' in situ, thus no need to return a value

    def cache(cache, main_memory, hex_address, data): # upon a "miss", data must be reteived from main memory
        ways = len(cache)
        ways_log2 = ways.bit_length()
        offset = len(cache['way_0']['data'][0]) # All caches are generated with at least one way, or set: 'way_0'
        offset_log2 = offset.bit_length()
        binary_address = bin(int(hex_address, 16))[ways_log2:-offset_log2]
        print('binary_address: ', binary_address)
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

# [Variables]: instruction, sub_operation(s), source(s), sink(s/destination). Possibly debugging variables

# [Info]
# Maximum packet side

# """



#----Testing----#
mem = generate_memory(16) # page_size=16
gp_registers = mem.memory(64)
l1_data_cache = mem.cache(64, 2, lru)
main_mem = mem.memory(256)

write.memory(gp_registers, '0000', 'ffff')
write.memory(gp_registers, '000f', 'f0f0')
write.memory(main_mem, '000e', '0fe0')
# print(read.memory(gp_registers, '0f'))
print(main_mem)
pprint.mem(gp_registers, 'GPR')
pprint.mem(main_mem, 'RAM')
# pprint.cache_horiz(l1_data_cache, 'L1 Cache')
# pprint.cache_vert(l1_data_cache, 'L1 Cache')

read.cache
