def memory(memory, name):
    print(f"{name}","{\n\n\t0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity

    rows_per_page = len(memory[list(memory.keys())[0]]) % 8
    if rows_per_page <= 1:
        for page in memory:
            print(f"{page.replace('age_', ':')}\t{' '.join(list(memory[page].values()))}")
    else:
        print('Page sizes >8 are yet to be implemented')
    print("}\n")

def cache(cache, name):
    print(cache)
    print(f"{name}","{\n\n","\ttag\t\b\b\b0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity
    if len(cache['way_0']['tag']) > 0:
        replacement_algorithm = cache.pop('algorithm') # Not sure how else to get around this
        for way in cache:
            print(way.replace('ay_', ':'), end='') # 'way_X' -> 'wX'
            for t in range(len(cache[way]['tag'])):
                print(f"\t{cache[way]['tag'][t]} {' '.join(list(cache[way]['data'][t].values()))}")
        print("}\n")
        cache['algorithm'] = replacement_algorithm
    else:
        print(f"\n[ CACHE EMPTY ]\n")


# if target_cache[way_key][tag].maxlen > len(target_cache[way_key]['tag']): # is way fully populated?
            #     pass
