#!/usr/bin/env python3
"""Train the VLSI fault detection model"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.fault_detector import VLSIFaultDetector

def main():
    print("="*80)
    print("🚀 TRAINING VLSI FAULT DETECTION MODEL")
    print("="*80)
    
    detector = VLSIFaultDetector()
    accuracy = detector.train()
    
    print(f"\n✅ Training complete! Best accuracy: {accuracy*100:.2f}%")
    print("="*80)

if __name__ == "__main__":
    main()
