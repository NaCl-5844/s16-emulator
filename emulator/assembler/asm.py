#!/usr/bin/env python

import re
# Goals:
# > To generate hexadecimal or binary files based on s16 assembly
# > Use "argv"s to anable multiple assembly files to be stitched into one hex/bin file
# > port and upgrade functions from "t16-assembler"

# Long Term Goals:
# > Code and assemble in the command-line/shell then output to hex/bin file
# >





def get_assembly(assembly_file):
    assembly = {}
    with open(assembly_file, 'r') as f:
        for k, v in enumerate(f):
            split_line = re.split(' ', v, 1)
            if len(v.split()) >= 2:
                assembly[k] = (split_line[0], re.split(' \n| ;', split_line[1])[0])
                print(f"file line number: {k}\nRaw line: {v}Split line: {split_line}\nAssembly: {assembly[k]}\n") # [ DEBUG ]
    return assembly #assembly[line_address] -> (op, 'operand string')


# will contain a {set} of (instruction,format) tuples to save time lookup/translation speed
def get_reference_cache(cleaned_assembly, format_file):
    reference_cache = {}
    operation_set = {v[0] for v in cleaned_assembly.values()}
    with open(format_file, 'r') as f:
        for line in f:
            split_line = line.split()
            if len(split_line) > 1 and split_line[0] in operation_set:
                reference_cache[split_line[0]] = split_line[1].replace('-', '')
    return reference_cache #reference_cache[op] -> format



cleaned_assembly = get_assembly('test_asm.s16')
ref_cache = get_reference_cache(cleaned_assembly, '_s16_format_')
print(ref_cache)
