# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import time

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

# Quiz Configuration
QUIZ_ANSWERS = ["VERT", "BLEU", "ROSE", "BLEU", "ROSE", "VERT", "JAUNE", "ROSE", "BLEU", "JAUNE"]
current_question_index = 0
last_action_time = 0
COOLDOWN_SECONDS = 2.0

# Register a callback for when all objects are detected
def send_detections_to_ui(detections: dict):
  global current_question_index, last_action_time

  # Visualization for UI
  for key, value in detections.items():
    entry = {
      "content": key,
      "confidence": value.get("confidence"),
      "timestamp": datetime.now(UTC).isoformat(),
      "current_question": current_question_index + 1,
      "target_answer": QUIZ_ANSWERS[current_question_index] if current_question_index < len(QUIZ_ANSWERS) else "DONE"
    }
    ui.send_message("detection", message=entry)

  # Game Logic
  if current_question_index >= len(QUIZ_ANSWERS):
    return # Quiz finished

  now = time.time()
  if now - last_action_time < COOLDOWN_SECONDS:
    return

  # Filter valid colors and find best match
  valid_colors = ["JAUNE", "BLEU", "ROSE", "VERT"]
  best_detection = None
  highest_confidence = 0.0

  for key, value in detections.items():
    if key == "RIEN":
      continue
    
    if key in valid_colors:
      conf = value.get("confidence", 0)
      if conf > highest_confidence:
        highest_confidence = conf
        best_detection = key

  if best_detection:
    expected_answer = QUIZ_ANSWERS[current_question_index]
    print(f"Detected: {best_detection}, Expected: {expected_answer}")

    if best_detection == expected_answer:
      print("Correct!")
      Bridge.call("trigger_relay")
      current_question_index += 1
      last_action_time = now
    else:
      print("Incorrect!")
      Bridge.call("trigger_taser")
      last_action_time = now

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
