import re

class FeatureExtractor:
    @staticmethod
    def extract_features(verilog_code, testbench_code, expected_out="", actual_out=""):
        features = {
            'input_transitions': len(re.findall(r'[01]', testbench_code)),
            'toggle_rate': 0.5, 'signal_strength': 1.0, 'output_mismatch': 0,
            'expected_vs_actual': 1.0, 'output_stability': 1.0,
            'propagation_delay': 10.0, 'setup_time_margin': 5.0,
            'hold_time_margin': 5.0, 'power_consumption': 1.0,
            'current_spike': 0.0, 'pattern_similarity': 1.0,
            'error_pattern_length': 0, 'consecutive_errors': 0,
        }
        
        if expected_out and actual_out:
            mismatches = sum(1 for e, a in zip(expected_out, actual_out) if e != a)
            features['output_mismatch'] = mismatches
            features['expected_vs_actual'] = 1 - (mismatches / max(len(expected_out), 1))
            
            consecutive, max_consecutive = 0, 0
            for e, a in zip(expected_out, actual_out):
                consecutive = consecutive + 1 if e != a else 0
                max_consecutive = max(max_consecutive, consecutive)
            features['consecutive_errors'] = max_consecutive
        
        if re.search(r'assign\s+\w+\s*=\s*1\'b0\s*;', verilog_code):
            features['signal_strength'] = 0.3
            features['output_stability'] = 0.2
        elif re.search(r'assign\s+\w+\s*=\s*1\'b1\s*;', verilog_code):
            features['signal_strength'] = 1.7
            features['output_stability'] = 0.2
        
        if '#25' in verilog_code or '#15' in verilog_code:
            features['propagation_delay'] = 90
            features['setup_time_margin'] = -5.0
        
        if 'transition' in verilog_code.lower():
            features['consecutive_errors'] = 8
            features['error_pattern_length'] = 15
        
        return features
