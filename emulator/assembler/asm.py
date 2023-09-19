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
# (fixed) 000: Cannot determine if asembly instruction not compatible with format file
# (fixed) 001: cannot determine if format file is of consistent bit-length


class InstructionMatchError(KeyError):
    pass
class FormatFileError(ValueError):
    pass
class AssemblyError(ValueError):
    pass



def get_assembly(assembly_file):
    assembly = {}
    with open(assembly_file, 'r') as f:
        for line_number, line in enumerate(f):
            split_line = re.split(' ', line, 1)
            if len(line.split()) >= 2:
                assembly[line_number] = (split_line[0], (re.split('\n| ;', split_line[1])[0]).rstrip())
                # print(f"file line number: {line_number}\nRaw line: {line}Split line: {split_line}\nAssembly: {assembly[line_number]}\n") # [ DEBUG ]
    return assembly #assembly[line_address] -> (op, 'operand string')


# Generate a {set} of (instruction,format) tuples to save time lookup/translation speed
# Also assembles operation(op) codes and sub-operation(subOp) codes, e.g:
# ret:  XXXXXXX-SSS-BBB-AAA -> 0001110-111-BBB-AAA
def get_reference_cache(assembly, format_file):
    reference_cache = {}
    operation_set = {v[0] for v in assembly.values()}
    with open(format_file, 'r') as f:
        checksum, line_sum = 0, 0 # both variables equal zero
        for line in f:
            split_line = line.split()
            if len(split_line) > 1 and split_line[0] in operation_set:
                clean_line = split_line[1].replace('-', '')
                reference_cache[split_line[0]] = clean_line
                checksum += len(clean_line)
                line_sum += 1
                # print(checksum, line_sum) # [ DEBUG ]
    if checksum == 16*line_sum: # lines*16 == lines*format_length
        return reference_cache #reference_cache[op] -> format
    else:
        raise FormatFileError('Inconsistent bit-lengths in format file.') # BUG 001 -- fixed


def parse(assembly, reference_cache):
    print(f"Cleaned assembly:\n{assembly}")
    bytecode = {}
    for line, instruction in enumerate(assembly.values()): # assemble operation codes
        operation, operands = instruction
        print(line, operation, operands)                    # [ DEBUG ]
        instruction_format = reference_cache.get(operation)
        if instruction_format == None: # BUG 000 -- fixed
            raise InstructionMatchError(f"Invalid instruction found: [{operation}] Please review assembly code or use a different _[x]16_format_")
        bytecode[line] = (reference_cache[operation],
                          operands,
                          list(set(re.findall('N|C|B|A', instruction_format))))
        # print(f"Incomplete bytecode: {bytecode[line]}\n")  # [ DEBUG ]
    for line, partial_bytecode in enumerate(bytecode.values()): # assemble operands
        code, assembly_operands, format_operands = partial_bytecode
        for operand_count, value in enumerate(format_operands): # Nested loop becuase f**k you. That's why.
            operand_len = len(re.findall(f"{format_operands[-1]}", code))
            print(line, operand_count, value, code, operand_len, assembly_operands) # [ DEBUG ]
            target_operand = assembly_operands.rsplit(', ', 1)[-1]
            if target_operand[0] == 'r':
                try:
                    target_value = int(target_operand[1:])
                    print(target_value)
                except AssemblyError:
                    print(f"Error found in {partial_bytecode}")
            else:
                try:
                    target_value = int(target_operand)
                    print(target_value)
                except AssemblyError:
                    print(f"Error found in {partial_bytecode}")
            if target_value < 0:
                target_value = None



















cleaned_assembly = get_assembly('test_asm.s16')
ref_cache = get_reference_cache(cleaned_assembly, '_s16_format_')
print(ref_cache)
parse(cleaned_assembly, ref_cache)

