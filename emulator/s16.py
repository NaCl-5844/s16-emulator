#!/usr/bin/env python
# import math

##----[Notes]----##

# s16 = Simple 16
# Page = Block of 32 Bytes = (16-bits*16)/8 -- I'm allowing this to be modifiable
# Cache:
#   - https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
#   - https://www.geeksforgeeks.org/write-through-and-write-back-in-cache



#----[Custom Exceptions]----#

class CacheCapacityError(ValueError):
    pass




#----[Custom Pretty Print class]----#

class pprint: # May reverse printing order, for now I'm happy with just displaying addresses

    def memory(memory, name):
        print(f"{name}","{\n\n","\t0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity
        rows_per_page = len(memory['page_0']) % 8
        if rows_per_page <= 1:
            for page in memory:
                print(f"{page.replace('age_', ':')}\t{' '.join(list(memory[page].values()))}")
        else:
            print('Page sizes >8 are yet to be implemented')
        print("}\n")

    def cache_horiz(cache, name):
        print(f"{name}","{\n\n","\ttag\t\b\b\b0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity
        for way in cache:
            print(way.replace('ay_', ':'), end='')
            for t in range(len(cache[way]['tag'])):
                print(f"\t{cache[way]['tag'][t]} {' '.join(list(cache[way]['data'][t].values()))}")
        print("}\n")

    # def cache_vert(cache, name): # Breaks when a given way has multiple pages
    #     columns = range(len(cache))
    #     print(f"{name}","{\n") # Title
    #     for x_axis_ways in columns: # Display "ways", or sets, along the x axis in a table format
    #         print(f"\tw{x_axis_ways}", end='')
    #     print()
    #     for x_axis_tags in cache:  # Display "tags", along the x axis in a table format
    #         print(f"\t{cache[x_axis_tags]['tag'][0]}", end='')
    #     print("\n")
    #     for offset, data in enumerate(cache['way_0']['data'][0]): # A page's offset is the fine-grain address to access a given word(s16 -> 16-bit -> 2 bytes)
    #         print(hex(offset),"\t", end='')
    #         for pages in range(len(cache['way_0']['data'])): # Pages/blocks/cachelines are blocks of data which increaces the efficientcy of data movement
    #             for ways in columns: # or sets -- x-way set-associative
    #                 print(cache[f"way_{ways}"]['data'][pages][f"{offset:x}"],"\t",end='')
    #         print()
    #     print("}\n")



#----[Replacement Algorithms]----#

def lru(cache, way, entry): # Least Recently Used
    # Must return replaced_page to be written back to main_memory
    # replaced_address can be generated from: tag|current_way
    target_way = cache[way]
    target_way['tag'].insert(0, target_way['tag'].pop(entry['tag'])) # Remove [-1] and insert into position [0], i.e. remove least recent and move into most recent
    target_way['dirty'].insert(0, target_way['dirty'].pop(entry['dirty']))
    target_way['data'].insert(0, target_way['data'].pop(entry['data']))

def lfu(cache, way, entry): # least frequently used
    return 0

def plru(cache, way, entry): # pseudo-lru
    return 0


# class control:
    """
    [Aim]: To decode, schedule, clock, interupts and monitor all "in-flight" operations

    [Varables/Objects?]: count/program_counter, clock, instruction_decode, ...
    """

#----[Initialisation]----#

class Generate:
    """
    [Aim]: To generate the various memory structures in a dynamic way which allows
    a lot of testing and debugging.

    [varables/Objects?]: capacity=x/direct_memory, capacity=x/ways=y/algorithm=z/cache_memory
    """

    # call variables

    def __init__(self, page_size): # Size in bytes
        self.PAGE_SIZE = page_size # I like to call cachelines pages >:D

    # I need to implement a dirty bit. >_>
    def cache(self, byte_capacity, ways, replacement_algorithm): # https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
        cache = {} # cache decoding: way | tag | offset
        PAGE_SIZE = self.PAGE_SIZE
        total_tag_count = int(byte_capacity / PAGE_SIZE) # minimum byte_capacity == ways*PAGE_SIZE
        tags_per_way = int(total_tag_count / ways)
        # print('ttc: ',total_tag_count, 'tpw: ', tags_per_way) # [ debug ]
        if tags_per_way == 0:
            raise CacheCapacityError(f"Insufficient <byte_capacity> for the number of <ways>\nMinimum <byte_capacity> == ways*PAGE_SIZE = {ways*PAGE_SIZE}")
        if ways < 2: # Other functions require, at least, a 'way_0' key to access the data inside a cache
            cache['way_0'] = {'tag': [], 'dirty':[], 'data': []}
            for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                cache['way_0']['tag'].insert(0, '0000') # Need to implement variable tag size
                cache['way_0']['dirty'].insert(0, 0) # https://en.wikipedia.org/wiki/Dirty_bit
                cache['way_0']['data'].insert(0, {f"{offset<<1:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # {offset... ~ int -> hex. bit_length() ~ log2
        else:
            for w in range(ways): # ways, as in, x-way set-associative
                way_key = f"way_{w:x}" # way_{hex(w)}
                cache[way_key] = {'tag': [], 'dirty':[], 'data': []}
                for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                    cache[way_key]['tag'].insert(0, '0000') # Need to implement variable tag size
                    cache[way_key]['dirty'].insert(0, 0) # https://en.wikipedia.org/wiki/Dirty_bit
                    cache[way_key]['data'].insert(0, {f"{offset<<1:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # {offset... ~ int -> hex. bit_length() ~ log2
        return cache # cache['way_x']['tag'/'data']s

    def memory(self, byte_capacity):
        PAGE_SIZE = self.PAGE_SIZE
        pages = int(byte_capacity / PAGE_SIZE) # Page -> [data, mapped, into, one, address]
        memory = {}
        for p in range(pages): # building the memory
            memory[f"page_{p:0x}"] = {}
            for offset in range(PAGE_SIZE >> 1): # Offset -> Address of data within a page -- page[int(x)] = y_data
                memory[f"page_{p:0x}"][f"{offset<<1:0x}"] = '0000' # Hex formatting -- pages.bit_length()-4 == log2(x)-4
        return memory

    def reorder_buffer():
        0
    def memory_buffer():
        0



#---[Input/Output]----#

class read: # Need to adjust the decoding to account for 16-bit words. CUrrently I decode as if my word size =

    def memory(memory, address):
        offset_bits = len(memory['page_0']).bit_length() # Any memory must have at least page_0
        bin_address = f"{int(address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
        offset = int(bin_address[15-(offset_bits):15], 2) # Extracting the upper most bits of the address
        page = int(bin_address[0:-(offset_bits+1)], 2) # The remaining bits address the page
        print('\b, offset_bits: ' ,offset_bits,'bin_address: ',bin_address)   # [ debug ]
        print('page: ', page,'offset: ', offset)                              # [ debug ]
        return memory[f"page_{page:0x}"][f"{offset:0x}"]

    def cache(cache, main_memory, address): # upon a "miss", data must be reteived from main memory
        """
        HIT:
        > IF ( address_tag in cache['address_way']['tag'] ) AND ( cache['address_way']['tag'].index(address_tag) == cache['address_way']['dirty'][cache['address_way']['tag'].index(address_tag)] )
        """
        # Splitting address -> tag|way|offset
        way_bits = len(cache).bit_length()-1
        offset_bits = len(cache['way_0']['data'][0]).bit_length() # All caches are generated with at least one way, or set: 'way_0'
        bin_address = f"{int(address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
        way = int(bin_address[way_bits:15-(offset_bits+1)], 2)
        way_key = f"way_{way:x}"
        tag = f"{int(bin_address[way_bits:-(offset_bits+1)], 2):0{4}x}"
        offset = int(bin_address[15-(offset_bits):15], 2) # Extracting the upper most bits of the address
        print('way_bits:',way_bits,'offset_bits:',offset_bits,'bin_address:',bin_address)   # [ debug ]
        print('way:', way,'tag:', tag,'offset: ', offset)                                   # [ debug ]

        # Searcing for a read_hit

        if tag in cache[way_key]['tag']: # wayyyyyyyyy more readable
            tag_index = cache[way_key]['tag'].index(tag)
            dirty_bit = cache[way_key]['dirty'][tag_index]
            if dirty_bit == 0:
                print('hit')
                return 'hit', cache[way_key]['data'][tag_index][f"{offset:0x}"]
            else: # fetch newest version -- i_cache's may need to look inside d_cache for newest data
                print('dirty hit... Finding last modified page')
                # with just 1 level of caching, only direct accesses to main_memory will cause a page to become dirty
                # This could possibly happen if a DMA(Direct Memory Access) is implemented. Unlikely, maybe in T16.
        else:
            print('miss')
            page = int(bin_address[0:-(offset_bits+1)], 2) # The remaining bits address the page
            data = main_memory[f"page_{page:0x}"][f"{offset:0x}"]
            return 'miss', data



        """
        The function must be able to return data to main memory as well as the cache:

        write.cache()  ::HIT?   -> read from existing_entry
                        :MISS?  -> find old_entry to evict -> send old_entry to main_memory -> pull addressed_entry from main_memory to cache -> write to entry
        """


class write: # Need to adjust the decoding to account for 16-bit words. CUrrently I decode as if my word size = 8

    def memory(memory, address, data):
        offset_bits = len(memory['page_0']).bit_length() # Any memory must have at least page_0
        bin_address = f"{int(address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
        offset = int(bin_address[15-(offset_bits):15], 2) # Extracting the upper most bits of the address
        page = int(bin_address[0:-(offset_bits+1)], 2) # The remaining bits address the page
        # print('\b, offset_bits: ' ,offset_bits,'bin_address: ',bin_address)   # [ debug ]
        # print('page: ', page,'offset: ', offset)                              # [ debug ]
        memory[f"page_{page:0x}"][f"{offset:0x}"] = data


    def cache(cache, main_memory, address, data): # upon a "miss", data must be reteived from main memory
        way_bits = len(cache).bit_length()-1
        offset_bits = len(cache['way_0']['data'][0]).bit_length() # All caches are generated with at least one way, or set: 'way_0'
        bin_address = f"{int(address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
        way = int(bin_address[way_bits:15-(offset_bits+1)], 2)
        way_key = f"way_{way:x}"
        tag = f"{int(bin_address[way_bits:-(offset_bits+1)], 2):0{4}x}"
        offset = int(bin_address[15-(offset_bits):15], 2) # Extracting the upper most bits of the address
        print('way_bits:',way_bits,'offset_bits:',offset_bits,'bin_address:',bin_address)   # [ debug ]
        print('way:', way,'tag:', tag,'offset: ', offset)                                   # [ debug ]

        # Searcing for a read_hit

        if tag in cache[way_key]['tag']: # wayyyyyyyyy more readable
            tag_index = cache[way_key]['tag'].index(tag)
            dirty_bit = cache[way_key]['dirty'][tag_index]
            if dirty_bit == 0:
                print('hit')
                cache[way_key]['data'][tag_index][f"{offset:0x}"] = data
                return 'hit',
            else: # fetch newest version -- i_cache's may need to look inside d_cache for newest data
                print('dirty hit... Finding last modified page')
                # with just 1 level of caching, only direct accesses to main_memory will cause a page to become dirty
                # This could possibly happen if a DMA(Direct Memory Access) is implemented. Unlikely, maybe in T16.
        else:
            print('miss')
            page = int(bin_address[0:-(offset_bits+1)], 2) # The remaining bits address the page
            data = main_memory[f"page_{page:0x}"][f"{offset:0x}"]
            # <cache write>
            return 'miss', data

        """
        The function must be able to return data to main memory as well as the cache:

        write.cache()  ::HIT?   -> write to existing_entry
                        :MISS?  -> find old_entry to evict -> send old_entry to main_memory -> pull addressed_entry from main_memory to cache -> write to entry
        """

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
GenerateMemory = Generate(16) # page_size=16 Bytes -> 8*2 Byte words -> 2B = 16-bits
gp_registers = GenerateMemory.memory(64)
l1_data_cache = GenerateMemory.cache(128, 4, lru)
main_mem = GenerateMemory.memory(512)

# print(gp_registers)
# print(main_mem)
# print()
# print(l1_data_cache)
# pprint.memory(gp_registers, 'GPR')
# pprint.cache_vert(l1_data_cache, 'L1 Cache') # Needs work >_>
pprint.memory(main_mem, 'RAM')
write.memory(main_mem, '0090', '0fe0')
# pprint.memory(main_mem, 'RAM')
print(read.memory(main_mem, '0090'))
pprint.cache_horiz(l1_data_cache, 'L1 Cache')
print(read.cache(l1_data_cache, main_mem, '0090'))



























#----[I'm amazed how long it will be before I implement operations >_>]----#

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

