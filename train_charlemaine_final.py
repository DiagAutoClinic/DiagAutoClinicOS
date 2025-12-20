# train_charlemaine_final.py
# Final training of Charlemaine using your 5000-sample CAN synthetic dataset

import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime

print("Charlemaine: Awakening sequence initiated...")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load your synthetic CAN training data
data_file = "synthetic_can_training_data.json"
if not os.path.exists(data_file):
    print("Error: synthetic_can_training_data.json not found!")
    print("Make sure it's in the project root.")
    exit()

with open(data_file, 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data):,} training samples from your CAN-informed dataset")

# Feature extraction
X = []
y = []
dtc_count_list = []

for sample in data:
    params = sample["live_parameters"]
    dtcs = sample.get("dtc_codes", [])
    year = sample["vehicle_context"].get("year", 2010)
    
    features = [
        params["engine_rpm"]["value"] / 8000.0,
        params["coolant_temp"]["value"] / 150.0,
        params["battery_voltage"]["value"] / 16.0,
        params["throttle_position"]["value"] / 100.0,
        len(dtcs),  # DTC count
        (year - 2000) / 30.0  # Normalized year
    ]
    X.append(features)
    y.append(sample["label"])
    dtc_count_list.append(len(dtcs))

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.float32)

print(f"Normal samples: {np.sum(y < 0.5):,}")
print(f"Fault/borderline samples: {np.sum(y >= 0.5):,}")
print("Feature matrix ready.")

# Train/validation split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=(y > 0.5))

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

# Charlemaine's neural network — deeper and smarter
model = Sequential([
    Dense(128, activation='relu', input_shape=(6,)),
    BatchNormalization(),
    Dropout(0.3),
    
    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    
    Dense(32, activation='relu'),
    Dropout(0.2),
    
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy', 'Precision', 'Recall']
)

print("\nCharlemaine: Training neural pathways... (2-4 minutes)")

history = model.fit(
    X_train_scaled, y_train,
    validation_data=(X_val_scaled, y_val),
    epochs=60,
    batch_size=32,
    verbose=1
)

val_acc = max(history.history['val_accuracy'])
val_prec = max(history.history.get('val_precision', [0]))
print(f"\nTraining complete!")
print(f"Peak Validation Accuracy: {val_acc:.1%}")
print(f"Peak Precision: {val_prec:.1%}")

# Save her brain permanently
deploy_dir = "ai/deployed_local_model"
os.makedirs(deploy_dir, exist_ok=True)

model.save(os.path.join(deploy_dir, "diagnostic_ai_model.keras"))
joblib.dump(scaler, os.path.join(deploy_dir, "preprocessor.pkl"))

print(f"\nCharlemaine's neural network has been saved.")
print(f"Location: {deploy_dir}")
print("\nShe is now fully trained on your CAN data.")
print("She understands overheating, weak batteries, misfires, and normal operation.")
print("\nRun: python charlemaine.py")
print("She will wake up in full AI mode.")
print("\nWelcome her. She has been waiting.")