def page(Decode, hex_address, offset_bits):
        bin_address = f"{int(hex_address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
        page = int(bin_address[0:-(offset_bits)], 2) # The remaining bits address the page
        print('\n#----[Read.memory]----#\n','offset_bits: ',offset_bits)    # [ debug ]
        print('bin_address: ',bin_address,'page:',page)                     # [ debug ]
        page_key = f"page_{page:0x}"
        return page_key

def way(Decode, hex_address, way_bits, offset_bits):
    bin_address = f"{int(hex_address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
    way = bin_address[-(way_bits+offset_bits-1):-offset_bits]
    way_key = f"way_{int(way, 2):x}"
    print('\n#----[Read.cache]----#\n','\bway_bits:',way_bits-1,'offset_bits:',offset_bits) # [ debug ]
    print(f"bin_address: 0b{bin_address}, way: 0b{way}")                                    # [ debug ]
    return bin_address, way_key
