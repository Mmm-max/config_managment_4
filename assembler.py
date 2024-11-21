import json
import struct
from bitarray import bitarray
import argparse


MACHINE_MEMORY_SIZE = 32
ASSEMBLER_MEMORY_SIZE = 32
COMANDS = {
    'LOAD_CONST': 20,
    'READ_MEM': 140,
    'WRITE_MEM': 232,
    'BIN_OP_AND': 219
}

COMMANDS_SIZE = {
    20: 7,
    140: 6,
    232: 6,
    219: 9
}

def parse_arguments():
    parser = argparse.ArgumentParser(description='Assembler for VM')
    parser.add_argument('--input', type=str, default="input/input.txt", help='Input file with commands')
    parser.add_argument('--output', type=str, default="output.bin", help='Output file with bytecode')
    parser.add_argument('--log', type=str, default="log.json", help='Log file')
    return parser.parse_args()


class Coder:
    def __init__(self):
        self.instructions = []
        
    def read(self, file_name):
        with open(file_name, 'r') as f:
            for line in f.readlines():
                if not line.strip():
                    continue
                opcode, *operands = line.strip().split(', ')
                # print(f'first operands: {operands}')
                self.instructions.append(Instruction(opcode, operands))
    
    def write(self, file_name):
        with open(file_name, 'wb') as f:
            for instruction in self.instructions:
                f.write(instruction.encode())
            
class Instruction:
    def __init__(self, opcode, operands):
        self.opcode = opcode
        self.operands = list(map(int, operands))
    
    def __str__(self):
        return f'{self.opcode} {", ".join(self.operands)}'
    
    def encode(self):
        print("endcode")
        print(f'operands {self.operands}, opcode: {self.opcode}')
        bit_arr = bitarray(endian='big')
        if self.opcode not in COMANDS:
            raise ValueError(f'Unknown command {self.opcode}')
        self.opcode = COMANDS[self.opcode]
        size = COMMANDS_SIZE[self.opcode] * 8
        if self.opcode == 20:    # const
            const, adress = self.operands
            # print(f'const {const}, adress {adress}')
            # print(f'const {const} ({bin(const)}), adress {adress} ({bin(adress)})')
            # print(f'shift opcode: {size - 7}, shift const: {size - 26}, shift adress: {size - 18}')
            packed_data = (self.opcode << (size - 8)) | (const << (size - 34)) | (adress << (size - 52))
            # for i in packed_data.to_bytes(7, byteorder='big'):
            #     print(f'i: {i} - {i:08b}')
            bit_arr.frombytes(packed_data.to_bytes(7, byteorder='big'))
        elif self.opcode == 140:   # read
            read_adress, write_adress = self.operands
            packed_data = (self.opcode << 40) | (read_adress << 22) | (write_adress << 4)
            bit_arr.frombytes(packed_data.to_bytes(6, byteorder='big'))
        elif self.opcode == 232:    # write
            read_adress, write_adress = self.operands
            packed_data = (self.opcode << 40) | (read_adress << 22) | (write_adress << 4)
            bit_arr.frombytes(packed_data.to_bytes(6, byteorder='big'))
        else:       # bin_op_and
            b_adress, bias, adress_d, adress_e = self.operands
            packed_data = (self.opcode << 64) | (b_adress << 46) | (bias << 41) | (adress_d << 23) | (adress_e << 5)
            bit_arr.frombytes(packed_data.to_bytes(9, byteorder='big'))
        
        
        
        # print(' '.join(f'{byte:02x}' for byte in bit_arr.tobytes()))
        # print(1)
        # print(bit_arr.to01())
        return bit_arr
    

class Assembler:
    def __init__(self):
        self.instructions = []
        self.memory = [0] * ASSEMBLER_MEMORY_SIZE
    
    def read_bytecode(self, file_name):
        with open(file_name, 'rb') as f:
            while True:
                opcode = f.read(1)
                if not opcode:
                    break
                opcode = int.from_bytes(opcode, byteorder='big')
                if opcode not in COMANDS.values():
                    raise ValueError(f'Unknown command {opcode}')
                bit_arr = bitarray()
                # size in bytes
                size = (COMMANDS_SIZE[opcode] - 1) # opcode already read
                match opcode:
                    case 20: # const
                        data = f.read(size)

                        # const 8th - 33th bit, adress 34th - 51th bit
                        bit_arr.frombytes(data)
                        const = int(bit_arr[0:34 - 8].to01(), 2)
                        adress = int(bit_arr[34 - 8:52 - 8].to01(), 2)
                        # print(f'bit_arr {bit_arr.to01()}')
                        # print(f'const {int(const, 2)} - {const}, adress {int(adress, 2)} - {adress}')
                        yield "LOAD_CONST", const, adress
                        
                    case 140:
                        data = f.read(size)
                        # read_adress 8th - 25th bit, write_adress 26th - 43th bit
                        bit_arr.frombytes(data)
                        read_adress = int(bit_arr[0:26 - 8].to01(), 2)
                        write_adress = int(bit_arr[26 - 8:44 - 8].to01(), 2)
                        yield "READ_MEM", read_adress, write_adress
                    case 232: # write
                        data = f.read(size)
                        # read_adress 8th - 25th bit, write_adress 26th - 43th bit
                        bit_arr.frombytes(data)
                        read_adress = int(bit_arr[0:26 - 8].to01(), 2)
                        write_adress = int(bit_arr[26 - 8:44 - 8].to01(), 2)
                        yield "WRITE_MEM", read_adress, write_adress
                    case 219: # bin_op_and
                        data = f.read(size)
                        # b_adress 8th - 25th bit, bias 26th - 40th bit, adress_d 41th - 63th bit, adress_e 64th - 88th bit
                        bit_arr.frombytes(data)
                        b_adress = int(bit_arr[0:26 - 8].to01(), 2)
                        bias = int(bit_arr[26 - 8:31 - 8].to01(), 2)
                        adress_d = int(bit_arr[31 - 8:49 - 8].to01(), 2)
                        adress_e = int(bit_arr[49 - 8:67 - 8].to01(), 2)
                        yield "BIN_OP_AND", b_adress, bias, adress_d, adress_e
                    case _:
                        raise ValueError(f'Unknown command {opcode}')
                    
    def set_value(self, value: int, adress: int) -> int:
        if len(self.memory) <= adress:
            raise ValueError(f'Adress {adress} out of memory')
        self.memory[adress] = value
        return 0
    
    def get_value(self, adress):
        if len(self.memory) <= adress:
            raise ValueError(f'Adress {adress} out of memory')
        return self.memory[adress]
    
    def add_bin(self, a, b):
        return a & b
    
    

class VirtualMachine:
    def __init__(self, logfile):
        self.memory = [0] * MACHINE_MEMORY_SIZE
        self.assembler = Assembler()
        self.logger = Logger_json(logfile)
    
    def __len_memory(self):
        return len(self.memory)
    def run(self, file_name):
        for opcode, *operands in self.assembler.read_bytecode(file_name):
            match opcode:
                case 'LOAD_CONST':
                    const, adress = operands
                    try:
                        self.assembler.set_value(const, adress)
                    except IndexError:
                        self.logger.logging({'opcode': opcode, 'const': const, 'adress': adress, 'error': 'Adress out of VM memory'})
                        self.logger.write()
                        raise ValueError(f'Adress {adress} out of VM memory')
                    self.logger.logging({'opcode': opcode, 'const': const, 'adress': adress})
                case 'READ_MEM':
                    read_adress, write_adress = operands
                    if len(self.memory) <= read_adress:
                        self.logger.logging({'opcode': opcode, 'read_adress': read_adress, 'write_adress': write_adress, 'error': 'Adress out of VM memory'})
                        self.logger.write()
                        raise ValueError(f'Adress {read_adress} out of VM memory')
                    self.assembler.set_value(self.memory[read_adress], write_adress)
                    self.logger.logging({'opcode': opcode, 'read_adress': read_adress, 'write_adress': write_adress})
                case 'WRITE_MEM':
                    read_adress, write_adress = operands
                    if len(self.memory) <= write_adress:
                        raise ValueError(f'Adress {write_adress} out of VM memory')
                    self.memory[write_adress] = self.assembler.get_value(read_adress)
                    self.logger.logging({'opcode': opcode, 'read_adress': read_adress, 'write_adress': write_adress})
                case 'BIN_OP_AND':
                    b_adress, bias, adress_d, adress_e = operands
                    if len(self.memory) <= b_adress or len(self.memory) <= adress_e or len(self.memory) <= adress_d:
                        self.logger.logging({'opcode': opcode, 'b_adress': b_adress, 'bias': bias, 'adress_d': adress_d, 'adress_e': adress_e, 'error': 'Adress out of VM memory'})
                        self.logger.write()
                        raise ValueError(f'Adress {b_adress} or {adress_e} or {adress_d} out of VM memory')
                    self.bin_op_and(b_adress, bias, adress_d, adress_e)
                    self.logger.logging({'opcode': opcode, 'b_adress': b_adress, 'bias': bias, 'adress_d': adress_d, 'adress_e': adress_e})
                case _:
                    self.logger.logging({'opcode': opcode, 'operands': operands})
                    self.logger.write()
                    raise ValueError(f'Unknown command {opcode}')
        
        print("vm memory: ", self.memory)
        print("assembler memory: ", self.assembler.memory)
        self.logger.write()

    def bin_op_and(self, b_adress: int, bias: int, adress_d: int, adress_e: int):
        if self.__len_memory() <= b_adress + bias or self.__len_memory() <= adress_e + bias or self.__len_memory() <= adress_d + bias:
            raise ValueError(f'Adress {b_adress} or {adress_e} or {adress_d} out of VM memory')
        for i in range(bias):
            # print(f'adress_d + i: {adress_d + i}, adress_e + i: {adress_e + i}')
            self.memory[adress_d + i] = self.assembler.add_bin(self.memory[b_adress + i], self.memory[adress_e + i])

    def set_memory(self, memory):
        self.memory = memory
    
    def get_memory(self):
        return self.memory
    
    def get_assember_memory(self):
        return self.assembler.memory
    
    def set_assember_memory(self, memory):
        self.assembler.memory = memory
                
class Logger_json:
    def __init__(self, file_name):
        self.log = []
        self.file_name = file_name
    
    def logging(self, message):
        self.log.append(message)
    
    def write(self):
        with open(self.file_name, 'w') as f:
            json.dump(self.log, f)
    
    def read(self):
        with open(self.file_name, 'r') as f:
            self.log = json.load(f)
    
    def print_log(self):
        self.read()
        print("log")
        for log in self.log:
            print(log)
    
def main():
    args = parse_arguments()
    coder = Coder()
    # input.txt
    coder.read(args.input)
    # output.txt
    coder.write(args.output)
    # log.json
    vm = VirtualMachine(args.log)
    # output.txt
    vm.run(args.output)
    vm.logger.print_log()

if __name__ == '__main__':
    main()