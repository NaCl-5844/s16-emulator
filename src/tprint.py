def memory(memory, name=""):
    print(f"{name}","{\n\n\t0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity

    rows_per_page = len(memory[list(memory.keys())[0]]) % 8
    if rows_per_page <= 1:
        for page in memory:
            print(f"{page.replace('age_', ':')}\t{' '.join(list(memory[page].values()))}")
    else:
        print('Page sizes >8 are yet to be implemented')
    print("}\n")


def cache(cache, name=""):
    replacement_algorithm = cache.pop('algorithm') # Not sure how else to get around this
    max_length = cache['way_0']['tag'].maxlen # maxlen is consisgtent across all ways
    print(f"{name}","{\n\n","\ttag\t\b\b\b0x0  0x2  0x4  0x6  0x8  0xa  0xc  0xe\n") # Hardcoded for simplicity
    for way in cache:
        population = len(cache[way]['tag'])
        print(way.replace('ay_', ':'), end='') # 'way_X' -> 'w:X'
        for index, tag in enumerate(cache[way]['tag']): # prints current population of cache
            print(f"\t{tag} {' '.join(list(cache[way]['data'][index].values()))}")
        for unpopulated in range(max_length-population): # fills in unpopulated cache entries
            empty_page = ['0000' for word in range(8)]
            print(f"\t____ {' '.join(empty_page)}")

    print("}\n")
    cache['algorithm'] = replacement_algorithm


