import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.feature_extractor import FeatureExtractor
from src.fault_detector import VLSIFaultDetector
from src.waveform_generator import WaveformGenerator
from src.simulator import VerilogSimulator
from PIL import Image

st.set_page_config(page_title="VLSI Fault Detection", page_icon="🔬", layout="wide")

# Initialize
@st.cache_resource
def load_model():
    detector = VLSIFaultDetector()
    if not detector.load_model():
        st.warning("Model not found. Training...")
        detector.train()
    return detector

detector = load_model()
simulator = VerilogSimulator()

# Header
st.title("🔬 AI-Powered VLSI Fault Detection")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Options")
    template = st.selectbox("Load Template", 
        ["Custom", "AND Gate", "D Flip-Flop", "Faulty AND (SA0)", "Timing Fault"])
    
    if template == "AND Gate":
        st.session_state['v_code'] = "module and_gate(input a, b, output y);\n  assign y = a & b;\nendmodule"
        st.session_state['tb_code'] = "module tb;\n  reg a, b; wire y;\n  and_gate uut(.a(a), .b(b), .y(y));\n  initial begin\n    a=0;b=0;#10;\n    a=1;b=1;#10;\n    $finish;\n  end\nendmodule"
    elif template == "Faulty AND (SA0)":
        st.session_state['v_code'] = "module and_gate(input a, b, output y);\n  assign y = 1'b0; // FAULT\nendmodule"
        st.session_state['tb_code'] = "module tb;\n  reg a, b; wire y;\n  and_gate uut(.a(a), .b(b), .y(y));\n  initial begin\n    a=0;b=0;#10;\n    a=1;b=1;#10;\n    $finish;\n  end\nendmodule"

# Main
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Verilog Code")
    v_code = st.text_area("Module", st.session_state.get('v_code', 
        "module and_gate(input a, b, output y);\n  assign y = a & b;\nendmodule"), height=300)

with col2:
    st.subheader("🧪 Testbench")
    tb_code = st.text_area("Testbench", st.session_state.get('tb_code',
        "module tb;\n  reg a,b; wire y;\n  and_gate uut(.a(a),.b(b),.y(y));\n  initial begin\n    a=0;b=0;#10;\n    a=1;b=1;#10;\n  end\nendmodule"), height=300)

st.session_state['v_code'] = v_code
st.session_state['tb_code'] = tb_code

if st.button("🚀 Analyze Circuit", type="primary"):
    with st.spinner("Analyzing..."):
        import re
        match = re.search(r'module\s+(\w+)', v_code)
        circuit_name = match.group(1) if match else 'circuit'
        
        # Simulate
        sim_result = simulator.simulate(v_code, tb_code, circuit_name)
        
        # Extract features
        features = FeatureExtractor.extract_features(v_code, tb_code,
            sim_result.get('expected', ''), sim_result.get('actual', ''))
        
        # Detect
        fault_type, confidence, top3, model_info = detector.detect_faults(features)
        
        # Generate waveform
        try:
            waveform_path = WaveformGenerator.generate(v_code, tb_code, circuit_name)
        except:
            waveform_path = None
        
        # Display results
        st.markdown("---")
        st.success("✅ Analysis Complete!")
        
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            st.metric("Fault Detected", fault_type.replace('_', ' ').title())
            st.metric("Confidence", f"{confidence:.1f}%")
        
        with col_res2:
            st.subheader("Top 3 Predictions")
            for i, (f, p) in enumerate(top3, 1):
                st.progress(p/100, text=f"{i}. {f.replace('_', ' ').title()}: {p:.1f}%")
        
        if waveform_path and waveform_path.exists():
            st.markdown("---")
            st.subheader("📊 Waveform Analysis")
            st.image(str(waveform_path), use_container_width=True)
