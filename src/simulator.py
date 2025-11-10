import subprocess
import shutil

class VerilogSimulator:
    def __init__(self):
        self.iverilog_available = shutil.which('iverilog') is not None
    
    def simulate(self, verilog_code, testbench_code, module_name):
        # Mock simulation for demo
        has_fault = any(kw in verilog_code for kw in ['1\'b0;', '1\'b1;', '#25', '#15'])
        
        if has_fault:
            if "1'b0" in verilog_code:
                return {'success': True, 'output': 'Fault detected', 
                       'expected': '01011', 'actual': '00000'}
            elif "1'b1" in verilog_code:
                return {'success': True, 'output': 'Fault detected',
                       'expected': '01011', 'actual': '11111'}
            else:
                return {'success': True, 'output': 'Fault detected',
                       'expected': '01011', 'actual': '01001'}
        else:
            return {'success': True, 'output': 'Simulation complete',
                   'expected': '01011', 'actual': '01011'}
