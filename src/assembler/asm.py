#!/usr/bin/env python
from sys import argv
import re
# Long Term Goals:
# > Code and assemble in the command-line/shell then output to hex/bin file

class InstructionMatchError(KeyError):
    pass
class FormatFileError(ValueError):
    pass
class AssemblyError(ValueError):
    pass
class LineArgumentError(KeyError):
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
# Also assembles operation codes, e.g: ret = XXXXXXX-SSS-BBB-AAA -> 0001110-111-BBB-AAA
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
                checksum += len(clean_line) # checksum checks for consistent bit length in source assembly
                line_sum += 1 # aids in the checksum calculation
                # print(checksum, line_sum) # [ DEBUG ]
    if checksum == 16*line_sum: # lines*16 == lines*format_length
        return reference_cache #reference_cache[op] -> format
    else:
        raise FormatFileError('Inconsistent bit-lengths in format file.') # BUG 001 -- fixed

def parse(assembly, reference_cache, output_format):
    print(f"Cleaned assembly:\n{assembly}")
    bytecode = {}
    for file_line, instruction in enumerate(assembly.values()): # assemble operation codes
        operation, operands = instruction
        print(file_line, operation, operands)                    # [ DEBUG ]
        instruction_format = reference_cache.get(operation)
        if instruction_format == None: # BUG 000 -- fixed
            raise InstructionMatchError(f"Invalid instruction found: [{operation}] Please review assembly code or use a different _[x]16_format_")
        bytecode[file_line] = (reference_cache[operation],
                               operands,
                               list(set(re.findall('N|C|B|A', instruction_format))))
        # print(f"Incomplete bytecode: {bytecode[line]}\n")  # [ DEBUG ]
    for line, partial_bytecode in enumerate(bytecode.values()): # assemble operands
        code, assembly_operands, format_operands = partial_bytecode
        for operand_count in range(len(format_operands)): # Nested loop becuase f**k you. That's why.
            operand_length = len(re.findall(f"{format_operands[-1]}", code))
            operand = format_operands[-1]
            print(line, operand_count, operand, code, operand_length, assembly_operands, format_operands) # [ DEBUG ]
            target_operand = assembly_operands.rsplit(', ', 1)
            if target_operand[-1][0] == 'r':
                try:
                    target_value = int(target_operand[-1][1:])
                except ValueError:
                    raise AssemblyError(f"Error found on line {line+1}: {assembly[line]}")
            else:
                try:
                    target_value = int(target_operand[-1])
                except ValueError:
                    raise AssemblyError(f"Error found on line {line+1}: {assembly[line]}")
            if target_value < 0:
                # This AWFUL line converts a signed value into it's binary 2's complement value
                target_value = f"{((1<<operand_length)-1)+target_value+1:0{operand_length}{output_format}}"
            else:
                target_value = f"{target_value:0{operand_length}{output_format}}"
            print(target_value)
            code = (code.replace(operand*operand_length, target_value))
            assembly_operands = target_operand[0]
            format_operands.pop(-1)
            print(code)
            bytecode[line] = code
    return bytecode

def store_to_file(bytecode, file_name):
    with open(file_name, 'w') as output_file:
        for line, code in enumerate(bytecode):
            output_file.writelines(f"{bytecode[line]}\n")
            print(bytecode[line]) # [ DEBUG ]

def print_help():
    print("""
    OPTION\tDESCRIPTION

    asm.py -[format/option] [assembly] [filename]

    -h, --help\tPrint help
    -b\t\tBinary Format
    -h\t\tHexadecimal Format
    -bh\t\tBoth formats, binary first
    -hb\t\tBoth formats, hex first

    """)
    exit()

def main():
    if '-h' in argv or '--help' in argv:
        print_help() # prints help then exit()
    try:
        option = argv[-3]
        if option in ['-h', '-b', '-x', '-bx', '-bx']:
            print(option)
            input_file = argv[-2]
            output_file = argv[-1]
        else:
            raise KeyError
    except IndexError:
        print('\nA format, source assembly file and an output filename are required.')
        print_help() # prints help then exit()
        # print("Incorrect line arguments.Correct method:\npython asm.py -[b/x/bx/xb] [assembly_in] [filename_out]")
    except KeyError:
        print('\n Please use valid options.')
        print_help() # prints help then exit()
    cleaned_assembly = get_assembly(input_file)
    ref_cache = get_reference_cache(cleaned_assembly, '_s16_format_') # Hardcoded format file -- should check if it exists?
    binary_code = parse(cleaned_assembly, ref_cache, option[-1])
    store_to_file(binary_code, output_file)
    exit()

if __name__ == "__main__":
    main()




