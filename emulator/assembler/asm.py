#!/usr/bin/env python

import re
# Goals:
# > To generate hexadecimal or binary files based on s16 assembly
# > Use "argv"s to anable multiple assembly files to be stitched into one hex/bin file
# > port and upgrade functions from "t16-assembler"

# Long Term Goals:
# > Code and assemble in the command-line/shell then output to hex/bin file
# >


# BUG List:
# 000: Cannot determine if asembly instruction not compatible with format file

class InstructionMatchError(KeyError):
    pass




def get_assembly(assembly_file):
    assembly = {}
    with open(assembly_file, 'r') as f:
        for line_number, line in enumerate(f):
            split_line = re.split(' ', line, 1)
            if len(line.split()) >= 2:
                assembly[line_number] = (split_line[0], (re.split('\n| ;', split_line[1])[0]).rstrip())
                print(f"file line number: {line_number}\nRaw line: {line}Split line: {split_line}\nAssembly: {assembly[line_number]}\n") # [ DEBUG ]
    return assembly #assembly[line_address] -> (op, 'operand string')


# Generate a {set} of (instruction,format) tuples to save time lookup/translation speed
# Also assembles operation(op) codes and sub-operation(subOp) codes, e.g:
# ret:  XXXXXXX-SSS-BBB-AAA -> 0001110-111-BBB-AAA
def get_reference_cache(assembly, format_file):
    reference_cache = {}
    operation_set = {v[0] for v in assembly.values()}
    with open(format_file, 'r') as f:
        for line in f:
            split_line = line.split()
            if len(split_line) > 1 and split_line[0] in operation_set: ### BUG 000
                reference_cache[split_line[0]] = split_line[1].replace('-', '')
    return reference_cache #reference_cache[op] -> format


def parse(assembly, reference_cache):
    print(f"Cleaned assembly:\n{assembly}")
    bytecode = {}
    for line, instruction in enumerate(assembly.values()):
        operation = instruction[0]
        operands = instruction[1]
        print(line, operation, operands) # [ DEBUG ]
        instruction_format = reference_cache.get(operation)
        if instruction_format == None:
            raise InstructionMatchError(f"Invalid instruction found: [{operation}] Please review assembly code or use a different _[x]16_format_")
        print(f"findall: {re.findall('N|C|B|A', instruction_format)}")




        # raise InstructionMatchError:





cleaned_assembly = get_assembly('test_asm.s16')
ref_cache = get_reference_cache(cleaned_assembly, '_s16_format_')
print(ref_cache)
parse(cleaned_assembly, ref_cache)

