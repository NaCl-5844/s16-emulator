#!/usr/bin/env python
from customExceptions import *
import os
import collections
import assembler.asm
import instruction
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
# > ROM address-space cannot be above RAM's address-space
# > Only binary file-types can be generted/used (MAY NOT IMPLEMENT BUT ATTACH A BIN -> HEX CONVERTER SCRIPT)
# > Naive page address decoding in class:Read and class:Write
# > Partially filled pages do not get loaded to ROM in Generate.files_to_rom()

# TODO LIST:
# > REFACTOR: read.cache() and write.cache. I've gained more knowledge on flag usage and deques
#           and can simplify the code a bunch. Also update the lru replacemeny function.
# > Make a basic single cycle loop to test the: pc, read, write, l1_inst_cache and instruction.decode




#----[ These should be their own module? or compound them into larger modules? ]----#

class read:

    def memory(memory, address):
        offset_bits = len(list(memory.values())[0]).bit_length() # Any memory must have at least page_0  # BUG: Naive page address decoding
        page_key = decode.page(address, offset_bits)
        if page_key in memory:
            return memory[page_key]
        else:
            min_address = list(memory.keys())[0][5:]
            max_address = list(memory.keys())[-1][5:]
            raise OutOfBoundAddress(f"{page_key} out-of-bound, page range = 0x{min_address} - 0x{max_address}")

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
                page_address = int(bin_address[:-(offset_bits)], 2) # The remaining bits address the page
                page = main_memory[f"page_{page_address:0x}"]
                print('miss...retrieving page\npage_address:',page_address,',page:', page)  # [ debug ]
                new_entry = {'tag': tag, 'dirty': 0, 'data': page} # int(bin_address[0:-(offset_bits)], 2)int(bin_address[0:-(offset_bits)], 2)collecting components which make up an entry
                cache['algorithm'](cache, way_key, new_entry) # sending the entry to the replacement algorithm
                tag_index = cache[way_key]['tag'].index(tag)
                return cache[way_key]['data'][tag_index][f"{offset:0x}"]
        else:
            page_address = int(bin_address[:-(offset_bits)], 2) # The remaining bits address the page
            page = main_memory[f"page_{page_address:0x}"]
            print('miss...retrieving page\npage_address:',page_address,',page:', page)  # [ debug ]
            new_entry = {'tag': tag, 'dirty': 0, 'data': page} # int(bin_address[0:-(offset_bits)], 2)int(bin_address[0:-(offset_bits)], 2)collecting components which make up an entry
            cache['algorithm'](cache, way_key, new_entry) # sending the entry to the replacement algorithm
            tag_index = cache[way_key]['tag'].index(tag)
            return cache[way_key]['data'][tag_index][f"{offset:0x}"]

class write: # write.<function> modify by reference
    def memory(memory, address, entry):
        offset_bits = len(list(memory.values())[0]).bit_length() # Any memory must have at least page_0 # BUG: Naive page address decoding
        page_key = decode.page(address, offset_bits)
        if page_key in memory:
            memory[page_key] = entry
        else:
            min_address = list(memory.keys())[0][5:]
            max_address = list(memory.keys())[-1][5:]
            raise OutOfBoundAddress(f"{page_key} out-of-bound, page range = 0x{min_address} - 0x{max_address}")

    def cache(cache, main_memory, address, data): # upon a "miss", data must be retrieved from main main_memory # Splitting address -> tag|way|offset
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
                cache[way_key]['data'][tag_index][f"{offset:x}"] = data
            else: # fetch newest version -- i_cache's may need to look inside d_cache for newest data -- Dirty hit
                print('dirty hit... Finding last modified page')    # [ debug ]
                # with just 1 level of caching, only direct accesses to main_memory will cause a page to become dirty
                # This could possibly happen if a DMA(Direct Memory Access) is implemented. Unlikely, maybe in T16.
                page_key = decode.page(address, offset_bits)
                if page_key in main_memory: # If address is valid
                    page[f"{offset:0x}"] = data # data written to the incoming page
                    new_entry = {'tag': tag, 'dirty': 0, 'data': page} # collecting components which make up an entry
                    cache['algorithm'](cache, way_key, new_entry) # sending the entry to the replacement algorithm
                else: # Address out-of-range -- Raise error
                    min_address = list(main_memory.keys())[0][5:]
                    max_address = list(main_memory.keys())[-1][5:]
                    raise OutOfBoundAddress(f"Page 0x{page:x} out-of-bound, page range = 0x{min_address} - 0x{max_address}")
        else: # Miss
            page_key = decode.page(address, offset_bits)
            if page_key in main_memory: # If address is valid
                page[f"{offset:0x}"] = data # data written to the incoming page
                new_entry = {'tag': tag, 'dirty': 0, 'data': page} # collecting components which make up an entry
                cache['algorithm'](cache, way_key, new_entry) # sending the entry to the replacement algorithm
            else: # Address out-of-range -- Raise error
                min_address = list(main_memory.keys())[0][5:]
                max_address = list(main_memory.keys())[-1][5:]
                raise OutOfBoundAddress(f"Page 0x{page:x} out-of-bound, page range = 0x{min_address} - 0x{max_address}")

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
                    if key_value_pair[1] == 'True' or key_value_pair[1] == 'False':
                        config[key_value_pair[0]] = eval(key_value_pair[1]) # evaluates string into bool
                    else:
                        config[key_value_pair[0]] = str(key_value_pair[1]) # catch-all, sanitises any dubious entries
            return config

    @classmethod
    def cache_hierarchy(Generate, config):
        hierarchy = {}

        # Complicated way to test if config file warrents a given cache structure
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
    def cache(Generate, config, memory_type): # generating collections.deque instead of lists can improve the code and functionality
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
            cache['way_0'] = {'tag': [], 'new':[], 'dirty':[], 'data': []}
            for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                cache['way_0']['tag'].insert(0, '0000') # tag holds upper section of address
                cache['way_0']['new'].insert(0, 1) # new/accessed aids prefetching
                cache['way_0']['data'].insert(0, {f"{offset<<1:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # bit_length() ~ log2
                cache['way_0']['dirty'].insert(0, 1) # https://en.wikipedia.org/wiki/Dirty_bit
        else:
            for w in range(WAYS): # WAYS, as in, x-way set-associative
                way_key = f"way_{w:x}" # way_{hex(w)}
                cache[way_key] = {'tag': [], 'new':[], 'dirty':[], 'data': []}
                for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                    cache[way_key]['tag'].insert(0, '0000') # tag holds upper section of address
                    cache[way_key]['new'].insert(0, 1) # new/accessed aids  prefetching
                    cache[way_key]['data'].insert(0, {f"{offset<<1:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # bit_length() ~ log2
                    cache[way_key]['dirty'].insert(0, 1) # https://en.wikipedia.org/wiki/Dirty_bit
        return cache # cache['way_x']['tag'/'data']

    @classmethod
    def memory(Generate, config, memory_type):
        PAGE_SIZE = config.get("PAGE_SIZE")
        if memory_type == 'ROM':
            START_ADDRESS = int(config['ROM_START_ADDRESS'], 16)
            BYTE_CAPACITY = int(config['MAIN_START_ADDRESS'], 16) - START_ADDRESS
            starting_page = int(START_ADDRESS / PAGE_SIZE)
            if BYTE_CAPACITY <= 0: ### BUG: ROM address-space cannot be above RAM's address-space
                raise ConfigError('Custom start addresses not yet supported\n -- ROM_START_ADDRESS must equal 0x0.')
        elif memory_type == 'MAIN':
            START_ADDRESS = int(config['MAIN_START_ADDRESS'], 16)
            BYTE_CAPACITY = config['MAIN_MEMORY_SIZE']
            starting_page = int(START_ADDRESS / PAGE_SIZE)
        else:
            START_ADDRESS, starting_page = 0, 0
            BYTE_CAPACITY = config['GPR_MEMORY_SIZE']
        memory = {}
        pages = int(BYTE_CAPACITY / PAGE_SIZE) # Page -> [a, group, of, data, mapped, to, one, address]
        for p in range(starting_page, starting_page + pages): # building the memory
            memory[f"page_{p:x}"] = {}
            for offset in range(PAGE_SIZE >> 1): # Offset -> Address of data within a page
                memory[f"page_{p:x}"][f"{offset<<1:x}"] = '0000' # Hex formatting -- pages.bit_length()-4 == log2(x)-4
        return memory

    @classmethod
    def files_to_rom(Generate, rom, config):
        files = config['ROM_FILE_NAMES'].split()
        file_format = config['ROM_FILE_FORMAT']
        START_ADDRESS = config['ROM_START_ADDRESS'][2:]
        # print(files, file_format, START_ADDRESS) # [ DEBUG ]
        queue, pages, page_queue = {}, {}, {}
        queue_offset  = 0
        for f in files: # loop A: Select files
            with open(f"bytecode/{f}", 'r') as active_file:
                for line, bytecode in enumerate(active_file):# loop A.B: collect bytecode from the file
                    queue[queue_offset+line] = f"{int(bytecode.strip(), 2):04x}"
            queue_offset = len(queue.values()) # Reset the offset as a lower bound for the next file
        page_key = decode.page(START_ADDRESS, 4)
        pages.update({page_key: {}})
        for position, bytecode in enumerate(queue.values()): # loop C: break bytecode into pages and store to ROM
            page_offset = f"{(position<<1) % 16:x}"
            pages[page_key].update({page_offset: bytecode})
            # print(page_offset, page_key, pages) # [ DEBUG ]
            if page_offset == 'e':
                rom[page_key] = pages[page_key]
                page_key = f"page_{int(page_key[5:], 16) + 1:x}"
                pages.update({page_key: {}})
        empty_entries = 8 - len(pages[page_key])
        print(f"EE: {empty_entries}")
        for i in range(empty_entries): # loop D: Fill partially filled pages
            pages[page_key].update({f"{int(page_offset, 16)+i+1:x}": '0000'})
        rom[page_key] = pages[page_key]
        return rom

    @classmethod
    def queue(Generate, config, memory_type):
        queue = collections.deque([], config[f"{memory_type}_DEPTH"])
        return queue


    def __init__(self, config_name): # Size in bytes
        self.config = Generate.config(config_name) # Take s16.conf key-values and place in dictionary
        self.PAGE_SIZE = Generate.page_size(self.config) # Hardcoded to 16 Bytes
        self.program_counter = {'address': '0000', 'offset': '0002'}
        self.reorder_buffer = Generate.queue(self.config, 'REORDER_BUFFER')



        self.register = Generate.memory(self.config, 'GPR') # GPRs will technically be 16-bit + 2=bit flags -- info in docs
        self.register_flags = {'co' : '0000', 'zr': '0000'}
        self.main_memory = Generate.memory(self.config, 'MAIN')
        self.read_only_memory = Generate.memory(self.config, 'ROM')
        self.read_only_memory = Generate.files_to_rom(self.read_only_memory, self.config)
        self.cache_hierarchy = Generate.cache_hierarchy(self.config) # depreciated - could be usefull in future updates
        if 'L1' in self.cache_hierarchy:
            self.l1_data_cache = self.cache_hierarchy['L1']['data'] = Generate.cache(self.config, 'L1_DATA')
            self.l1_inst_cache = self.cache_hierarchy['L1']['inst'] = Generate.cache(self.config, 'L1_INST')
        if 'L2' in self.cache_hierarchy:
            self.l2_cache = self.cache_hierarchy['L2'] = Generate.cache(self.config, 'L2')

    def read(self, source, sink, mode=""): # modes: [b]yte, [w]ord, [p]age, [i]nstruction_page
        pass



    def write(self, source, sink, mode=""): # modes: [b]yte, [w]ord, [p]age, [i]nstruction_page
        pass


    def prefetch(self):
        # check reference_prediction_table if stride == 0 for current tag & state ==
        # if cache[way_x][new][page] == False: # The page has been accessed -> NOT "new"
        #   pc_address = get_current_pc_address
        #
        pass


    def step_clock(self): # fully step through cpu stages
        print('----cycle----')
        counter = self.program_counter


        # [ DECODE ]
        print(read.cache(self.l1_inst_cache, self.read_only_memory, counter['address']))
        # instruction.decode()



        # [ FETCH ]




        # [ EXECUTE ]






        # [ WRITEBACK ]


        # FINAL STEP
        counter['address'] = f"{(int(counter['address'],16)+int(counter['offset'],16)):04x}"
        pass





def main():
    print()
    print(os.getcwd())

    s16 = Generate('s16.conf') # page_size=16 Bytes -> 8*2 Byte words -> 2B = 16-bits
    tprint.memory(s16.read_only_memory, 'rom')
    # tprint.memory(s16.register, 'gpr')
    # tprint.memory(s16.main_memory, 'main')
    # tprint.cache(s16.l1_data_cache, 'l1d')
    # write.memory(s16.main_memory, '0080', s16.rom['page_0'])
    # tprint.memory(s16.main_memory, 'main')

    print(s16.l1_data_cache)
    print(s16.reorder_buffer)
    # instruction.decode('0000000001111101')

    # realistic loop:
        # Prefetch to I-Cache
        # commit instruction to ROB
        # decode instruction
        # execute
        # writeback ready ROB entry
    i=0
    while i < 10: # simple test loop
        print(i)
        tprint.cache(s16.l1_inst_cache, 'l1_i')
        s16.step_clock()
        print(s16.program_counter)
        i+=1
    pass


if __name__ == "__main__":
    main()
