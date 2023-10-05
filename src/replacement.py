def lru(cache, way, new_entry): # Least Recently Used
    lru_dirty_bit = cache[way]['dirty'][-1]
    # print('\n#----[lru]----#\nlru page dirty?', bool(lru_dirty_bit))    # [ debug ]
    # print('\ntarget_way:', cache[way],'\nNew Entry:', new_entry)        # [ debug ]
    cache[way]['tag'].insert(0, cache[way]['tag'].pop(-1)) # remove least recent, [-1], and move into most recent, [0]
    # cache[way]['new'].insert(0, cache[way]['new'].pop(-1))
    cache[way]['data'].insert(0, cache[way]['data'].pop(-1))
    cache[way]['dirty'].insert(0, cache[way]['dirty'].pop(-1))
    cache[way]['tag'][0] = new_entry['tag']
    # cache[way]['new'][0] = new_entry['new']
    cache[way]['data'][0] = new_entry['data']
    cache[way]['dirty'][0] = new_entry['dirty']
    # generating collections.deque instead of lists can improve this code a lot

def lfu(cache, way, new_entry): # least frequently used
    return 0

def plru(cache, way, new_entry): # pseudo-lru
    return 0
