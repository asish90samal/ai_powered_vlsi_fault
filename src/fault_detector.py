import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import *

class VLSIFaultDetector:
    def __init__(self):
        self.best_model = None
        self.best_model_name = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.fault_types = FAULT_TYPES
        self.feature_names = FEATURE_NAMES
        self.trained = False
    
    def generate_training_data(self, n_samples=TRAINING_SAMPLES):
        data = []
        for _ in range(n_samples):
            sample = {
                'input_transitions': np.random.randint(0, 100),
                'toggle_rate': np.random.uniform(0, 1),
                'signal_strength': np.random.uniform(0.5, 1.5),
                'output_mismatch': np.random.randint(0, 50),
                'expected_vs_actual': np.random.uniform(0, 1),
                'output_stability': np.random.uniform(0, 1),
                'propagation_delay': np.random.uniform(1, 100),
                'setup_time_margin': np.random.uniform(-10, 10),
                'hold_time_margin': np.random.uniform(-10, 10),
                'power_consumption': np.random.uniform(0.5, 2.0),
                'current_spike': np.random.uniform(0, 1),
                'pattern_similarity': np.random.uniform(0, 1),
                'error_pattern_length': np.random.randint(0, 20),
                'consecutive_errors': np.random.randint(0, 15),
            }
            sample['fault_type'] = self._assign_fault(sample)
            data.append(sample)
        return pd.DataFrame(data)
    
    def _assign_fault(self, s):
        if s['output_mismatch'] == 0 and s['expected_vs_actual'] > 0.9:
            return 'no_fault'
        elif s['consecutive_errors'] > 4 and s['output_stability'] > 0.4:
            return 'transition_fault'
        elif s['current_spike'] > 0.65 and s['power_consumption'] > 1.4:
            return 'bridging_fault'
        elif s['output_stability'] < 0.3 and s['signal_strength'] < 0.7:
            return 'stuck_at_0'
        elif s['output_stability'] < 0.3 and s['signal_strength'] > 1.3:
            return 'stuck_at_1'
        elif abs(s['setup_time_margin']) < 2:
            return 'timing_violation'
        elif s['propagation_delay'] > 80:
            return 'delay_fault'
        elif s['signal_strength'] < 0.6:
            return 'open_circuit'
        else:
            return 'logic_error'
    
    def train(self):
        print("   Generating training data...")
        df = self.generate_training_data()
        X = df[FEATURE_NAMES].values
        y = self.label_encoder.fit_transform(df['fault_type'].values)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        print("   Training Random Forest...")
        self.best_model = RandomForestClassifier(n_estimators=150, max_depth=15, 
                                                  random_state=RANDOM_STATE, n_jobs=-1)
        self.best_model.fit(X_train, y_train)
        self.best_model_name = "RandomForest"
        
        y_pred = self.best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"   Accuracy: {accuracy*100:.2f}%")
        self.trained = True
        
        MODELS_DIR.mkdir(exist_ok=True)
        joblib.dump({
            'model': self.best_model,
            'name': self.best_model_name,
            'encoder': self.label_encoder,
            'scaler': self.scaler,
            'features': self.feature_names
        }, MODEL_FILE)
        print(f"   Model saved to: {MODEL_FILE}")
        
        return accuracy
    
    def detect_faults(self, features_dict):
        if not self.trained:
            return None, 0.0, [], "Model not trained!"
        
        X = np.array([features_dict[name] for name in self.feature_names]).reshape(1, -1)
        X = self.scaler.transform(X)
        
        pred = self.best_model.predict(X)[0]
        probs = self.best_model.predict_proba(X)[0]
        
        fault_type = self.label_encoder.inverse_transform([pred])[0]
        confidence = probs[pred] * 100
        
        top3_idx = np.argsort(probs)[-3:][::-1]
        top3 = [(self.label_encoder.inverse_transform([i])[0], probs[i]*100) for i in top3_idx]
        
        return fault_type, confidence, top3, f"Using: {self.best_model_name}"
    
    def load_model(self):
        if MODEL_FILE.exists():
            data = joblib.load(MODEL_FILE)
            self.best_model = data['model']
            self.best_model_name = data['name']
            self.label_encoder = data['encoder']
            self.scaler = data['scaler']
            self.feature_names = data['features']
            self.trained = True
            return True
        return False
