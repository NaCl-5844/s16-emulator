def lru(cache, way_key, new_entry): # Least Recently Used
    # BUG: does not return the replaced entry
    # -- doesn't work anyway if this function updates by reference >_>

    # NOTE: generating collections.deque instead of lists can improve this code a lot
    cache[way_key]['tag'].insert(0, cache[way_key]['tag'].pop(-1)) # remove least recent, [-1], and move into most recent, [0]
    cache[way_key]['new'].insert(0, cache[way_key]['new'].pop(-1))
    cache[way_key]['data'].insert(0, cache[way_key]['data'].pop(-1))
    cache[way_key]['dirty'].insert(0, cache[way_key]['dirty'].pop(-1))
    cache[way_key]['tag'][0] = new_entry['tag']
    cache[way_key]['new'][0] = new_entry['new']
    cache[way_key]['data'][0] = new_entry['data']
    cache[way_key]['dirty'][0] = new_entry['dirty']


def lru_deque(cache, way_key, new_entry): # Least Recently Used
    # BUG: does not return the replaced entry
    # -- doesn't work anyway if this function updates by reference >_>
    cache[way_key]['tag'].insert(0, new_entry['tag'])
    cache[way_key]['new'].insert(0, new_entry['new'])
    cache[way_key]['data'].insert(0, new_entry['data'])
    cache[way_key]['dirty'].insert(0, new_entry['dirty'])

def lfu(cache, way, new_entry): # least frequently used
    return 0

def plru(cache, way, new_entry): # pseudo-lru
    return 0
