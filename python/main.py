import cv2
import numpy as np
import tensorflow as tf
import serial
import serial.tools.list_ports
import time
import sys
import os

# Configuration
# NO HARDCODED PORT - We will search for it
BAUD_RATE = 9600
CONFIDENCE_THRESHOLD = 0.5  # Lowered for easier testing

def find_arduino_port():
    """Attempts to find the Arduino serial port automatically."""
    ports = list(serial.tools.list_ports.comports())
    print(f"Available ports: {[p.device for p in ports]}")
    
    # Priority list for Linux/Internal ports
    # On many embedded Linux arduino boards, the internal link might be ttyRPMSG0, ttyGS0, or ttyACM0
    priority_patterns = ['/dev/ttyACM', '/dev/ttyUSB', '/dev/ttyS', 'COM']
    
    for pattern in priority_patterns:
        for p in ports:
            if pattern in p.device:
                return p.device
    
    # Fallback: just return the first one if any
    if ports:
        return ports[0].device
    return None

def main():
    print("Python Script Starting...", flush=True)

    # 1. Setup Serial Communication
    port = find_arduino_port()
    arduino = None
    
    if port:
        try:
            print(f"Attempting to connect to {port}...", flush=True)
            arduino = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2) # Wait for DTR reset
            print(f"Connected to Arduino on {port}", flush=True)
        except Exception as e:
            print(f"Error connecting to Serial {port}: {e}", flush=True)
    else:
        print("No Serial Port found. Running in simulation mode.", flush=True)

    # 2. Load Model
    model_path = 'keras_model.h5'
    labels_path = 'labels.txt'
    
    if not os.path.exists(model_path):
        print(f"ERROR: Model file {model_path} not found in {os.getcwd()}", flush=True)
        # Attempt to look in common temp locations if needed, or just warn
    
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        print("Model loaded successfully", flush=True)
    except Exception as e:
        print(f"Error loading model: {e}", flush=True)
        return

    # Load Labels
    class_names = ["Class 0", "Class 1"]
    if os.path.exists(labels_path):
        with open(labels_path, "r") as f:
            class_names = f.readlines()
    else:
        print("Warning: labels.txt not found. Using default names.", flush=True)

    # 3. Open Webcam
    # Try indices 0, 1, 2 in case 0 is not the USB cam
    cap = None
    for i in range(3):
        temp_cap = cv2.VideoCapture(i)
        if temp_cap.isOpened():
            cap = temp_cap
            print(f"Camera opened on index {i}", flush=True)
            break
    
    if not cap:
        print("Error: Could not open any webcam.", flush=True)
        return

    print("Starting Main Loop.", flush=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame", flush=True)
            break

        # 4. Preprocess Frame
        image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        image = (image / 127.5) - 1

        # 5. Inference
        prediction = model.predict(image, verbose=0)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]

        # 6. Logic
        # Debug print every 10 frames or so to avoid spam, or just print status changes
        # For now, print status
        
        # Check for 'Up' or 'Levé' or index 1 (Assuming 0 is down/neutral)
        is_up = False
        if "Up" in class_name or "Levé" in class_name:
            is_up = True
        elif index == 1: # Fallback assumption if names don't match
             is_up = True

        if confidence_score > CONFIDENCE_THRESHOLD:
            if is_up:
                cmd = b'1'
                status = "UP (Tick)"
            else:
                cmd = b'0'
                status = "DOWN (Cross)"
            
            if arduino:
                try:
                    arduino.write(cmd)
                except Exception as e:
                    print(f"Serial Write Error: {e}", flush=True)
        else:
            status = "Unsure"

        print(f"Pred: {class_name} ({confidence_score:.2f}) -> {status}", flush=True)

        # Optional: Show Output (might fail in headless container)
        try:
            cv2.putText(frame, f"{status} ({int(confidence_score*100)}%)", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Webcam Image", frame)
            if cv2.waitKey(1) == 27:
                break
        except Exception:
            pass # Ignore display errors

    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()

if __name__ == "__main__":
    main()
