import json
import struct


class Assembler:
    def __init__(self):
        self.instructions = []
    
    def assemble(self, sourse_file, output_file, log_file):
        with open(sourse_file, 'r') as f:
            lines = f.readlines()
        
        with open(log_file, 'w') as f:
            for line in lines:
                line = line.strip()
                if line.startswith()