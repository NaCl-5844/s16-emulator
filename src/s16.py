#!/usr/bin/env python
from customExceptions import *
from functools import cache
import collections
import assembler.asm
import instruction
import replacement
import decode
import tprint


##----[Notes]----##

# NOTE:
#
# I'm making an effort to learn/use PEP 8* guidelines, except the "no-alignment" policy.
# Not following the policy has made following my own code way easier.
# If this project ever gets forked (doubt) then I may take the time to de-align.
# *PEP 8: https://peps.python.org/pep-0008/
#
# s16  = Simple 16
# Page = 8*words = 8*16-bit = 8*2B = 16-Bytes -- possibly modifiable in the future
#



# BUG LIST:
# > Check prefetch -- not properly implemented
# >
# >
# >
# > Only binary file-types can be generted/used (MAY NOT IMPLEMENT BUT ATTACH A BIN -> HEX CONVERTER SCRIPT)

# TODO LIST:
# > implement pipeline related methods
# > Implement call, return and register_window https://en.wikipedia.org/wiki/Register_window
# >
# >
# > When the project hits v1.x.x make an effort to properly comment s16.py and supporting modules




#----[Initialisation]----#

class Generate:

    @classmethod # basically a function without access to the object and its internals
    def config(Generate, config_name):
        with open(config_name, "r") as s16_config:
            config = {}
            for line in s16_config:
                clean_line = line.strip() # Clean up line
                if clean_line == '' or clean_line[0] == '[' or clean_line[0] == '#' or clean_line[0] == '\\': # jump to start if...
                    continue # '\\' -> \, is the first character of *newline* -> \n
                key_value_pair = clean_line.split('=')
                if len(key_value_pair) == 1: # jump to start if no value provided{len(key+value)==2}
                    continue
                key_value_pair[0] = key_value_pair[0].strip()
                key_value_pair[1] = key_value_pair[1].strip()
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
            raise ConfigError('Please use the default 16-Byte PAGE_SIZE')
        else:
            return PAGE_SIZE

    @classmethod
    def cache_deque(Generate, config, memory_type): # generating collections.deque instead of lists can improve the code and functionality
        # https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache
        cache                 = {} # cache decoding: way | tag | offset
        WAYS                  = config[f"{memory_type}_CACHE_WAYS"]
        PAGE_SIZE             = config['PAGE_SIZE']
        BYTE_CAPACITY         = config[f"{memory_type}_CACHE_SIZE"]
        tag_count             = int(BYTE_CAPACITY / PAGE_SIZE) # minimum BYTE_CAPACITY == WAYS*PAGE_SIZE
        tags_per_way          = int(tag_count / WAYS)
        replacement_algorithm = config[f"{memory_type}_CACHE_REPL"]
        cache['algorithm']    = eval(f"replacement.{replacement_algorithm}")
        if tags_per_way == 0:
            raise CacheCapacityError(f"Insufficient <BYTE_CAPACITY> for the number of <WAYS>\nMinimum <BYTE_CAPACITY> == WAYS*PAGE_SIZE = {WAYS*PAGE_SIZE}")
        else:
            for w in range(WAYS): # WAYS, as in, x-way set-associative
                way_key = f"way_{w:x}" # way_{hex(w)}
                cache[way_key] = {
                    'tag': collections.deque([], tags_per_way), # tag holds upper section of address
                    'new': collections.deque([], tags_per_way), # new/accessed aids prefetching
                    'data': collections.deque([], tags_per_way), # page[offset]
                    'dirty': collections.deque([], tags_per_way)} # https://en.wikipedia.org/wiki/Dirty_bit
        return cache # cache['way_x']['tag'/'data']

    @classmethod
    def memory(Generate, config, memory_type):
        PAGE_SIZE = config.get("PAGE_SIZE")
        if memory_type == 'ROM':
            START_ADDRESS = int(config['ROM_START_ADDRESS'], 16)
            BYTE_CAPACITY = int(config['MAIN_START_ADDRESS'], 16) - START_ADDRESS
            starting_page = int(START_ADDRESS / PAGE_SIZE)
            if BYTE_CAPACITY <= 0:
                raise ConfigError('Read ony memory(ROM) must start at memory address 0\n -- ROM_START_ADDRESS must equal 0x0.')
        elif memory_type == 'MAIN':
            START_ADDRESS = int(config['MAIN_START_ADDRESS'], 16)
            BYTE_CAPACITY = config['MAIN_MEMORY_SIZE']
            starting_page = int(START_ADDRESS / PAGE_SIZE)
        else:
            START_ADDRESS, starting_page = 0, 0
            BYTE_CAPACITY = config['GPR_MEMORY_SIZE']
        memory = {}
        pages  = int(BYTE_CAPACITY / PAGE_SIZE) # Page -> [a, group, of, data, mapped, to, one, address]
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
        self.PAGE_SIZE         = Generate.page_size(self.config) # Hardcoded, hence the CAPS, to 16 Bytes
        self.offset_bits       = self.PAGE_SIZE>>2
        self.program_counter   = {'address': '0000', 'offset': '0002'}
        self.reorder_buffer    = Generate.queue(self.config, 'REORDER_BUFFER')
        self.read_only_memory  = Generate.memory(self.config, 'ROM')
        self.read_only_memory  = Generate.files_to_rom(self.read_only_memory, self.config)
        self.main_memory       = Generate.memory(self.config, 'MAIN')
        self.combined_memory   = {**self.read_only_memory, **self.main_memory} # combined for self.read() operations
        self.cache_hierarchy   = Generate.cache_hierarchy(self.config) # depreciated - could be usefull in future updates
        self.register          = Generate.memory(self.config, 'GPR') # = self.cache_hierarchy['GPR']       may insert GPR hierarchy
        self.register_flags    = {'co' : '0000', 'zr': '0000'}
        if 'l1_data' in self.cache_hierarchy: # if l1_data exists, l1_inst exists
            self.l1_data_cache = self.cache_hierarchy['l1_data']['unit'] = Generate.cache_deque(self.config, 'L1_DATA')
            self.l1_inst_cache = self.cache_hierarchy['l1_inst']['unit'] = Generate.cache_deque(self.config, 'L1_INST')
        else:
            raise ConfigError('config must include at least an l1_data and l1_inst cache')
        if 'l2' in self.cache_hierarchy:
            self.l2_cache      = self.cache_hierarchy['l2']['unit'] = Generate.cache_deque(self.config, 'L2')

        # -------- [ BOOT FROM ROM ] -------- # Not sure what to call this. Places page_0 into l1_instr_cache
        l1_inst_tag, l1_inst_way, offset = decode.way('0000', self.cache_hierarchy['l1_inst']['config']['ways'], self.offset_bits)
        first_page = decode.page('0000', self.offset_bits)
        entry      = {'new': 1, 'dirty': 0, 'tag': l1_inst_tag, 'data': self.read_only_memory[first_page]}
        self.l1_data_cache['algorithm'](self.l1_inst_cache, l1_inst_way, entry)
        # -------- [ /BOOT FROM ROM ] -------- #

        # self.tagged_prefetch_state      = '00' # 00: strong miss, 01: weak miss, 10: weak hit, 11: string hit
        # self.reference_prediction_table = Generate.queue(self.config, 'REF_PREDICTION_TABLE')


    def read(self, source_address, sink_address, mode=""): # memory_address, register_address,  modes: [b]yte, [w]ord, [p]age
        register    = self.register
        hierarchy   = self.cache_hierarchy
        offset_bits = self.offset_bits
        live_cache  = [cache for cache in hierarchy] # order: l1_data?, l1_inst?, l2?
        source_page = decode.page(source_address, offset_bits)
        hit         = None
        sink_page, sink_offset = decode.register(sink_address)

        # -------- [ HIERARCHY MANAGEMENT ] -------- #
        for target_cache in live_cache:
            target_cache_ways              = hierarchy[target_cache]['config']['ways']
            target_tag, target_way, offset = decode.way(source_address, target_cache_ways, offset_bits) # decodes address into TAG|WAY|OFFSET - offset universal to PAGE_SIZE
            if target_tag in hierarchy[target_cache]['unit'][target_way]['tag']: # is tag present in way?
                target_tag_index                 = hierarchy[target_cache]['unit'][target_way]['tag'].index(target_tag)
                l1_data_tag, l1_data_way, offset = decode.way(source_address, hierarchy['l1_data']['config']['ways'], offset_bits)  # decodes address into TAG|WAY|OFFSET
                l1_data_tag_index                = self.l1_data_cache[l1_data_way]['tag'].index(l1_data_tag)
                evicted_entry_address            = decode.join_keys(target_way, target_cache_ways, target_tag, offset_bits)
                hit                              = target_cache
                print('hit in', target_cache)
                if target_cache == 'l1_data': # L1_Data HIT -- read value into register
                    self.l1_data_cache[l1_data_way]['new'][l1_data_tag_index] = 0 # Hits will set 'new' to 0
                    evicted_entry = None
                    break
                if target_cache == 'l1_inst': # L1_Inst HIT -- Move page to L1_Data.
                    entry = {'new': 1, 'dirty':0, 'tag': target_tag, 'data': self.l1_inst_cache[target_way]['data'][target_tag_index]}
                if target_cache == 'l2': # L2 HIT -- Move page to L1_Data. Evicted entries must be kicked up the hierarchy if modified(dirty=1)
                    entry = {'new': 1, 'dirty':0, 'tag': target_tag, 'data': self.l2_cache[target_way]['data'][target_tag_index]}
                evicted_entry         = self.l1_data_cache['algorithm'](self.l1_data_cache, l1_data_way, entry) # if cache == 'l1_inst' | 'l2' -> move to 'l1_data'
                evicted_entry_address = decode.join_keys(target_way, target_cache_ways, target_tag, offset_bits)
                break
        if hit == None:
            print('miss')
            l1_data_tag, l1_data_way, offset = decode.way(source_address, hierarchy['l1_data']['config']['ways'], offset_bits)  # decodes address into TAG|WAY|OFFSET
            entry                 = {'new': 1, 'dirty':0, 'tag': l1_data_tag, 'data': self.combined_memory[source_page]}
            evicted_entry         = self.l1_data_cache['algorithm'](self.l1_data_cache, l1_data_way, entry) # [lru/lfu/etc..](cache, way, entry)
            evicted_entry_address = decode.join_keys(target_way, target_cache_ways, target_tag, offset_bits)
            l1_data_tag_index     = self.l1_data_cache[l1_data_way]['tag'].index(l1_data_tag)

        evicted_entry_page = decode.page(evicted_entry_address, offset_bits)
        if (evicted_entry != None) & ('l2' in live_cache): # Entry modified and returned to evicted_entry, instead of None
            l2_tag, l2_way, offset = decode.way(evicted_entry_address, hierarchy['l2']['config']['ways'], offset_bits)
            entry                  = {'new': 1, 'dirty':1, 'tag': l2_tag, 'data': evicted_entry['data']} # dirty_bit=1 -> modified
            evicted_l2_entry       = self.l2_cache['algorithm'](self.l2_cache, l2_way, entry) # [lru/lfu/etc..](cache, way, entry)
            if evicted_l2_entry != None:
                self.main_memory[evicted_entry_page] = evicted_l2_entry['data']
        elif evicted_entry != None:
            self.main_memory[evicted_entry_page] = evicted_entry['data']
        # -------- [ /HIERARCHY MANAGEMENT ] -------- #

        offset_key = f"{offset:x}"
        if (mode=='') | (mode=='w'):
            register[sink_page][sink_offset] = self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index][offset_key]
        elif mode=='b':
            register[sink_page][sink_offset] = f"{register[sink_page][sink_offset][:2]}{self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index][offset_key][-2:]}"
        elif mode=='p':
            register[sink_page]              = self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index]
        else:
            raise ValueError('Check <instruction> module for cpu.read() ModeError')
        return hit


    def write(self, source_address, sink_address, mode=""): # memory_address, register_address,  modes: [b]yte, [w]ord, [p]age
        register    = self.register
        hierarchy   = self.cache_hierarchy
        offset_bits = self.offset_bits
        live_cache  = [cache for cache in hierarchy] # order: l1_data?, l1_inst?, l2?
        hit         = None
        l1_data_way_count               = hierarchy['l1_data']['config']['ways']
        source_page, source_offset      = decode.register(source_address)
        sink_tag, sink_way, sink_offset = decode.way(sink_address, l1_data_way_count, offset_bits)

        # -------- [ HIERARCHY MANAGEMENT ] -------- #
        for target_cache in live_cache:
            target_cache_ways              = hierarchy[target_cache]['config']['ways']
            target_tag, target_way, offset = decode.way(sink_address, target_cache_ways, offset_bits) # decodes address into TAG|WAY|OFFSET - offset universal to PAGE_SIZE
            if target_tag in hierarchy[target_cache]['unit'][target_way]['tag']: # is tag present in way?
                target_tag_index                 = hierarchy[target_cache]['unit'][target_way]['tag'].index(target_tag)
                l1_data_tag, l1_data_way, offset = decode.way(sink_address, l1_data_way_count, offset_bits)  # decodes address into TAG|WAY|OFFSET
                l1_data_tag_index                = self.l1_data_cache[l1_data_way]['tag'].index(l1_data_tag)
                # evicted_entry_address            = decode.join_keys(target_way, target_cache_ways, target_tag, offset_bits)
                hit                              = target_cache
                print(f"write hit::{target_cache}\n\t:address:{sink_address}\n\t:tag:{target_tag}")
                if target_cache == 'l1_data': # L1_Data HIT -- read value into register
                    self.l1_data_cache[l1_data_way]['new'][l1_data_tag_index] = 0 # Hits will set 'new' to 0
                    evicted_entry = None
                    break
                if target_cache == 'l1_inst': # L1_Inst HIT -- Move page to L1_Data.
                    entry = {'new': 1, 'dirty':0, 'tag': target_tag, 'data': self.l1_inst_cache[target_way]['data'][target_tag_index]}
                if target_cache == 'l2': # L2 HIT -- Move page to L1_Data. Evicted entries must be kicked up the hierarchy if modified(dirty=1)
                    entry = {'new': 1, 'dirty':0, 'tag': target_tag, 'data': self.l2_cache[target_way]['data'][target_tag_index]}
                evicted_entry         = self.l1_data_cache['algorithm'](self.l1_data_cache, l1_data_way, entry) # if cache == 'l1_inst' | 'l2' -> move to 'l1_data'
                evicted_entry_address = decode.join_keys(target_way, target_cache_ways, evicted_entry['tag'], offset_bits)
                break
        if hit == None:
            l1_data_tag, l1_data_way, offset = decode.way(sink_address, l1_data_way_count, offset_bits)  # decodes address into TAG|WAY|OFFSET
            print(f"Write Miss::address:'{sink_address}'")
            entry                 = {'new': 1, 'dirty':1, 'tag': l1_data_tag, 'data': self.register[source_page]}
            evicted_entry         = self.l1_data_cache['algorithm'](self.l1_data_cache, l1_data_way, entry) # [lru/lfu/etc..](cache, way, entry)
            l1_data_tag_index     = self.l1_data_cache[l1_data_way]['tag'].index(l1_data_tag)

        if (evicted_entry != None) & ('l2' in live_cache): # Entry modified and returned to evicted_entry, instead of None
            evicted_entry_address  = decode.join_keys(target_way, target_cache_ways, evicted_entry['tag'], offset_bits)
            l2_tag, l2_way, offset = decode.way(evicted_entry_address, hierarchy['l2']['config']['ways'], offset_bits)
            entry                  = {'new': 1, 'dirty':1, 'tag': l2_tag, 'data': evicted_entry['data']} # dirty_bit=1 -> modified
            evicted_l2_entry       = self.l2_cache['algorithm'](self.l2_cache, l2_way, entry) # [lru/lfu/etc..](cache, way, entry)
            if evicted_l2_entry != None:
                evicted_l2_entry_address             = decode.join_keys(l2_way, hierarchy['l2']['config']['ways'], evicted_l2_entry['tag'], offset_bits)
                evicted_l2_entry_page                = decode.page(evicted_l2_entry_address, offset_bits)
                self.main_memory[evicted_entry_page] = evicted_l2_entry['data']
        elif evicted_entry != None:
            evicted_entry_address  = decode.join_keys(target_way, target_cache_ways, evicted_entry['tag'], offset_bits)
            evicted_entry_page = decode.page(evicted_entry_address, offset_bits)
            self.main_memory[evicted_entry_page] = evicted_entry['data']
        # -------- [ /HIERARCHY MANAGEMENT ] -------- #

        offset_key = f"{offset:x}"
        if (mode=='') | (mode=='w'):
            self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index][offset_key] = register[source_page][source_offset]
        elif mode=='b':
            self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index][offset_key] = f"{register[source_page][source_offset][:2]}{self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index][offset_key][-2:]}"
        elif mode=='p':
            self.l1_data_cache[l1_data_way]['data'][l1_data_tag_index]             = register[source_page]
        else:
            raise ValueError('Check <instruction> module for cpu.write() ModeError')
        return hit


    def tagged_prefetch(self): # BUG: properly test prefetching - No 'new' bit checking present
        next_address    = f"{(int(self.program_counter['address'],16)+16):04x}" # +16 increased page address by 1 -- 16-Bytes per page
        hierarchy       = self.cache_hierarchy
        offset_bits     = self.offset_bits
        live_cache      = [cache for cache in hierarchy] # order: l1_data?, l1_inst?, l2?
        source_page     = decode.page(next_address, offset_bits)
        hit             = None

        # if decoded<current_address>[l1_inst][way_x]['new'][index] == 1: # not accessed
        #   return None#
        # else:
        #   pass # and do all the stuff below



        # -------- [ L1 INST FOCUSED HIERARCHY MANAGEMENT ] -------- #
        for target_cache in live_cache:
            target_cache_ways              = hierarchy[target_cache]['config']['ways']
            target_tag, target_way, offset = decode.way(next_address, target_cache_ways, offset_bits) # decodes address into TAG|WAY|OFFSET - offset universal to PAGE_SIZE
            if target_tag in hierarchy[target_cache]['unit'][target_way]['tag']: # is tag present in way?
                target_tag_index                 = hierarchy[target_cache]['unit'][target_way]['tag'].index(target_tag)
                l1_inst_tag, l1_inst_way, offset = decode.way(next_address, hierarchy['l1_inst']['config']['ways'], offset_bits)  # decodes address into TAG|WAY|OFFSET
                l1_inst_tag_index                = self.l1_inst_cache[l1_inst_way]['tag'].index(l1_inst_tag)
                if self.l1_inst_cache[l1_inst_way]['new'][l1_inst_tag_index] == 1:
                    return None
                else:
                    pass
                evicted_entry_address            = decode.join_keys(target_way, target_cache_ways, target_tag, offset_bits)
                hit                              = target_cache
                print('hit in', target_cache)
                if target_cache == 'l1_inst': # L1_Inst HIT -- set 'new' to 0
                    self.l1_inst_cache[l1_inst_way]['new'][l1_inst_tag_index] = 0 # Hits will set 'new' to 0
                    evicted_entry = None
                    break
                if target_cache == 'l1_data':
                    entry = {'new': 1, 'dirty':0, 'tag': target_tag, 'data': self.l1_data_cache[target_way]['data'][target_tag_index]}
                if target_cache == 'l2': # L2 HIT -- Move page to L1_Data. Evicted entries must be kicked up the hierarchy if modified(dirty=1)
                    entry = {'new': 1, 'dirty':0, 'tag': target_tag, 'data': self.l2_cache[target_way]['data'][target_tag_index]}
                evicted_entry         = self.l1_inst_cache['algorithm'](self.l1_inst_cache, l1_inst_way, entry) # if cache == 'l1_inst' | 'l2' -> move to 'l1_data'
                evicted_entry_address = decode.join_keys(target_way, target_cache_ways, target_tag, offset_bits)
                break
        if hit == None:
            print('miss')
            l1_inst_tag, l1_inst_way, offset = decode.way(next_address, hierarchy['l1_inst']['config']['ways'], offset_bits)  # decodes address into TAG|WAY|OFFSET
            entry                 = {'new': 1, 'dirty':0, 'tag': l1_inst_tag, 'data': self.combined_memory[source_page]}
            evicted_entry         = self.l1_inst_cache['algorithm'](self.l1_inst_cache, l1_inst_way, entry) # [lru/lfu/etc..](cache, way, entry)
            evicted_entry_address = decode.join_keys(target_way, target_cache_ways, target_tag, offset_bits)
            l1_inst_tag_index     = self.l1_inst_cache[l1_inst_way]['tag'].index(l1_inst_tag)

        evicted_entry_page = decode.page(evicted_entry_address, offset_bits)
        if (evicted_entry != None) & ('l2' in live_cache): # Entry modified and returned to evicted_entry, instead of None
            l2_tag, l2_way, offset = decode.way(evicted_entry_address, hierarchy['l2']['config']['ways'], offset_bits)
            entry                  = {'new': 1, 'dirty':1, 'tag': l2_tag, 'data': evicted_entry['data']} # dirty_bit=1 -> modified
            evicted_l2_entry       = self.l2_cache['algorithm'](self.l2_cache, l2_way, entry) # [lru/lfu/etc..](cache, way, entry)
            if evicted_l2_entry != None:
                self.main_memory[evicted_entry_page] = evicted_l2_entry['data']
        elif evicted_entry != None:
            self.main_memory[evicted_entry_page] = evicted_entry['data']
        # -------- [ /L1 INST FOCUSED HIERARCHY MANAGEMENT ] -------- #


    def step_clock(self): # fully step through cpu stages
        print('----cycle----')
        counter = self.program_counter

        # [ FETCH ]
        # { prefetch } # BUG: properly test prefetching -
        # { read l1_instr_cache }
        # { pre-decode } [ TODO ]
        #   > { generate instruction_tag} [ TODO ]
        #   > { generate instruction_matrix hint } [ TODO ]


        l1_inst_tag, l1_inst_way, offset = decode.way(counter['address'], self.cache_hierarchy['l1_inst']['config']['ways'], self.offset_bits)
        l1_inst_tag_index = self.l1_inst_cache[l1_inst_way]['tag'].index(l1_inst_tag)
        raw_instruction = self.l1_inst_cache[l1_inst_way]['data'][l1_inst_tag_index][f"{offset:x}"]

        # [ DECODE ]
        # { decode instruction }
        # { populate dependancy_matrix } [ TODO ]
        # { populate execution_queue } [ TODO ]


        s16_instruction, cost, upper_field, middle_field, lower_field = instruction.decode(raw_instruction)
        instruction_entry = {'instr': s16_instruction, 'cost': cost, 'u': upper_field, 'm': middle_field, 'l': lower_field}
        print(s16_instruction)



        # [ EXECUTE ]
        # { execution_queue eviction } [ TODO ]




        # [ WRITEBACK ]
        # { writeback evicted instruction_entry } [ TODO ]
        # { dependancy_matrix eviction } [ TODO ]
        # { increment program_counter }
        counter['address'] = f"{(int(counter['address'],16)+int(counter['offset'],16)):04x}"





@cache
def main():
    print()

    s16 = Generate('s16.conf') # page_size=16 Bytes -> 8*2 Byte words -> 2B = 16-bits
    # realistic loop:
        # Prefetch to I-Cache
        # commit instruction to ROB
        # decode instruction
        # execute
        # writeback ready ROB entry
    tprint.memory(s16.read_only_memory, 'ROM')
    # s16.program_counter['offset'] = '0010'
    # write_address = '0080'

    i=0
    while i < 14: # simple test loop
        print(i)
        tprint.cache(s16.l1_inst_cache)
        s16.tagged_prefetch()
        s16.step_clock()
        i+=1


if __name__ == "__main__":
    main()
