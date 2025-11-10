import re
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import REPORTS_DIR
from .feature_extractor import FeatureExtractor
from .simulator import VerilogSimulator
from .waveform_generator import WaveformGenerator

# Import detector globally (will be passed in)
detector = None

class CircuitAnalyzer:
    def __init__(self, fault_detector):
        global detector
        detector = fault_detector
        self.simulator = VerilogSimulator()
        self.enable_waveform = True
    
    def analyze_circuit(self, verilog_code, testbench_code, circuit_name=None):
        print("="*80)
        print("ANALYZING CIRCUIT")
        print("="*80)
        
        match = re.search(r'module\s+(\w+)', verilog_code)
        module_name = match.group(1) if match else 'test_module'
        circuit_name = circuit_name or module_name
        
        print(f"\nModule: {module_name}")
        print("\n1. Simulating...")
        sim_result = self.simulator.simulate(verilog_code, testbench_code, module_name)
        print("   Done")
        
        print("\n2. Extracting features...")
        features = FeatureExtractor.extract_features(
            verilog_code, testbench_code,
            sim_result.get('expected', ''),
            sim_result.get('actual', '')
        )
        print("   Done")
        
        print("\n3. AI Fault Detection...")
        fault_type, confidence, top3, model_info = detector.detect_faults(features)
        
        print("\n4. Generating waveform...")
        if self.enable_waveform:
            try:
                waveform_path = WaveformGenerator.generate(verilog_code, testbench_code, circuit_name)
                print(f"   Saved: {waveform_path.name}")
            except Exception as e:
                print(f"   Skipped: {e}")
                waveform_path = None
        
        print("\n" + "="*80)
        print("RESULTS")
        print("="*80)
        print(f"\n{model_info}")
        print(f"\nFault: {fault_type.upper().replace('_', ' ')}")
        print(f"Confidence: {confidence:.2f}%")
        print(f"\nTop 3:")
        for i, (f, p) in enumerate(top3, 1):
            print(f"   {i}. {f.replace('_', ' '):<25} {p:>6.2f}%")
        
        REPORTS_DIR.mkdir(exist_ok=True, parents=True)
        report_path = REPORTS_DIR / f'{circuit_name}_report.txt'
        with open(report_path, 'w') as f:
            f.write(f"VLSI Fault Report\n")
            f.write(f"Module: {module_name}\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write(f"Fault: {fault_type}\n")
            f.write(f"Confidence: {confidence:.2f}%\n")
        
        print(f"\nReport: {report_path}")
        if waveform_path:
            print(f"Waveform: {waveform_path}")
        print("="*80)
