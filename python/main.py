import cv2
import numpy as np
import tensorflow as tf
import serial
import time
import sys

# Configuration
# Replace 'COM3' with your Arduino's serial port (e.g., 'COM3' on Windows, '/dev/ttyACM0' on Linux/Mac)
SERIAL_PORT = 'COM3'  
BAUD_RATE = 9600
MODEL_PATH = "model.keras" # Assumes model is in the same directory, user needs to update path if different
# If you have model.json and bin files, load them differently, but Keras typically uses .h5 or .keras

def main():
    # 1. Setup Serial Communication
    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # Wait for connection to stabilize
        print(f"Connected to Arduino on {SERIAL_PORT}")
    except Exception as e:
        print(f"Error connecting to Serial: {e}")
        print("Continuing without Arduino (simulation mode)...")
        arduino = None

    # 2. Load Model
    # Note: Adjust model loading based on your specific file format (Teachable Machine usually exports Keras .h5)
    try:
        # If it's a model.json + weights, use model_from_json
        # from tensorflow.keras.models import model_from_json
        # with open('model.json', 'r') as json_file:
        #     loaded_model_json = json_file.read()
        # model = model_from_json(loaded_model_json)
        # model.load_weights("model_weights.h5")
        
        # Build a robust loader assuming standard Teachable Machine export
        model = tf.keras.models.load_model('keras_model.h5', compile=False)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure 'keras_model.h5' and 'labels.txt' are in this folder.")
        return

    # Load Labels
    try:
        with open("labels.txt", "r") as f:
            class_names = f.readlines()
    except FileNotFoundError:
        class_names = ["Class 0", "Class 1"]

    # 3. Open Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting Main Loop. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 4. Preprocess Frame for Model
        # Teachable Machine models are typically 224x224
        image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
        # Make the image a numpy array and reshape it to the models input shape.
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        # Normalize the image array
        image = (image / 127.5) - 1

        # 5. Inference
        prediction = model.predict(image, verbose=0)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]

        # 6. Logic: Determine if Arm is Up or Down
        # You need to check which class index corresponds to "Arm Up"
        # Let's assume Class 0 is "Down/Neutral" and Class 1 is "Up" (Change this based on your training!)
        
        # Heuristic: If confidence is high enough
        if confidence_score > 0.7:
             # Assuming '1' means Arm Level/Up in your labels, checking string content is safer
            if "Up" in class_name or "Levé" in class_name or index == 0: # ADJUST THIS INDEX
                # Send '1' for Tick
                if arduino:
                    arduino.write(b'1')
                display_text = "Arm UP (Tick)"
            else:
                # Send '0' for Cross
                if arduino:
                    arduino.write(b'0')
                display_text = "Arm DOWN (Cross)"
        else:
             display_text = "Unsure"

        # Show Output on Screen
        cv2.putText(frame, f"{display_text} ({int(confidence_score*100)}%)", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Webcam Image", frame)

        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)
        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27 or keyboard_input == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()

if __name__ == "__main__":
    main()
