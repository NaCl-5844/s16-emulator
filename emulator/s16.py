#!/usr/bin/env python
# import math

##----[Notes]----##

# s16 = Simple 16
# Page = Block of 32 Bytes = (16-bits*16)/8 -- I'm allowing this to be modifiable
# Cache:
#   - https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
#   - https://www.geeksforgeeks.org/write-through-and-write-back-in-cache

# BUG LIST:
#



#----[Custom Exceptions]----#

class CacheCapacityError(ValueError):
    pass
class OutOfBoundAddress(KeyError):
    pass
class ConfigError(ValueError):
    pass

#----[Custom Pretty Print class]----#

class pprint: # May reverse printing order, for now I'm happy with just displaying addresses

    def memory(memory, name):
        print(f"{name}","{\n\n\t0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity
        rows_per_page = len(memory['page_0']) % 8
        if rows_per_page <= 1:
            for page in memory:
                print(f"{page.replace('age_', ':')}\t{' '.join(list(memory[page].values()))}")
        else:
            print('Page sizes >8 are yet to be implemented')
        print("}\n")

    def cache_horiz(cache, name):
        print(f"{name}","{\n\n","\ttag\t\b\b\b0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity
        replacement_algorithm = cache.pop('algorithm') # Not sure how else to get around this
        for way in cache:
            print(way.replace('ay_', ':'), end='')
            for t in range(len(cache[way]['tag'])):
                print(f"\t{cache[way]['tag'][t]} {' '.join(list(cache[way]['data'][t].values()))}")
        print("}\n")
        cache['algorithm'] = replacement_algorithm


#----[Replacement Algorithms]----#

def lru(cache, way, new_entry): # Least Recently Used
    lru_dirty_bit = cache[way]['dirty'][-1]
    print('\n#----[lru]----#\nlru page dirty?', bool(lru_dirty_bit))    # [ debug ]
    print('\ntarget_way:', cache[way],'\nNew Entry:', new_entry)        # [ debug ]
    cache[way]['tag'].insert(0, cache[way]['tag'].pop(-1)) # remove least recent, [-1], and move into most recent, [0]
    cache[way]['data'].insert(0, cache[way]['data'].pop(-1))
    cache[way]['dirty'].insert(0, cache[way]['dirty'].pop(-1))
    if lru_dirty_bit == 0: # clean
        cache[way]['tag'][0] = new_entry['tag']
        cache[way]['data'][0] = new_entry['data']
        cache[way]['dirty'][0] = new_entry['dirty']
    else: # dirty
        # only cases I can see is between l1_data_cache and a l1_instr_cache
        # I'd also need to maintain a hierarchy of the cache levels somehow'
        pass


def lfu(cache, way, new_entry): # least frequently used
    return 0

def plru(cache, way, new_entry): # pseudo-lru
    return 0


#----[Initialisation]----#

class Generate:


    def load_config(config_name :str):
        with open(config_name, "r") as s16_config:
            config = {}
            for line in s16_config:
                clean_line = line.strip() # Clean up line
                if clean_line == '' or clean_line[0] == '[' or clean_line[0] == '#' or clean_line[0] == '\\': # jump to start if...
                    continue # '\\' -> \, is the first character of *newline* -> \n
                key_value_pair = clean_line.split(' = ')
                if len(key_value_pair) == 1: # jump to start if no value provided{len(key+value)==2}
                    continue
                try:
                    config[key_value_pair[0]] = int(key_value_pair[1])
                except ValueError:
                    if key_value_pair[1] == 'True':
                        config[key_value_pair[0]] = True
                    elif key_value_pair[1] == 'False':
                        config[key_value_pair[0]] = False
                    else:
                        config[key_value_pair[0]] = str(key_value_pair[1]) # catch-all, sanitises any dubious entries
            return config

    def get_config(key :str):
        value = config.get(key)
        if value == None:
            raise ConfigError
        else:
            return value

    def __init__(self, config_name): # Size in bytes
        self.config = load_config(config_name)
        self.memory_hierarchy = {'l1_data': 0, 'l1_instr': 0, 'main_memory': 0}

    def cache(self, byte_capacity, ways, replacement_algorithm): # https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
        cache = {} # cache decoding: way | tag | offset
        PAGE_SIZE = self.PAGE_SIZE
        tag_count = int(byte_capacity / PAGE_SIZE) # minimum byte_capacity == ways*PAGE_SIZE
        tags_per_way = int(tag_count / ways)
        cache['algorithm'] = replacement_algorithm
        # print('ttc: ',tag_count, 'tpw: ', tags_per_way) # [ debug ]
        if tags_per_way == 0:
            raise CacheCapacityError(f"Insufficient <byte_capacity> for the number of <ways>\nMinimum <byte_capacity> == ways*PAGE_SIZE = {ways*PAGE_SIZE}")
        if ways < 2: # Other functions require, at least, a 'way_0' key to access the data inside a cache
            cache['way_0'] = {'tag': [], 'dirty':[], 'data': []}
            for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                cache['way_0']['tag'].insert(0, '0000') # Need to implement variable tag size
                cache['way_0']['data'].insert(0, {f"{offset<<1:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # bit_length() ~ log2
                cache['way_0']['dirty'].insert(0, 0) # https://en.wikipedia.org/wiki/Dirty_bit
        else:
            for w in range(ways): # ways, as in, x-way set-associative
                way_key = f"way_{w:x}" # way_{hex(w)}
                cache[way_key] = {'tag': [], 'dirty':[], 'data': []}
                for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                    cache[way_key]['tag'].insert(0, '0000') # Need to implement variable tag size
                    cache[way_key]['data'].insert(0, {f"{offset<<1:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # bit_length() ~ log2
                    cache[way_key]['dirty'].insert(0, 0) # https://en.wikipedia.org/wiki/Dirty_bit
        return cache # cache['way_x']['tag'/'data']

    def memory(self, byte_capacity):
        PAGE_SIZE = self.PAGE_SIZE
        memory = {}
        pages = int(byte_capacity / PAGE_SIZE) # Page -> [a, group, of, data, mapped, to, one, address]
        for p in range(pages): # building the memory
            memory[f"page_{p:0x}"] = {}
            for offset in range(PAGE_SIZE >> 1): # Offset -> Address of data within a page -- page[int(x)] = data
                memory[f"page_{p:0x}"][f"{offset<<1:0x}"] = '0000' # Hex formatting -- pages.bit_length()-4 == log2(x)-4
        return memory

    def reorder_buffer():
        0
    def memory_buffer():
        0





#---[Input/Output]----#

class Decode: # I'll use this class to make my read/write methods easier to read

    @classmethod # basically a function without access to the object and its internals
    def page(Decode, hex_address, offset_bits):
        bin_address = f"{int(hex_address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
        page = int(bin_address[0:-(offset_bits)], 2) # The remaining bits address the page
        print('\n#----[Read.memory]----#\n','offset_bits: ',offset_bits)    # [ debug ]
        print('bin_address: ',bin_address,'page:',page)                     # [ debug ]
        page_key = f"page_{page:0x}"
        return page_key


    @classmethod # basically a function without access to the object and its internals
    def way(Decode, hex_address, way_bits, offset_bits):
        bin_address = f"{int(hex_address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
        way = bin_address[-(way_bits+offset_bits-1):-offset_bits]
        way_key = f"way_{int(way, 2):x}"
        print('\n#----[Read.cache]----#\n','\bway_bits:',way_bits-1,'offset_bits:',offset_bits) # [ debug ]
        print(f"bin_address: 0b{bin_address}, way: 0b{way}")                                    # [ debug ]
        return bin_address, way_key

class read(Decode):

    def memory(memory, address):
        offset_bits = len(memory['page_0']).bit_length() # Any memory must have at least page_0
        page_key = Decode.page(address, offset_bits)
        if page_key in memory:
            return memory[page_key]
        else:
            min_address = list(memory.keys())[0][5:]
            max_address = list(memory.keys())[-1][5:]
            raise OutOfBoundAddress(f"Page 0x{page:0x} out-of-bound, page range = 0x{min_address} - 0x{max_address}")

    def cache(cache, main_memory, address): # upon a "miss", data must be reteived from main_memory
        way_bits = (len(cache)-1).bit_length()
        offset_bits = len(cache['way_0']['data'][0]).bit_length() # All caches are generated with at least one way, or set: 'way_0'
        bin_address, way_key = Decode.way(address, way_bits, offset_bits) # Decodes address into TAG|WAY|OFFSET
        tag = f"{int(bin_address[way_bits:-(offset_bits+1)], 2):0{4}x}"
        offset = int(bin_address[-(offset_bits):15], 2) << 1 # Extracting the upper most bits of the address
        if tag in cache[way_key]['tag']: # wayyyyyyyyy more readable
            tag_index = cache[way_key]['tag'].index(tag)
            dirty_bit = cache[way_key]['dirty'][tag_index]
            if dirty_bit == 0:
                print('hit')                                                            # [ debug ]
                return cache[way_key]['data'][tag_index][f"{offset:0x}"]
            else: # fetch newest version -- i_cache's may need to look inside d_cache for newest data
                print('dirty hit... Finding last modified page')                        # [ debug ]
                # with just 1 level of caching, these ar the possible conflicts:
                # 1) Direct access to main_memory -- via peripherals?
                # 2) l1_instr page is modified inside l1_data -- the reverse is impossible
        else:
            page_address = int(bin_address[:-(offset_bits)], 2) # The remaining bits address the page
            page = main_memory[f"page_{page_address:0x}"]
            print('miss...retrieving page\npage_address:',page_address,',page:', page)  # [ debug ]
            new_entry = {'tag': tag, 'dirty': 0, 'data': page} # collecting components which make up an entry
            cache['algorithm'](cache, way_key, new_entry) # sending the entry to the replacement algorithm
            tag_index = cache[way_key]['tag'].index(tag)
            return cache[way_key]['data'][tag_index][f"{offset:0x}"]


class write(Decode): # write.<functions> modify by reference

    def memory(memory, address, entry):
        offset_bits = len(memory['page_0']).bit_length() # Any memory must have at least page_0
        page_key = Decode.page(address, offset_bits)
        if page_key in memory:
            memory[page_key] = entry
        else:
            min_address = list(memory.keys())[0][5:]
            max_address = list(memory.keys())[-1][5:]
            raise OutOfBoundAddress(f"Page 0x{page:0x} out-of-bound, page range = 0x{min_address} - 0x{max_address}")

    def cache(cache, main_memory, address, data): # upon a "miss", data must be retrieved from main memory # Splitting address -> tag|way|offset
        way_bits = (len(cache)-1).bit_length()
        offset_bits = len(cache['way_0']['data'][0]).bit_length() # All caches are generated with at least one way, or set: 'way_0'
        bin_address, way_key = Decode.way(address, way_bits, offset_bits) # Decodes address into TAG|WAY|OFFSET
        tag = f"{int(bin_address[way_bits:-(offset_bits+1)], 2):0{4}x}"
        if tag in cache[way_key]['tag']: # Testing for a read_hit
            tag_index = cache[way_key]['tag'].index(tag)
            dirty_bit = cache[way_key]['dirty'][tag_index]
            if dirty_bit == 0: # Clean hit
                print('hit')                                        # [ debug ]
                offset = int(bin_address[-(offset_bits):15], 2) << 1 # Extracting the upper most bits of the address
                cache[way_key]['data'][tag_index][f"{offset:0x}"] = data
            else: # fetch newest version -- i_cache's may need to look inside d_cache for newest data -- Dirty hit
                print('dirty hit... Finding last modified page')    # [ debug ]
                # with just 1 level of caching, only direct accesses to main_memory will cause a page to become dirty
                # This could possibly happen if a DMA(Direct Memory Access) is implemented. Unlikely, maybe in T16.
        else: # Miss
            page_key = Decode.page(address, offset_bits)
            if page_key in memory: # If address is valid
                page[f"{offset:0x}"] = data # data written to the incoming page
                new_entry = {'tag': tag, 'dirty': 0, 'data': page} # collecting components which make up an entry
                cache['algorithm'](cache, way_key, new_entry) # sending the entry to the replacement algorithm
            else: # Address out-of-range -- Raise error
                min_address = list(memory.keys())[0][5:]
                max_address = list(memory.keys())[-1][5:]
                raise OutOfBoundAddress(f"Page 0x{page:0x} out-of-bound, page range = 0x{min_address} - 0x{max_address}")



class Processor: # Class to collect generated components and allow them to interact easily
    pass

# class control:
    """
    [Aim]: To decode, schedule, clock, interupts and monitor all "in-flight" operations

    [Varables/Objects?]: count/program_counter, clock, instruction_decode, ...
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

# pprint.cache_vert(l1_data_cache, 'L1 Cache') # Needs work >_>

# print(gp_registers)
# print(main_mem)
# print()
# print(l1_data_cache)
# pprint.memory(gp_registers, 'GPR')
# pprint.memory(main_mem, 'RAM')

# pages of data:
write.memory(main_mem, '0027', {'0': 'ffff', '2': '0000', '4': '0000', '6': '0000', '8': '0000', 'a': '0000', 'c': '0000', 'e': '0000'})
write.memory(main_mem, '0017', {'0': 'abcd', '2': 'ffff', '4': '0000', '6': '0000', '8': '0000', 'a': '0000', 'c': '0000', 'e': '0000'})
write.memory(main_mem, '0004', {'0': '0000', '2': '0000', '4': 'ffff', '6': '0000', '8': '0000', 'a': '0000', 'c': '0000', 'e': '0000'})


pprint.memory(main_mem, 'RAM')
print(read.memory(main_mem, '0027'))
print(read.memory(main_mem, '0017'))
pprint.cache_horiz(l1_data_cache, 'L1 Cache')
print(read.cache(l1_data_cache, main_mem, '0090'))
write.cache(l1_data_cache, main_mem, '0017', '0fe0')
write.cache(l1_data_cache, main_mem, '0004', '0ca0')
pprint.memory(main_mem, 'RAM')
print(read.cache(l1_data_cache, main_mem, '0027'))
print(read.cache(l1_data_cache, main_mem, '0014'))
pprint.cache_horiz(l1_data_cache, 'L1 Cache')











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
