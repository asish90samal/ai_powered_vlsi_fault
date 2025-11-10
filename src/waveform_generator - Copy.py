import numpy as np
import matplotlib.pyplot as plt
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import VISUALIZATIONS_DIR

class WaveformGenerator:
    @staticmethod
    def generate(verilog_code, testbench_code, circuit_name):
        signals = WaveformGenerator._extract_signals(testbench_code)
        waveform_data = WaveformGenerator._generate_data(signals, verilog_code)
        return WaveformGenerator._plot(waveform_data, circuit_name)
    
    @staticmethod
    def _extract_signals(testbench):
        signals = []
        signals.extend(re.findall(r'reg\s+(\w+)', testbench))
        signals.extend(re.findall(r'wire\s+(\w+)', testbench))
        return list(set(signals))
    
    @staticmethod
    def _generate_data(signals, verilog_code):
        time = np.arange(0, 100, 1)
        data = {'time': time}
        
        has_stuck_0 = '1\'b0' in verilog_code
        has_stuck_1 = '1\'b1' in verilog_code
        has_timing = '#25' in verilog_code or '#15' in verilog_code
        
        for sig in signals:
            if 'clk' in sig.lower():
                data[sig] = np.array([i % 20 < 10 for i in time], dtype=int)
            elif 'rst' in sig.lower():
                data[sig] = np.array([1 if i < 12 else 0 for i in time], dtype=int)
            elif sig.lower() in ['q', 'y', 'out']:
                wave = np.zeros(len(time), dtype=int)
                if has_stuck_0:
                    wave[:] = 0
                elif has_stuck_1:
                    wave[12:] = 1
                elif has_timing:
                    wave[25:40] = 1
                    wave[65:80] = 1
                else:
                    wave[20:40] = 1
                    wave[60:80] = 1
                data[sig] = wave
            else:
                wave = np.zeros(len(time), dtype=int)
                for i, t in enumerate(time):
                    if t in [20, 40, 60, 80]:
                        wave[i:] = 1 - wave[i-1] if i > 0 else 1
                data[sig] = wave
        return data
    
    @staticmethod
    def _plot(data, circuit_name):
        signals = [k for k in data.keys() if k != 'time']
        time = data['time']
        
        fig, axes = plt.subplots(len(signals), 1, figsize=(14, len(signals)*1.5))
        if len(signals) == 1:
            axes = [axes]
        
        fig.suptitle(f'Waveform - {circuit_name}', fontsize=16, fontweight='bold')
        
        for idx, sig in enumerate(signals):
            ax = axes[idx]
            wave = data[sig]
            
            for i in range(len(time)-1):
                ax.plot([time[i], time[i+1]], [wave[i], wave[i]], 'b-', linewidth=2)
                if wave[i] != wave[i+1]:
                    ax.plot([time[i+1], time[i+1]], [wave[i], wave[i+1]], 'b-', linewidth=2)
            
            ax.set_ylabel(sig, fontsize=11, fontweight='bold', rotation=0, ha='right')
            ax.set_ylim(-0.3, 1.3)
            ax.set_yticks([0, 1])
            ax.grid(True, alpha=0.3)
            
            if idx < len(signals)-1:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel('Time (ns)', fontsize=12)
        
        plt.tight_layout()
        VISUALIZATIONS_DIR.mkdir(exist_ok=True, parents=True)
        path = VISUALIZATIONS_DIR / f'{circuit_name}_waveform.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        return path
