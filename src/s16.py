#!/usr/bin/env python
from customExceptions import *
import collections
import assembler.asm
import instruction
import replacement
import decode
import tprint


##----[Notes]----##

# NOTE:
# s16 = Simple 16
# Page = Block of 32 Bytes = (16-bits*16)/8 -- I'm allowing this to be modifiable
# Cache:
#   - https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
#   - https://www.geeksforgeeks.org/write-through-and-write-back-in-cache
# Dirty Bit:
#   - Don't get the order mixed up:
#       * When page is modified, the dirty bit is set to True
#       * Upon eviction, the modified page needs go through the write-back process
#   - https://en.wikipedia.org/wiki/Dirty_bit
# Adding date and time to a file:
#   - https://www.geeksforgeeks.org/how-to-create-filename-containing-date-or-time-in-python/

# BUG LIST:
# > Replacement algorithm does not return outbound entry
# >
# >
# > ROM address-space cannot be above RAM's address-space [[ This may not matter, keep in BUG for now ]]
# > Only binary file-types can be generted/used (MAY NOT IMPLEMENT BUT ATTACH A BIN -> HEX CONVERTER SCRIPT)

# TODO LIST:
# > (lol nvm lets do this now)
# > REFACTOR: read.cache() and write.cache. I've gained more knowledge on flag usage and deques
#       - Modify Generate.cache()
#       - Update the lru replacemeny functions
# > Find a way to offload cache heirarchy into <module>replacement logic?
# >
# >
# >
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
        tag, way_key, offset = decode.way(address, way_bits, offset_bits) # decodes address into TAG|WAY|OFFSET
        page_key = decode.page(address, offset_bits)
        # tag = f"{int(bin_address[way_bits:-(offset_bits+1)], 2):0{4}x}"
        # offset = int(bin_address[-(offset_bits):15], 2) << 1 # Extracting the upper most bits of the address
        if tag in cache[way_key]['tag']: # wayyyyyyyyy more readable
            tag_index = cache[way_key]['tag'].index(tag)
            dirty_bit = cache[way_key]['dirty'][tag_index]
            if dirty_bit == 0:
                print('hit')                                                            # [ debug ]
                return cache[way_key]['data'][tag_index][f"{offset:0x}"]
            else: # fetch newest version -- i_cache's may need to look inside d_cache for newest data
                print('dirty hit... Finding last modified page')                        # [ debug ]
                # page_address = int(bin_address[:-(offset_bits)], 2) # The remaining bits address the page
                page = main_memory[page_key]
                print('miss...retrieving page\npage_address:',page_key,',page:', page)  # [ debug ]
                new_entry = {'tag': tag, 'new': 1, 'dirty': 0, 'data': page} # int(bin_address[0:-(offset_bits)], 2)int(bin_address[0:-(offset_bits)], 2)collecting components which make up an entry
                cache['algorithm'](cache, way_key, new_entry) # sending the entry to the replacement algorithm
                tag_index = cache[way_key]['tag'].index(tag)
                return cache[way_key]['data'][tag_index][f"{offset:0x}"]
        else:
            # page_address = int(bin_address[:-(offset_bits)], 2) # The remaining bits address the page
            page = main_memory[page_key]
            print('miss...retrieving page\npage_address:',page_key,',page:', page)  # [ debug ]
            new_entry = {'tag': tag, 'new': 1, 'dirty': 0, 'data': page} # int(bin_address[0:-(offset_bits)], 2)int(bin_address[0:-(offset_bits)], 2)collecting components which make up an entry
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
        tag, way_key, offset = decode.way(address, way_bits, offset_bits) # decodes address into TAG|WAY|OFFSET
        # tag = f"{int(bin_address[way_bits:-(offset_bits+1)], 2):0{4}x}"
        if tag in cache[way_key]['tag']: # Testing for a read_hit
            tag_index = cache[way_key]['tag'].index(tag)
            dirty_bit = cache[way_key]['dirty'][tag_index]
            if dirty_bit == 0: # Clean hit
                print('hit')                                        # [ debug ]
                # offset = int(bin_address[-(offset_bits):15], 2) << 1 # Extracting the upper most bits of the address
                cache[way_key]['data'][tag_index][f"{offset:x}"] = data
            else: # fetch newest version -- i_cache's may need to look inside d_cache for newest data -- Dirty hit
                print('dirty hit... Finding last modified page')    # [ debug ]
                # with just 1 level of caching, only direct accesses to main_memory will cause a page to become dirty
                # This could possibly happen if a DMA(Direct Memory Access) is implemented. Unlikely, maybe in T16.
                page_key = decode.page(address, offset_bits)
                if page_key in main_memory: # If address is valid
                    page[f"{offset:0x}"] = data # data written to the incoming page
                    new_entry = {'tag': tag, 'new': 1, 'dirty': 0, 'data': page} # collecting components which make up an entry
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
            hierarchy['l1_data'], hierarchy['l1_inst'] = {}, {}
            hierarchy['l1_data']['config'] = {
                'size': config.get('L1_DATA_CACHE_SIZE'),
                'ways': config.get('L1_DATA_CACHE_WAYS'),
                'cost': config.get('L1_DATA_CACHE_COST'),
                'repl': config.get('L1_DATA_CACHE_REPL')}
            hierarchy['l1_inst']['config'] = {
                'size': config.get('L1_INST_CACHE_SIZE'),
                'ways': config.get('L1_INST_CACHE_WAYS'),
                'cost': config.get('L1_INST_CACHE_COST'),
                'repl': config.get('L1_INST_CACHE_REPL')}
            if None in hierarchy['l1_data'].values() or None in hierarchy['l1_inst'].values():
                del hierarchy['l1_data']
                del hierarchy['l1_inst']
        if config.get('L2_CACHE') == True:
            hierarchy['l2'] = {}
            hierarchy['l2']['config'] = {
                'size': config.get('L2_CACHE_SIZE'),
                'ways': config.get('L2_CACHE_WAYS'),
                'cost': config.get('L2_CACHE_COST'),
                'repl': config.get('L2_CACHE_REPL')}
            if None in hierarchy['l2'].values():
                del hierarchy['l2']
        return hierarchy

    @classmethod ### PAGE_SIZE is set inside the config but due to the code not being functional, heres a sanity check
    def page_size(Generate, config):
        PAGE_SIZE = config.get('PAGE_SIZE')
        if PAGE_SIZE != 16: # HARDCODED 8*16-bit words
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
                cache['way_0']['data'].insert(0, {f"{offset:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # bit_length() ~ log2
                cache['way_0']['dirty'].insert(0, 1) # https://en.wikipedia.org/wiki/Dirty_bit
        else:
            for w in range(WAYS): # WAYS, as in, x-way set-associative
                way_key = f"way_{w:x}" # way_{hex(w)}
                cache[way_key] = {'tag': [], 'new':[], 'dirty':[], 'data': []}
                for a in range(tags_per_way): # Generate a initialised dictionary/page with offset(0 to f): 0000 (hex)
                    cache[way_key]['tag'].insert(0, '0000') # tag holds upper section of address
                    cache[way_key]['new'].insert(0, 1) # new/accessed aids  prefetching
                    cache[way_key]['data'].insert(0, {f"{offset:0{PAGE_SIZE.bit_length()-4}x}": '0000' for offset in range(PAGE_SIZE>>1)}) # bit_length() ~ log2
                    cache[way_key]['dirty'].insert(0, 1) # https://en.wikipedia.org/wiki/Dirty_bit
        return cache # cache['way_x']['tag'/'data']


    @classmethod
    def cache_deque(Generate, config, memory_type): # generating collections.deque instead of lists can improve the code and functionality
        # https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
        cache                 = {} # cache decoding: way | tag | offset
        WAYS                  = config.get(f"{memory_type}_CACHE_WAYS")
        PAGE_SIZE             = config.get('PAGE_SIZE')
        BYTE_CAPACITY         = config.get(f"{memory_type}_CACHE_SIZE")
        tag_count             = int(BYTE_CAPACITY / PAGE_SIZE) # minimum BYTE_CAPACITY == WAYS*PAGE_SIZE
        tags_per_way          = int(tag_count / WAYS)
        replacement_algorithm = config.get(f"{memory_type}_CACHE_REPL")
        cache['algorithm']    = eval(f"replacement.{replacement_algorithm}")
        # print('tc: ',tag_count, 'tpw: ', tags_per_way) # [ debug ]
        if tags_per_way == 0:
            raise CacheCapacityError(f"Insufficient <BYTE_CAPACITY> for the number of <WAYS>\nMinimum <BYTE_CAPACITY> == WAYS*PAGE_SIZE = {WAYS*PAGE_SIZE}")
        if WAYS < 2: # Other functions require, at least, a 'way_0' key to access the data inside a cache
            ache['way_0'] = {
            'tag': collections.deque([], tags_per_way),  # tag holds upper section of address
            'new':collections.deque([], tags_per_way), # new/accessed aids prefetching
            'data': collections.deque([], tags_per_way),
            'dirty':collections.deque([], tags_per_way)} # https://en.wikipedia.org/wiki/Dirty_bit
        else:
            for w in range(WAYS): # WAYS, as in, x-way set-associative
                way_key = f"way_{w:x}" # way_{hex(w)}
                cache[way_key] = {
                    'tag': collections.deque([], tags_per_way),
                    'new':collections.deque([], tags_per_way),
                    'data': collections.deque([], tags_per_way),
                    'dirty':collections.deque([], tags_per_way)}
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
        files         = config['ROM_FILE_NAMES'].split()
        file_format   = config['ROM_FILE_FORMAT']
        START_ADDRESS = config['ROM_START_ADDRESS'][2:]
        queue_offset  = 0
        queue, pages, page_queue = {}, {}, {}
        # print(files, file_format, START_ADDRESS) # [ DEBUG ]
        for f in files: # loop A: Select files
            with open(f"bytecode/{f}", 'r') as active_file:
                for line, bytecode in enumerate(active_file):# loop B: collect bytecode from the file
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
                page_key      = f"page_{int(page_key[5:], 16) + 1:x}"
                pages.update({page_key: {}})
        empty_entries = 8 - len(pages[page_key])
        for i in range(empty_entries): # loop D: Fill partially filled pages
            pages[page_key].update({f"{int(page_offset, 16)+i+1:x}": '0000'})
        rom[page_key] = pages[page_key]
        return rom

    @classmethod
    def queue(Generate, config, memory_type):
        queue = collections.deque([], config[f"{memory_type}_DEPTH"])
        return queue


    def __init__(self, config_name): # Size in bytes
        self.config            = Generate.config(config_name) # Take s16.conf key-values and place in dictionary
        self.PAGE_SIZE         = Generate.page_size(self.config) # Hardcoded to 16 Bytes
        self.program_counter   = {'address': '0000', 'offset': '0002'}
        self.reorder_buffer    = Generate.queue(self.config, 'REORDER_BUFFER')
        self.read_only_memory  = Generate.memory(self.config, 'ROM')
        self.read_only_memory  = Generate.files_to_rom(self.read_only_memory, self.config)
        self.main_memory       = Generate.memory(self.config, 'MAIN')
        self.combined_memory   = {**self.read_only_memory ,**self.main_memory} # combined for self.read() operations
        self.cache_hierarchy   = Generate.cache_hierarchy(self.config) # depreciated - could be usefull in future updates
        self.register          = Generate.memory(self.config, 'GPR') # = self.cache_hierarchy['GPR']       may insert GPR hierarchy
        self.register_flags    = {'co' : '0000', 'zr': '0000'}
        if 'l1_data' in self.cache_hierarchy: # if l1_data exists, l1_inst exists
            self.l1_data_cache = self.cache_hierarchy['l1_data']['unit'] = Generate.cache_deque(self.config, 'L1_DATA')
            self.l1_inst_cache = self.cache_hierarchy['l1_inst']['unit'] = Generate.cache_deque(self.config, 'L1_INST')
        if 'l2' in self.cache_hierarchy:
            self.l2_cache      = self.cache_hierarchy['l2']['unit'] = Generate.cache_deque(self.config, 'L2')

    def read(self, source_address, sink_address, mode=''): # modes: [b]yte, [w]ord (default), [p]age

        # FUNCTIONALITY FIRST -> THEN IMPROVE. thanks brain

        # BUG: does not return the replaced entry
        resolved_mode = { # I can see implementing these formats as a pain in the ass for paged
            (mode=='')|(mode=='w'): (lambda word: word), # No need to modify the output
            mode=='b'             : (lambda byte: f"00{byte[-2:]}"),
            # mode=='p'             : (lambda page: page),
            }

        hierarchy   = self.cache_hierarchy
        register    = self.register
        offset_bits = self.PAGE_SIZE>>2
        source_page = decode.page(source_address, offset_bits)
        hits        = 0
        live_cache  = [cache for cache in self.cache_hierarchy] # order: l1_data?, l1_inst?, l2?
        sink_page, sink_offset = decode.register(sink_address)

        for target_cache in live_cache:
            way_bits = hierarchy[target_cache]['config']['ways']
            tag, way_key, offset = decode.way(source_address, way_bits, offset_bits) # decodes address into TAG|WAY|OFFSET
            if tag in hierarchy[target_cache]['unit'][way_key]['tag']: # is tag present in way?
                cache     = hierarchy[target_cache]['unit']
                tag_index = cache[way_key]['tag'].index(tag)
                dirty_bit = cache[way_key]['dirty'][tag_index]
                new       = cache[way_key]['new'][tag_index]
                print('hit in', target_cache, 'dirty bit', dirty_bit)
                if target_cache=='l1_data': # L1_Data HIT -- read value into register
                    hits += 1
                    self.l1_data_cache[way_key]['new'][tag_index] = 0 # Hits will set 'new' to 0
                    register[sink_page][sink_offset] = self.l1_data_cache[way_key]['data'][tag_index][f"{offset:x}"]
                    break
                if target_cache=='l1_inst': # L1_Inst HIT -- Move page to L1_Data. NEW UNCHANGED
                    # Tags and way keys need to be updated when storing to a new cache
                    hits += 1
                    l1_data_tag, l1_data_way, offset = decode.way(source_address, hierarchy['l1_data']['config']['ways'], offset_bits)
                    entry = {'new': new, 'dirty':0, 'tag': l1_data_tag,  'data': self.l1_inst_cache[way_key]['data'][tag_index]}
                    self.l1_data_cache['algorithm'](self.l1_data_cache, l1_data_way, entry) # [lru/lfu/etc..](cache, way, entry)
                    l1_data_tag_index = self.l1_data_cache[way_key]['tag'].index(tag)
                    register[sink_page][sink_offset] = self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index][f"{offset:x}"] # read from l1 -> reg
                    break
                if target_cache=='l2': # L2 HIT -- Move page to L1_Data. NEW UNCHANGED
                    # Tags and way keys need to be updated when storing to a new cache
                    hits += 1
                    l1_data_tag, l1_data_way, offset = decode.way(source_address, hierarchy['l1_data']['config']['ways'], offset_bits)
                    entry = {'new': new, 'dirty':0, 'tag': l1_data_tag,  'data': self.l2_cache[way_key]['data'][tag_index]}
                    self.l1_data_cache['algorithm'](self.l1_data_cache, l1_data_way, entry) # [lru/lfu/etc..](cache, way, entry)
                    l1_data_tag_index = self.l1_data_cache[way_key]['tag'].index(tag)
                    register[sink_page][sink_offset] = self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index][f"{offset:x}"] # read from l1 -> reg
                    break
            # if target_cache[way_key][tag].maxlen > len(target_cache[way_key]['tag']): # is way fully populated?
            #     pass
        if (hits == 0):
            print('miss')
            l1_data_tag, l1_data_way, offset = decode.way(source_address, hierarchy['l1_data']['config']['ways'], offset_bits)
            entry = {'new': 1, 'dirty':0, 'tag': l1_data_tag,  'data': self.combined_memory[source_page]}
            self.l1_data_cache['algorithm'](self.l1_data_cache, l1_data_way, entry) # [lru/lfu/etc..](cache, way, entry)
            l1_data_tag_index = self.l1_data_cache[way_key]['tag'].index(tag)
            register[sink_page][sink_offset] = self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index][f"{offset:x}"]








    def write(self, source, sink, mode=""): # modes: [b]yte, [w]ord, [p]age
        hierarchy = self.cache_hierarchy
        resolved_mode = { # end of the method?
            mode==''|mode=='w': {  #
                'source': hierarchy['L1']['data'],
                'sink': hierarchy['GPR']},
            mode=='b': {
                'source': hierarchy['L1']['data'],
                'sink': hierarchy['GPR']},
            mode=='p': {
                'source': hierarchy['L1']['data'],
                'sink': hierarchy['GPR']},
            }


    def prefetch(self):
        # check reference_prediction_table if stride == 0 for current tag & state ==
        # if cache[way_x][new][page] == False: # The page has been accessed -> NOT "new"
        #   pc_address = get_current_pc_address
        #

        pass


def step_clock(cpu): # fully step through cpu stages
    print('----cycle----')
    counter = cpu.program_counter


    # [ DECODE ]
    # print(read.cache(self.l1_inst_cache, self.read_only_memory, counter['address']))

    # instruction.decode()



    # [ FETCH ]




    # [ EXECUTE ]




    # [ WRITEBACK ]


    # FINAL STEP
    counter['address'] = f"{(int(counter['address'],16)+int(counter['offset'],16)):04x}"
    pass





def main():
    print()

    s16 = Generate('s16.conf') # page_size=16 Bytes -> 8*2 Byte words -> 2B = 16-bits

    # print()
    # # print(s16.main_memory)
    # print(s16.l1_data_cache)
    # # print(s16.reorder_buffer)
    # # print(s16.cache_hierarchy)
    # s16.read('0000','0000')
    # tprint.memory(s16.register, 'gpr')
    # # tprint.cache(s16.l1_data_cache, 'l1d')
    # # instruction.decode('0000000001111101')
    # print(s16.l1_data_cache)
    # s16.read('0002','0010')
    # tprint.memory(s16.register, 'gpr')
    # realistic loop:
        # Prefetch to I-Cache
        # commit instruction to ROB
        # decode instruction
        # execute
        # writeback ready ROB entry
    i=0
    while i < 2: # simple test loop
        print(i)
        print(s16.l1_inst_cache)
        print(s16.l1_data_cache)

        tprint.memory(s16.register, 'gpr')
        s16.read('0000', '000')
        s16.read('0010', '001')
        s16.read('0001', '100')
        s16.read('001a', '1111')
        step_clock(s16)
        print(s16.program_counter)
        print(s16.l1_data_cache)
        tprint.memory(s16.register, 'gpr')

        i+=1
    # pass
    #

if __name__ == "__main__":
    main()
