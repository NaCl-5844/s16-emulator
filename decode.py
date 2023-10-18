def page(hex_address, offset_bits):
    bin_address = f"{int(hex_address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
    page        = int(bin_address[0:-(offset_bits)], 2) # The remaining bits address the page
    page_key    = f"page_{page:0x}"
    # print('\n#----[decode.page]----#\n','offset_bits: ',offset_bits)    # [ debug ]
    # print('bin_address: ',bin_address,'page:',page)                     # [ debug ]
    return page_key

def way(hex_address, way_bits, offset_bits):
    bin_address = f"{int(hex_address, 16):0{16}b}" # convert address into binary -- Hardcoded 16-bit
    way         = bin_address[-(way_bits+offset_bits-1):-offset_bits]
    way_key     = f"way_{int(way, 2):x}"
    tag         = f"{int(bin_address[way_bits:-(offset_bits+1)], 2):0{4}x}"
    offset      = int(bin_address[-(offset_bits):15], 2) << 1 # Extracting the upper most bits of the address
    # print('\n#----[decode.way]----#\n','\bway_bits:',way_bits-1,'offset_bits:',offset_bits) # [ debug ]
    # print(f"bin_address: 0b{bin_address}, way: 0b{way}")                                    # [ debug ]
    return tag, way_key, offset

def join_keys(way_key, ways, tag, offset_bits): # joins way and tag keys of evicted cache entries
    way_bits       = (ways - 1).bit_length()
    tag            = f"{int(tag, 16):0{16-way_bits-offset_bits}b}"
    way            = f"{int(way_key[4:], 16):0{way_bits}b}"
    offset         = f"{0:0{offset_bits}b}"
    binary_address = f"{tag}{way}{offset}"
    return f"{int(binary_address, 2):04x}"


def register(register_address):
    translate = { # 2-bit, 3-bit and 4-bit register addresses
        '0000': ('page_0', '0'),'000': ('page_0', '0'),
        '0001': ('page_0', '2'),'001': ('page_0', '2'),
        '0010': ('page_0', '4'),'010': ('page_0', '4'),
        '0011': ('page_0', '6'),'011': ('page_0', '6'),
        '0100': ('page_0', '8'),'100': ('page_0', '8'),
        '0101': ('page_0', 'a'),'101': ('page_0', 'a'),
        '0110': ('page_0', 'c'),'110': ('page_0', 'c'),
        '0111': ('page_0', 'e'),'111': ('page_0', 'e'),
        '1000': ('page_1', '0'),'00':  ('page_0', '0'),
        '1001': ('page_1', '2'),'01':  ('page_0', '2'),
        '1010': ('page_1', '4'),'10':  ('page_0', '4'),
        '1011': ('page_1', '6'),'11':  ('page_0', '6'),
        '1100': ('page_1', '8'),
        '1101': ('page_1', 'a'),
        '1110': ('page_1', 'c'),
        '1111': ('page_1', 'e'),
        }
    return translate[register_address]






