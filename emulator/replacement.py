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
