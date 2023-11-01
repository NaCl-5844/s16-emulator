#!/usr/bin/env python
from sys import argv
import os.path
import re

# TODO:
# > Add edgecase for <inc> and <dec>, which adds n+1 and subtracts n+1 respectively

# Long Term Goals:
# > Assembly files with formats .s16 and .t16 will automatically pick the correct _format_ file
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
    with open(os.path.join(os.path.dirname(__file__), 'assembly', assembly_file), 'r') as f:
        for line_number, line in enumerate(f):
            split_line = re.split(' ', line, 1)
            if (type(split_line) == int) or ('_' in split_line):
                raise AssemblyError
            if len(split_line) >= 2:
                if split_line[1][0] == ';':
                    assembly[line_number] = (split_line[0], None)
                else:
                    assembly[line_number] = (split_line[0], (re.split('\n| ;', split_line[1])[0]).rstrip())
    return assembly #assembly[line_address] -> (op, 'operand string')

def get_reference_cache(assembly, format_file): # Generate a {set} of (instruction,format) tuples to save time lookup/translation speed
    reference_cache = {}
    operation_set = {v[0] for v in assembly.values()}
    with open(format_file, 'r') as f: # file also contains opcodes(X) and subops(S), e.g: XXXXXXX-SSS-BBB-AAA -> 0001110-111-BBB-AAA
        checksum, line_sum = 0, 0 # both variables equal zero
        for line in f:
            split_line = line.split()
            if (len(split_line) > 1) and (split_line[0] in operation_set):
                clean_line = split_line[1].replace('-', '')
                operand_set = set(re.findall('N|C|B|A', clean_line))
                operand_dict = {operand:len(re.findall(operand, clean_line)) for operand in operand_set}
                reference_cache[split_line[0]] = {'format': clean_line, **operand_dict}
                print(operand_dict)
                checksum += len(clean_line) # checksum checks for consistent bit length in source assembly
                line_sum += 1 # aids in the checksum calculation
    if checksum == 16*line_sum: # lines*16 == lines*format_length
        return reference_cache #reference_cache[op] -> format
    else:
        raise FormatFileError('Inconsistent bit-lengths in format file.')

def get_addressing_modes(format_file):
    all_instructions = []
    with open(format_file, 'r') as f:
        for instruction_format in f:
            split_instruction_format = instruction_format.split()
            if (len(split_instruction_format) > 2) and ('_' not in instruction_format):
                all_instructions.insert(0, split_instruction_format[-1])
    print(set(all_instructions))

def get_assembly_instructions(format_file):
    all_instructions = []
    with open(format_file, 'r') as f:
        for instruction_format in f:
            split_instruction_format = instruction_format.split()
            if (len(split_instruction_format) > 2) and ('_' not in instruction_format):
                all_instructions.insert(0, split_instruction_format[0])
    print(set(all_instructions))

def parse(assembly, reference_cache, implement_formats):
    bytecode = {}
    for line, instruction in enumerate(assembly.values()):
        operation = instruction[0]
        operands = instruction[1]
        config = dict(reference_cache[operation]) # dict() creates a new instance/object? -- if config is a reference, pop() will delete values inside reference_cache
        partial_bytecode = config.pop('format')
        cleaned_format = partial_bytecode.strip('01XSZ')
        if cleaned_format == '':
            bytecode[line] = partial_bytecode
            continue # No assembling required, move onto next iteration
        for operand_count in config:
            format_operand = cleaned_format[0]
            bit_length = config[format_operand]
            assembly_operand = operands.split(',', 1)[0]
            if ((operation == 'inc') or (operation == 'dec')) and ((assembly_operand == '0') or (assembly_operand[0] == '-')):
                    raise AssemblyError(f" Invalid negative or zero integer usage on line {line+1}: {assembly[line]}")

            if (assembly_operand[0] == 'r') and assembly_operand[1:].isdigit():
                binary_operand = f"{int(assembly_operand[1:]):0{bit_length}b}"
            elif assembly_operand.isdigit():
                if (operation == 'inc') or (operation == 'dec'):
                    binary_operand = f"{int(assembly_operand)-1:0{bit_length}b}"
                else:
                    binary_operand = f"{int(assembly_operand):0{bit_length}b}"
            elif (assembly_operand[0] == '-') and assembly_operand[1:].isdigit():
                binary_operand = f"{((1<<bit_length)-1)-int(assembly_operand[1:])+1:0{bit_length}b}"
            else:
                raise AssemblyError(f"Error found on line {line+1}: {assembly[line]}")
            operands = operands.removeprefix(f"{assembly_operand},").strip()
            cleaned_format = cleaned_format.strip(format_operand)
            partial_bytecode = partial_bytecode.replace(format_operand * bit_length, binary_operand) # e.g. 'A' * 4 = 'AAAA'
        bytecode[line] = partial_bytecode
        print(locals())
    return bytecode

def store_to_file(bytecode, file_name):
    with open(os.path.join(os.path.dirname(__file__), os.pardir, 'bytecode', file_name), 'w') as output_file:
        for line, code in enumerate(bytecode):
            output_file.writelines(f"{bytecode[line]}\n")
            print(bytecode[line]) # [ DEBUG ]

def print_help(ExtraComments=""):
    print(ExtraComments)
    print("""
    OPTION\tDESCRIPTION

    asm.py -[format/option] [assembly file] [output file]

    -h, --help\tPrint help
    -b\t\tBinary Format
    -h\t\tHexadecimal Format
    -bh\t\tBoth formats, binary first
    -hb\t\tBoth formats, hex first


    EXTRAS\tOPTIONS

    asm.py --get [item]

    --get\taddressingModes, instructions

    Place assembly in /assembly
    Generated binaries are placed in s16-emulator/src/bytecode
    """)
    exit()

def main():
    if '-h' in argv or '--help' in argv:
        print_help() # prints help then exit()
    elif '--get' in argv:
        try:
            if argv[argv.index('--get')+1] == 'addressingModes':
               get_addressing_modes('_s16_format_')
            if argv[argv.index('--get')+1] == 'instructions':
               get_assembly_instructions('_s16_format_')
        except LineArgumentError:
            print_help()
        except IndexError:
            print_help('\n    ERROR: --get must be followed by an item!')
    else:
        try:
            option = argv[-3]
            if option in ['-h', '-b', '-x', '-bx', '-bx']:
                print(option)
                input_file = argv[-2]
                output_file = argv[-1]
            else:
                raise KeyError
        except IndexError:
            print('\nA format, source assembly file, and an output filename required.')
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




