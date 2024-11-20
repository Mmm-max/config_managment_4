import json
import struct
from bitarray import bitarray

COMANDS = {
    'LOAD_CONST': 20,
    'READ_MEM': 140,
    'WRITE_MEM': 232,
    'BIN_OP_AND': 83
}

COMMANDS_SIZE = {
    20: 7,
    140: 6,
    232: 6,
    83: 9
}

class Coder:
    def __init__(self):
        self.instructions = []
        
    def read(self, file_name):
        with open(file_name, 'r') as f:
            for line in f.readlines():
                opcode, *operands = line.strip().split(' ')
                self.instructions.append(Instruction(opcode, operands))
    
    def write(self, file_name):
        with open(file_name, 'wb') as f:
            for instruction in self.instructions:
                f.write(instruction.encode())
            
class Instruction:
    def __init__(self, opcode, *operands):
        self.opcode = opcode
        self.operands = operands
    
    def __str__(self):
        return f'{self.opcode} {", ".join(self.operands)}'
    
    def encode(self):
        print("endcode")
        print(f'operands {self.operands}')
        bit_arr = bitarray(endian='big')
        if self.opcode not in COMANDS:
            raise ValueError(f'Unknown command {self.opcode}')
        self.opcode = COMANDS[self.opcode]
        if self.opcode == 20:    # const
            const, adress = self.operands
            packed_data = (self.opcode << 48) | (const << 24) | (adress << 6)
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
    
    def read_bytecode(self, file_name):
        with open(file_name, 'rb') as f:
            while True:
                byte = f.read(1)
                if not byte:
                    break
                self.instructions.append(byte)