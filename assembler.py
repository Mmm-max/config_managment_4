import json
import struct
from bitarray import bitarray

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

VM_MEMORY = 200
class Coder:
    def __init__(self):
        self.instructions = []
        
    def read(self, file_name):
        with open(file_name, 'r') as f:
            for line in f.readlines():
                opcode, *operands = line.strip().split(', ')
                print(f'first operands: {operands}')
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
        print(f'operands {self.operands}')
        bit_arr = bitarray(endian='big')
        if self.opcode not in COMANDS:
            raise ValueError(f'Unknown command {self.opcode}')
        self.opcode = COMANDS[self.opcode]
        size = COMMANDS_SIZE[self.opcode] * 8
        if self.opcode == 20:    # const
            const, adress = self.operands
            print(f'const {const}, adress {adress}')
            print(f'const {const} ({bin(const)}), adress {adress} ({bin(adress)})')
            print(f'shift opcode: {size - 7}, shift const: {size - 26}, shift adress: {size - 18}')
            packed_data = (self.opcode << (size - 8)) | (const << (size - 34)) | (adress << (size - 52))
            for i in packed_data.to_bytes(7, byteorder='big'):
                print(f'i: {i} - {i:08b}')
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
        
        
        
        print(' '.join(f'{byte:02x}' for byte in bit_arr.tobytes()))
        print(1)
        print(bit_arr.to01())
        return bit_arr
    

class Assembler:
    def __init__(self):
        self.instructions = []
        self
    
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
                        print("const")
                        data = f.read(size)
                        # const 8th - 33th bit, adress 34th - 51th bit
                        bit_arr.frombytes(data)
                        # const = int(bit_arr[8:34].to01(), 2)
                        # adress = int(bit_arr[34:52].to01(), 2)
                        const = bit_arr[0:34 - 8].to01()
                        adress = bit_arr[34 - 8:52 - 8].to01()
                        print(f'bit_arr {bit_arr.to01()}')
                        print(f'const {int(const, 2)} - {const}, adress {int(adress, 2)} - {adress}')
                        yield (opcode, [adress])
                        
                    case 140:
                        data = f.read(size)
                        # read_adress 8th - 25th bit, write_adress 26th - 43th bit
                        bitarray.frombytes(data)
                        read_adress = int(bit_arr[0:26 - 8].to01(), 2)
                        write_adress = int(bit_arr[26 - 8:44 - 8].to01(), 2)
                        yield
                    case 232: # write
                        data = f.read(size)
                        # read_adress 8th - 25th bit, write_adress 26th - 43th bit
                        bitarray.frombytes(data)
                        read_adress = int(bit_arr[0:26 - 8].to01(), 2)
                        write_adress = int(bit_arr[26 - 8:44 - 8].to01(), 2)
                    case 219: # bin_op_and
                        data = f.read(size)
                        # b_adress 8th - 25th bit, bias 26th - 40th bit, adress_d 41th - 63th bit, adress_e 64th - 88th bit
                        bitarray.frombytes(data)
                        b_adress = int(bit_arr[0:26 - 8].to01(), 2)
                        bias = int(bit_arr[26 - 8:31 - 8].to01(), 2)
                        adress_d = int(bit_arr[31 - 8:49 - 8].to01(), 2)
                        adress_e = int(bit_arr[49 - 8:67 - 8].to01(), 2)
                    case _:
                        raise ValueError(f'Unknown command {opcode}')
    
    # def const()

class VirtualMachine:
    def __init__(self):
        self.memory = [0] * VM_MEMORY
        assembler = Assembler()

def main():
    coder = Coder()
    coder.read('input.txt')
    coder.write('output.bin')
    
    assembler = Assembler()
    assembler.read_bytecode('output.bin')