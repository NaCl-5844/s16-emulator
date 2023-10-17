def lru(cache, way_key, new_entry): # Least Recently Used
    # -- doesn't work anyway if this function updates by reference >_>
    writeback_entry = None
    if len(cache[way_key]['dirty']) > 0:
        if cache[way_key]['dirty'][-1] == 1:
            writeback_entry = {
                'tag': cache[way_key]['tag'][-1],
                'new': cache[way_key]['new'][-1],
                'data': cache[way_key]['data'][-1],
                'dirty': cache[way_key]['dirty'][-1]}
    cache[way_key]['tag'].insert(0, new_entry['tag'])
    cache[way_key]['new'].insert(0, new_entry['new'])
    cache[way_key]['data'].insert(0, new_entry['data'])
    cache[way_key]['dirty'].insert(0, new_entry['dirty'])
    return writeback_entry


def lfu(cache, way, new_entry): # least frequently used
    return 0

def plru(cache, way, new_entry): # pseudo-lru
    return 0
