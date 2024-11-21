import unittest 
from assembler import Assembler, VirtualMachine

class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.vm = VirtualMachine("log.json")
    
    def test_read_value(self):
        self.vm.assembler.set_value(5, 10)
        self.assertEqual(self.vm.assembler.get_value(10), 5)
    
    def test_bin_add(self):
        memory = [10, 10, 10, 0, 10, 5, 6, 0, 0, 0, 0, 0]
        self.vm.set_memory(memory)
        self.vm.bin_op_and(0, 3, 8, 4)
        print(self.vm.get_memory())
        self.assertEqual(self.vm.get_memory(), [10, 10, 10, 0, 10, 5, 6, 0, 10, 0, 2, 0])