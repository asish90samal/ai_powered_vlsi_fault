from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / 'models'
REPORTS_DIR = PROJECT_ROOT / 'reports'
VISUALIZATIONS_DIR = PROJECT_ROOT / 'visualizations'

MODEL_FILE = MODELS_DIR / 'best_model.pkl'
TRAINING_SAMPLES = 5000
TEST_SIZE = 0.2
RANDOM_STATE = 42

FAULT_TYPES = ['no_fault', 'stuck_at_0', 'stuck_at_1', 'bridging_fault',
               'open_circuit', 'delay_fault', 'transition_fault',
               'logic_error', 'timing_violation']

FEATURE_NAMES = ['input_transitions', 'toggle_rate', 'signal_strength',
                 'output_mismatch', 'expected_vs_actual', 'output_stability',
                 'propagation_delay', 'setup_time_margin', 'hold_time_margin',
                 'power_consumption', 'current_spike', 'pattern_similarity',
                 'error_pattern_length', 'consecutive_errors']
