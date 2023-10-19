def lru(cache, way_key, new_entry): # Least Recently Used
    # -- doesn't work anyway if this function updates by reference >_>
    writeback_entry = None
    if len(cache[way_key]['dirty']) == cache[way_key]['dirty'].maxlen: # .maxlen equal across whole cache
        if cache[way_key]['dirty'][-1] == 1:
            writeback_entry = {
                'tag': cache[way_key]['tag'][-1],
                'new': cache[way_key]['new'][-1],
                'data': cache[way_key]['data'][-1],
                'dirty': cache[way_key]['dirty'][-1]}
    cache[way_key]['tag'].appendleft(new_entry['tag'])
    cache[way_key]['new'].appendleft(new_entry['new'])
    cache[way_key]['data'].appendleft(new_entry['data'])
    cache[way_key]['dirty'].appendleft(new_entry['dirty'])
    return writeback_entry


def lfu(cache, way, new_entry): # least frequently used
    return 0

def plru(cache, way, new_entry): # pseudo-lru
    return 0
