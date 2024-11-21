import unittest 
from assembler import Assembler, VirtualMachine

class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.vm = VirtualMachine()
    
    def test_read_value(self):
        self.vm.assembler.set_value(5, 10)
        self.assertEqual(self.vm.assembler.get_value(10), 5)
    
    def test_bin_add(self):
        memory = 