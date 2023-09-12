#!/usr/bin/env python
from customExceptions import *
import replacement
import decode
import tprint


##----[Notes]----##

# s16 = Simple 16
# Page = Block of 32 Bytes = (16-bits*16)/8 -- I'm allowing this to be modifiable
# Cache:
#   - https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
#   - https://www.geeksforgeeks.org/write-through-and-write-back-in-cache
# Adding date and time to a file:
#   - https://www.geeksforgeeks.org/how-to-create-filename-containing-date-or-time-in-python/

# BUG LIST:
#


# TODO LIST:
# Generate cache structures from the hierarchy dictornary !!!


#----[Initialisation]----#

class Generate:

    @classmethod # basically a function without access to the object and its internals
    def config(Generate, config_name :str):
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

    @classmethod
    def memory_hierarchy(Generate, config):
        hierarchy = {}

        #ROM
        rom_file = config.get('ROM_FILE_NAME')
        print(rom_file[-4:])
        if rom_file[-4:] == '.s16':
            hierarchy['rom'] = {
                'file': rom_file,
                'start_address': config.get('ROM_START_ADDRESS')}

        #RAM/Main Memory
        hierarchy['main'] = {
            'size': config.get('MAIN_MEMORY_SIZE'),
            'start_address': config.get('MAIN_START_ADDRESS')}


        #Cache
        if config.get('L1_CACHE') == True:
            hierarchy['L1'] = {
                'data': {'size': config.get('L1_DATA_CACHE_SIZE'),
                            'ways': config.get('L1_DATA_CACHE_WAYS'),
                            'cost': config.get('L1_DATA_CACHE_COST'),
                            'repl': config.get('L1_DATA_CACHE_REPL')},
                'inst': {'size': config.get('L1_INST_CACHE_SIZE'),
                            'ways': config.get('L1_INST_CACHE_WAYS'),
                            'cost': config.get('L1_INST_CACHE_COST'),
                            'repl': config.get('L1_INST_CACHE_REPL')}}
            if None in hierarchy['L1']['data'].values() or None in hierarchy['L1']['inst'].values():
                hierarchy.pop('L1')
        if config.get('L2_CACHE') == True:
            hierarchy['L2'] = {
                'data': {'size': config.get('L2_CACHE_SIZE'),
                         'ways': config.get('L2_CACHE_WAYS'),
                         'cost': config.get('L2_CACHE_COST')}}
            if None in hierarchy['L2']['data'].values():
                hierarchy.pop('L2')
        print(hierarchy)
        return hierarchy

    @classmethod ### Not sure I need this due to PAGE_SIZE being inside config
    def page_size(Generate, config):
        PAGE_SIZE = config.get('PAGE_SIZE')
        if PAGE_SIZE != 16: # HARDCODED
            raise ConfigError
        else:
            return PAGE_SIZE

    @classmethod
    def cache(Generate, config, memory_type):
        # https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
        cache = {} # cache decoding: way | tag | offset
        WAYS = config.get(f"{memory_type}_CACHE_WAYS")
        PAGE_SIZE = config.get('PAGE_SIZE')
        BYTE_CAPACITY = config.get(f"{memory_type}_CACHE_SIZE")
        tag_count = int(BYTE_CAPACITY / PAGE_SIZE) # minimum BYTE_CAPACITY == WAYS*PAGE_SIZE
        tags_per_way = int(tag_count / WAYS)
        replacement_algorithm = config.get(f"{memory_type}_CACHE_REPL")
        cache['algorithm'] = eval(f"replacement.{replacement_algorithm}")
        # print('tc: ',tag_count, 'tpw: ', tags_per_way) # [ debug ]
        if tags_per_way == 0:
            raise CacheCapacityError(f"Insufficient <BYTE_CAPACITY> for the number of <WAYS>\nMinimum <BYTE_CAPACITY> == WAYS*PAGE_SIZE = {WAYS*PAGE_SIZE}")
        if WAYS < 2: # Other functions require, at least, a 'way_0' key to access the data inside a cache
            cache['way_0'] = {'tag': [], 'dirty':[], 'data': []}
            for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                cache['way_0']['tag'].insert(0, '0000') # Need to implement variable tag size
                cache['way_0']['data'].insert(0, {f"{offset<<1:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # bit_length() ~ log2
                cache['way_0']['dirty'].insert(0, 0) # https://en.wikipedia.org/wiki/Dirty_bit
        else:
            for w in range(WAYS): # WAYS, as in, x-way set-associative
                way_key = f"way_{w:x}" # way_{hex(w)}
                cache[way_key] = {'tag': [], 'dirty':[], 'data': []}
                for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                    cache[way_key]['tag'].insert(0, '0000') # Need to implement variable tag size
                    cache[way_key]['data'].insert(0, {f"{offset<<1:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # bit_length() ~ log2
                    cache[way_key]['dirty'].insert(0, 0) # https://en.wikipedia.org/wiki/Dirty_bit
        return cache # cache['way_x']['tag'/'data']

    @classmethod
    def memory(Generate, config, memory_type):
        PAGE_SIZE = config.get("PAGE_SIZE")
        if memory_type == 'ROM':
            START_ADDRESS = int(config.get('ROM_START_ADDRESS'), 16)
            BYTE_CAPACITY = int(config.get('MAIN_START_ADDRESS'), 16) - START_ADDRESS
            if BYTE_CAPACITY <= 0: ### BUG: ROM address-space cannot be above RAM's address-space
                raise ConfigError('Custom start addresses not yet supported\n -- ROM_START_ADDRESS must equal 0x0.')
        else:
            START_ADDRESS = int(config.get('MAIN_START_ADDRESS'), 16)
            BYTE_CAPACITY = config.get(f"{memory_type}_MEMORY_SIZE")
        memory = {}
        pages = int(BYTE_CAPACITY / PAGE_SIZE) # Page -> [a, group, of, data, mapped, to, one, address]
        starting_page = int(START_ADDRESS / PAGE_SIZE)
        for p in range(starting_page, starting_page + pages): # building the memory
            memory[f"page_{p:0x}"] = {}
            for offset in range(PAGE_SIZE >> 1): # Offset -> Address of data within a page
                memory[f"page_{p:0x}"][f"{offset<<1:0x}"] = '0000' # Hex formatting -- pages.bit_length()-4 == log2(x)-4
        return memory

    @classmethod
    def reorder_buffer():
        pass

    @classmethod
    def memory_buffer():
        pass

    def __init__(self, config_name): # Size in bytes
    # I need to generate an instance or something of "s16" - which plops out the fully generated spec
    # this may help:
    # https://stackoverflow.com/questions/24253761/how-do-you-call-an-instance-of-a-class-in-python

        self.config = Generate.config(config_name) # Take s16.conf key-values and place in dictionary
        print(self.config)
        self.PAGE_SIZE = Generate.page_size(self.config) # Hardcoded to 16 Bytes. # If Gen
        self.gpr_memory = Generate.memory(self.config, 'GPR')

        # when generating Main memory(aka s16's RAM) the starting/ending address must be taken into account
        # to properly address any extra memory, such as ROM and Ports
        # E.g. ROM addresses start and 0x0000 and end at 0x00ff, then RAM starts at 0x0100.

        self.main_memory = Generate.memory(self.config, 'MAIN')
        self.rom = Generate.memory(self.config, 'ROM')
        self.memory_hierarchy = Generate.memory_hierarchy(self.config) # will be used to generate memory structures correctly
        if 'L1' in self.memory_hierarchy:
            self.l1_data_cache = Generate.cache(self.config, 'L1_DATA')
            self.l1_inst_cache = Generate.cache(self.config, 'L1_INST')
        if 'L2' in self.memory_hierarchy:
            self.l2_cache = Generate.cache(self.config, 'L2')



class read:

    def memory(memory, address):
        offset_bits = len(memory['page_0']).bit_length() # Any memory must have at least page_0
        page_key = decode.page(address, offset_bits)
        if page_key in memory:
            return memory[page_key]
        else:
            min_address = list(memory.keys())[0][5:]
            max_address = list(memory.keys())[-1][5:]
            raise OutOfBoundAddress(f"Page 0x{page:0x} out-of-bound, page range = 0x{min_address} - 0x{max_address}")

    def cache(cache, main_memory, address): # upon a "miss", data must be reteived from main_memory
        way_bits = (len(cache)-1).bit_length()
        offset_bits = len(cache['way_0']['data'][0]).bit_length() # All caches are generated with at least one way, or set: 'way_0'
        bin_address, way_key = decode.way(address, way_bits, offset_bits) # decodes address into TAG|WAY|OFFSET
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


class write: # write.<function> modify by reference

    def memory(memory, address, entry):
        offset_bits = len(memory['page_0']).bit_length() # Any memory must have at least page_0
        page_key = decode.page(address, offset_bits)
        if page_key in memory:
            memory[page_key] = entry
        else:
            min_address = list(memory.keys())[0][5:]
            max_address = list(memory.keys())[-1][5:]
            raise OutOfBoundAddress(f"Page 0x{page:0x} out-of-bound, page range = 0x{min_address} - 0x{max_address}")

    def cache(cache, main_memory, address, data): # upon a "miss", data must be retrieved from main memory # Splitting address -> tag|way|offset
        way_bits = (len(cache)-1).bit_length()
        offset_bits = len(cache['way_0']['data'][0]).bit_length() # All caches are generated with at least one way, or set: 'way_0'
        bin_address, way_key = decode.way(address, way_bits, offset_bits) # decodes address into TAG|WAY|OFFSET
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
            page_key = decode.page(address, offset_bits)
            if page_key in memory: # If address is valid
                page[f"{offset:0x}"] = data # data written to the incoming page
                new_entry = {'tag': tag, 'dirty': 0, 'data': page} # collecting components which make up an entry
                cache['algorithm'](cache, way_key, new_entry) # sending the entry to the replacement algorithm
            else: # Address out-of-range -- Raise error
                min_address = list(memory.keys())[0][5:]
                max_address = list(memory.keys())[-1][5:]
                raise OutOfBoundAddress(f"Page 0x{page:0x} out-of-bound, page range = 0x{min_address} - 0x{max_address}")



    # def components(self):
    #     if 'L1' in self.memory_hierarchy:
    #         print('hi')
    #         l1_data = self.memory_hierarchy['L1']['data']
    #         self.l1_data_cache = Generate.cache(l1_data['size'], l1_data['ways'], l1_data['repl'])


#---[Input/Output]----#


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
s16 = Generate('s16.conf') # page_size=16 Bytes -> 8*2 Byte words -> 2B = 16-bits
tprint.memory(s16.gpr_memory, 'gpr')
tprint.memory(s16.rom, 'rom')
tprint.memory(s16.main_memory, 'main')
tprint.cache_horiz(s16.l1_data_cache, 'l1d')

# tprint.cache_vert(l1_data_cache, 'L1 Cache') # Needs work >_>

# print(gp_registers)
# print(main_mem)
# print()
# print(l1_data_cache)
# tprint.memory(gp_registers, 'GPR')
# tprint.memory(main_mem, 'RAM')
#
# # pages of data:
# write.memory(main_mem, '0027', {'0': 'ffff', '2': '0000', '4': '0000', '6': '0000', '8': '0000', 'a': '0000', 'c': '0000', 'e': '0000'})
# write.memory(main_mem, '0017', {'0': 'abcd', '2': 'ffff', '4': '0000', '6': '0000', '8': '0000', 'a': '0000', 'c': '0000', 'e': '0000'})
# write.memory(main_mem, '0004', {'0': '0000', '2': '0000', '4': 'ffff', '6': '0000', '8': '0000', 'a': '0000', 'c': '0000', 'e': '0000'})
#
#
# tprint.memory(main_mem, 'RAM')
# print(read.memory(main_mem, '0027'))
# print(read.memory(main_mem, '0017'))
# tprint.cache_horiz(l1_data_cache, 'L1 Cache')
# print(read.cache(l1_data_cache, main_mem, '0090'))
# write.cache(l1_data_cache, main_mem, '0017', '0fe0')
# write.cache(l1_data_cache, main_mem, '0004', '0ca0')
# tprint.memory(main_mem, 'RAM')
# print(read.cache(l1_data_cache, main_mem, '0027'))
# print(read.cache(l1_data_cache, main_mem, '0014'))
# tprint.cache_horiz(l1_data_cache, 'L1 Cache')



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


def main():
    # Initialise s16 dictonary(?) structure
    # loop<generate memory>:
    #   read hierarchy
    #   generate component
    #   place component -> s16
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    pass
