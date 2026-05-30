import cv2
import mediapipe as mp
import numpy as np
import math
import time
import winsound # For simple sound feedback

# --- Helper Functions ---
def calculate_distance(p1, p2):
    """Calculates the 3D Euclidean distance between two landmarks."""
    if not all(hasattr(pt, 'x') and hasattr(pt, 'y') and hasattr(pt, 'z') for pt in [p1, p2]): return 0
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def calculate_angle(a, b, c):
    """Calculates the angle between three 2D landmarks (angle at point b)."""
    if not all(hasattr(pt, 'x') and hasattr(pt, 'y') for pt in [a, b, c]): return 0
    a, b, c = np.array([a.x, a.y]), np.array([b.x, b.y]), np.array([c.x, c.y])
    ba, bc = a - b, c - b
    dot_product = np.dot(ba, bc)
    magnitude_ba, magnitude_bc = np.linalg.norm(ba), np.linalg.norm(bc)
    if magnitude_ba == 0 or magnitude_bc == 0: return 0
    cosine_angle = np.clip(dot_product / (magnitude_ba * magnitude_bc), -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))
    return angle

def calculate_wrist_deviation_angle(landmarks):
    """Calculates the wrist radial/ulnar deviation angle relative to forearm."""
    wrist = landmarks[mp_hands.HandLandmark.WRIST]
    mcp = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP] # Used for hand direction

    if not all(hasattr(pt, 'x') and hasattr(pt, 'y') for pt in [wrist, mcp, pip]): return 90

    angle_rad = math.atan2(mcp.x - wrist.x, -(mcp.y - wrist.y))
    angle_deg = math.degrees(angle_rad) + 90
    angle_deg = np.clip(angle_deg, 0, 180)
    return angle_deg


# --- Initialization ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# --- Game Variables ---
EXERCISES = [
    "HAND_OPEN_CLOSE",      # 1
    "WRIST_FLEX_EXTEND",    # 2
    "FINGER_SPREAD",        # 3
    "THUMB_OPPOSITION",     # 4
    "WRIST_DEVIATION",      # 5
    "INDEX_TAP"             # 6 (Experimental)
]
EXERCISE_DESCRIPTIONS = {
    "HAND_OPEN_CLOSE": ["1. Open hand fully (target > {val1:.2f}).", "2. Close into a tight fist (target < {val2:.2f}).", "3. Hold each pose for {hold_time:.1f} sec."],
    "WRIST_FLEX_EXTEND": ["1. Extend wrist UP (target < {val1:.0f} deg).", "2. Flex wrist DOWN (target > {val2:.0f} deg).", "3. Keep forearm steady.", "4. Hold each pose for {hold_time:.1f} sec."],
    "FINGER_SPREAD": ["1. Spread fingers wide (target > {val1:.2f}).", "2. Bring fingers together (target < {val2:.2f}).", "3. Keep palm flat.", "4. Hold each pose for {hold_time:.1f} sec."],
    "THUMB_OPPOSITION": ["Touch thumb tip sequentially to:", " INDEX (dist < {val1:.2f})", " MIDDLE (dist < {val1:.2f})", " RING (dist < {val1:.2f})", " PINKY (dist < {val2:.2f})", "Hold each touch briefly."],
    "WRIST_DEVIATION": ["1. Move wrist LEFT (target < {val1:.0f} deg).", "2. Move wrist RIGHT (target > {val2:.0f} deg).", "3. Keep palm flat, forearm steady.", "4. Hold each pose for {hold_time:.1f} sec."],
    "INDEX_TAP": ["1. Lift index finger UP (target > {val1:.2f}).", "2. Tap index finger DOWN (target < {val2:.2f}).", "3. Keep other fingers still.", "4. Hold each pose for {hold_time:.1f} sec."]
}

current_exercise_index = 0
current_exercise = EXERCISES[current_exercise_index]
rep_counters = {ex: 0 for ex in EXERCISES}
exercise_phase = "START"
successful_phase1 = False
successful_phase2 = False
last_state_change_time = time.time()
state_duration_threshold = 0.8

thresholds = {
    "HAND_OPEN_CLOSE": {"OPEN": 0.30, "CLOSE": 0.15},
    "WRIST_FLEX_EXTEND": {"EXTEND": 160, "FLEX": 200},
    "FINGER_SPREAD": {"SPREAD": 0.12, "TOGETHER": 0.06},
    "THUMB_OPPOSITION": {"TOUCH_INDEX": 0.05, "TOUCH_PINKY": 0.08},
    "WRIST_DEVIATION": {"RADIAL": 75, "ULNAR": 105},
    "INDEX_TAP": {"UP": 0.05, "DOWN": 0.02}
}
threshold_step = {
    "HAND_OPEN_CLOSE": 0.01, "WRIST_FLEX_EXTEND": 5, "FINGER_SPREAD": 0.01,
    "THUMB_OPPOSITION": 0.005, "WRIST_DEVIATION": 5, "INDEX_TAP": 0.005
}

opposition_target_finger = "INDEX"
feedback_text = "Select Exercise (1-6)"

# --- Main Loop ---
while cap.isOpened():
    success, image = cap.read()
    if not success: continue

    image = cv2.flip(image, 1)
    img_height, img_width, _ = image.shape

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    current_metric_value = 0
    metric_name = ""
    interp_range = [0.1, 0.4]
    # Initialize phase names at the start of the loop
    exercise_phase1_name, exercise_phase2_name = None, None

    # Determine thresholds *after* hand processing and potential state updates
    # This calculation is moved further down, right before UI drawing

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark
            current_time = time.time()

            # --- Determine current threshold keys AND values based on current exercise ---
            # Do this *inside* the hand landmarks loop, ensuring it uses the latest current_exercise
            current_thresh_dict = thresholds.get(current_exercise, {})
            phase1_key = next((k for k in current_thresh_dict if k in ["OPEN", "EXTEND", "SPREAD", "TOUCH_INDEX", "RADIAL", "UP"]), None)
            phase2_key = next((k for k in current_thresh_dict if k in ["CLOSE", "FLEX", "TOGETHER", "TOUCH_PINKY", "ULNAR", "DOWN"]), None)
            phase1_thresh = current_thresh_dict.get(phase1_key, 0)
            phase2_thresh = current_thresh_dict.get(phase2_key, 0)


            # --- Calculate Metric based on Current Exercise ---
            if current_exercise == "HAND_OPEN_CLOSE":
                metric_name = "Avg Dist"
                wrist = landmarks[mp_hands.HandLandmark.WRIST]
                fingertip_indices = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]
                if all(idx < len(landmarks) for idx in fingertip_indices):
                    total_distance = sum(calculate_distance(wrist, landmarks[idx]) for idx in fingertip_indices)
                    current_metric_value = total_distance / len(fingertip_indices) if fingertip_indices else 0
                else: current_metric_value = 0
                exercise_phase1_name, exercise_phase2_name = "OPEN", "CLOSE"
                meets_phase1_criteria = current_metric_value > phase1_thresh
                meets_phase2_criteria = current_metric_value < phase2_thresh
                phase1_target_text = "Open Hand Fully"
                phase2_target_text = "Close Fist Tightly"
                interp_range = [phase2_thresh * 0.8, phase1_thresh * 1.2]

            elif current_exercise == "WRIST_FLEX_EXTEND":
                 metric_name = "Wrist Angle"
                 wrist, mcp, pip = landmarks[mp_hands.HandLandmark.WRIST], landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP], landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
                 if all(hasattr(pt,'x') for pt in [wrist, mcp, pip]): current_metric_value = calculate_angle(wrist, mcp, pip)
                 else: current_metric_value = 0 # Default if landmarks missing
                 exercise_phase1_name, exercise_phase2_name = "EXTEND", "FLEX"
                 meets_phase1_criteria = current_metric_value < phase1_thresh
                 meets_phase2_criteria = current_metric_value > phase2_thresh
                 phase1_target_text = "Extend Wrist Up"
                 phase2_target_text = "Flex Wrist Down"
                 interp_range = [phase1_thresh * 0.9, phase2_thresh * 1.1]

            elif current_exercise == "FINGER_SPREAD":
                 metric_name = "Spread Dist"
                 tips = [landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP], landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP], landmarks[mp_hands.HandLandmark.RING_FINGER_TIP], landmarks[mp_hands.HandLandmark.PINKY_TIP]]
                 if all(hasattr(pt,'x') for pt in tips) and all(idx < len(landmarks) for idx in [8, 12, 16, 20]): # Check landmarks exist
                     dists = [calculate_distance(tips[i], tips[i+1]) for i in range(len(tips)-1)]
                     current_metric_value = sum(dists) / len(dists) if dists else 0
                 else: current_metric_value = 0
                 exercise_phase1_name, exercise_phase2_name = "SPREAD", "TOGETHER"
                 meets_phase1_criteria = current_metric_value > phase1_thresh
                 meets_phase2_criteria = current_metric_value < phase2_thresh
                 phase1_target_text = "Spread Fingers Wide"
                 phase2_target_text = "Bring Fingers Together"
                 interp_range = [phase2_thresh * 0.8, phase1_thresh * 1.2]

            elif current_exercise == "THUMB_OPPOSITION":
                 metric_name = "Thumb Dist"
                 thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
                 target_lm_idx = { "INDEX": mp_hands.HandLandmark.INDEX_FINGER_TIP, "MIDDLE": mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                                   "RING": mp_hands.HandLandmark.RING_FINGER_TIP, "PINKY": mp_hands.HandLandmark.PINKY_TIP }.get(opposition_target_finger)
                 target_thresh = phase1_thresh if opposition_target_finger != "PINKY" else phase2_thresh
                 target_text = f"Touch {opposition_target_finger} Finger"

                 if target_lm_idx is not None and target_lm_idx < len(landmarks) and hasattr(landmarks[target_lm_idx],'x'):
                     current_metric_value = calculate_distance(thumb_tip, landmarks[target_lm_idx])
                     meets_touch_criteria = current_metric_value < target_thresh

                     if meets_touch_criteria:
                         feedback_text = f"Holding {opposition_target_finger}..."
                         if current_time - last_state_change_time > state_duration_threshold * 0.5:
                             winsound.Beep(1000, 50)
                             if opposition_target_finger == "INDEX": opposition_target_finger = "MIDDLE"
                             elif opposition_target_finger == "MIDDLE": opposition_target_finger = "RING"
                             elif opposition_target_finger == "RING": opposition_target_finger = "PINKY"
                             else:
                                 opposition_target_finger = "INDEX"; rep_counters[current_exercise] += 1
                                 print(f"{current_exercise} Rep {rep_counters[current_exercise]} done!"); winsound.Beep(1500, 150)
                             last_state_change_time = current_time
                     else:
                         feedback_text = f"Target: {target_text}"; last_state_change_time = current_time
                 else: feedback_text = "Error: Landmarks not detected"; current_metric_value=99 # Set high distance if lm missing
                 interp_range = [target_thresh * 1.5, 0]

            elif current_exercise == "WRIST_DEVIATION":
                 metric_name = "Deviation Angle"
                 current_metric_value = calculate_wrist_deviation_angle(landmarks)
                 exercise_phase1_name, exercise_phase2_name = "RADIAL", "ULNAR"
                 meets_phase1_criteria = current_metric_value < phase1_thresh
                 meets_phase2_criteria = current_metric_value > phase2_thresh
                 phase1_target_text = "Move Wrist Left (Thumb Side)"
                 phase2_target_text = "Move Wrist Right (Pinky Side)"
                 interp_range = [phase1_thresh * 0.9, phase2_thresh * 1.1]

            elif current_exercise == "INDEX_TAP":
                 metric_name = "Index Tip Height"
                 index_tip, index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP], landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                 if all(hasattr(pt,'y') for pt in [index_tip, index_mcp]): current_metric_value = index_mcp.y - index_tip.y
                 else: current_metric_value = 0
                 exercise_phase1_name, exercise_phase2_name = "UP", "DOWN"
                 meets_phase1_criteria = current_metric_value > phase1_thresh
                 meets_phase2_criteria = current_metric_value < phase2_thresh
                 phase1_target_text = "Lift Index Finger"
                 phase2_target_text = "Tap Index Finger Down"
                 interp_range = [phase2_thresh * 0.8, phase1_thresh * 1.2]

            # --- Generic Exercise State Logic (excluding THUMB_OPPOSITION) ---
            if current_exercise != "THUMB_OPPOSITION":
                if exercise_phase1_name and exercise_phase2_name:
                    if exercise_phase == "START" or exercise_phase == exercise_phase1_name:
                        if meets_phase1_criteria:
                            feedback_text = f"Hold {exercise_phase1_name}..."
                            if current_time - last_state_change_time > state_duration_threshold:
                                if not successful_phase1: winsound.Beep(1000, 100)
                                successful_phase1 = True
                                feedback_text = f"Good! Now {phase2_target_text}"
                                exercise_phase = exercise_phase2_name
                                last_state_change_time = current_time
                        else:
                            feedback_text = f"Target: {phase1_target_text}"
                            last_state_change_time = current_time

                    elif exercise_phase == exercise_phase2_name:
                        if meets_phase2_criteria:
                            feedback_text = f"Hold {exercise_phase2_name}..."
                            if current_time - last_state_change_time > state_duration_threshold:
                                if not successful_phase2: winsound.Beep(1000, 100)
                                successful_phase2 = True
                                feedback_text = f"Good! Now {phase1_target_text}"
                                exercise_phase = exercise_phase1_name
                                last_state_change_time = current_time
                        else:
                            feedback_text = f"Target: {phase2_target_text}"
                            last_state_change_time = current_time

                    if successful_phase1 and successful_phase2:
                        rep_counters[current_exercise] += 1
                        successful_phase1, successful_phase2 = False, False
                        print(f"{current_exercise} Rep {rep_counters[current_exercise]} done!"); winsound.Beep(1500, 150)

    else:
        last_state_change_time = time.time()
        feedback_text = "Show your hand to start"


    # --- Key Press Handling ---
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'): break

    # Exercise Selection
    if ord('1') <= key <= ord(str(len(EXERCISES))):
        selected_index = key - ord('1')
        if selected_index != current_exercise_index:
             current_exercise_index = selected_index
             current_exercise = EXERCISES[current_exercise_index]
             exercise_phase = "START"
             successful_phase1, successful_phase2 = False, False
             last_state_change_time = time.time()
             feedback_text = f"Starting: {current_exercise}"
             if current_exercise == "THUMB_OPPOSITION": opposition_target_finger = "INDEX"
             print(f"\nSwitched to Exercise: {current_exercise}")

    # Threshold Adjustment
    # Get the keys again *after* potential exercise switch
    current_thresh_dict = thresholds.get(current_exercise, {})
    phase1_key = next((k for k in current_thresh_dict if k in ["OPEN", "EXTEND", "SPREAD", "TOUCH_INDEX", "RADIAL", "UP"]), None)
    phase2_key = next((k for k in current_thresh_dict if k in ["CLOSE", "FLEX", "TOGETHER", "TOUCH_PINKY", "ULNAR", "DOWN"]), None)

    if phase1_key and phase2_key:
        step = threshold_step[current_exercise]
        adj_made = False
        thresh1 = thresholds[current_exercise][phase1_key]
        thresh2 = thresholds[current_exercise][phase2_key]

        if key == ord('+') or key == ord('='):
            thresholds[current_exercise][phase1_key] = thresh1 + step if thresh1 > thresh2 else thresh1 - step
            thresholds[current_exercise][phase2_key] = thresh2 - step if thresh1 > thresh2 else thresh2 + step
            adj_made = True
        elif key == ord('-'):
            thresholds[current_exercise][phase1_key] = thresh1 - step if thresh1 > thresh2 else thresh1 + step
            thresholds[current_exercise][phase2_key] = thresh2 + step if thresh1 > thresh2 else thresh2 - step
            adj_made = True

        if adj_made:
             min_val = 0.01 if step < 1 else 1
             val1 = max(min_val, thresholds[current_exercise][phase1_key])
             val2 = max(min_val, thresholds[current_exercise][phase2_key])
             # Prevent crossing
             if (current_exercise not in ["WRIST_FLEX_EXTEND", "WRIST_DEVIATION"]) and val1 <= val2 : val1 = val2 + step
             elif (current_exercise in ["WRIST_FLEX_EXTEND", "WRIST_DEVIATION"]) and val1 >= val2: val1 = val2 - step
             thresholds[current_exercise][phase1_key] = val1
             thresholds[current_exercise][phase2_key] = val2
             print(f"Thresholds adjusted for {current_exercise}. Current: {phase1_key}={val1:.2f}, {phase2_key}={val2:.2f}")

    # --- Display UI and Feedback ---
    # Get final threshold values for display *after* potential adjustments
    phase1_thresh = thresholds[current_exercise].get(phase1_key, 0)
    phase2_thresh = thresholds[current_exercise].get(phase2_key, 0)

    # Draw Description Box
    desc_box_x, desc_box_y, desc_box_w, desc_box_h = img_width - 420, 120, 400, 180
    cv2.rectangle(image_bgr, (desc_box_x, desc_box_y), (desc_box_x + desc_box_w, desc_box_y + desc_box_h), (50, 50, 50), -1)
    cv2.rectangle(image_bgr, (desc_box_x, desc_box_y), (desc_box_x + desc_box_w, desc_box_y + desc_box_h), (255, 255, 255), 1)
    cv2.putText(image_bgr, "Instructions:", (desc_box_x + 10, desc_box_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    desc_lines_template = EXERCISE_DESCRIPTIONS.get(current_exercise, ["No description."])
    desc_lines_formatted = []
    for line in desc_lines_template:
        try: formatted_line = line.format(val1=phase1_thresh, val2=phase2_thresh, hold_time=state_duration_threshold); desc_lines_formatted.append(formatted_line)
        except: desc_lines_formatted.append(line)
    for i, line in enumerate(desc_lines_formatted):
         cv2.putText(image_bgr, line, (desc_box_x + 15, desc_box_y + 60 + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Draw progress bar
    bar_x, bar_y, bar_w, bar_h = 50, img_height - 100, img_width - 100, 30
    # Ensure interp_range is valid for drawing
    valid_interp = len(interp_range) == 2 and interp_range[0] != interp_range[1]
    if valid_interp and interp_range[0] > interp_range[1]: # Ensure min < max for interp
        interp_range = [interp_range[1], interp_range[0]]
        
    if valid_interp :
        prog = np.clip(np.interp(current_metric_value, interp_range, [0, 1]), 0, 1)
        curr_bar_w = int(bar_w * prog)
        cv2.rectangle(image_bgr, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), -1)
        cv2.rectangle(image_bgr, (bar_x, bar_y), (bar_x + curr_bar_w, bar_y + bar_h), (0, 255, 0), -1)
        if phase1_key and phase2_key:
             m1_val, m2_val = thresholds[current_exercise][phase1_key], thresholds[current_exercise][phase2_key]
             m1_pos, m2_pos = int(np.interp(m1_val, interp_range, [0, bar_w])), int(np.interp(m2_val, interp_range, [0, bar_w]))
             m1_pos, m2_pos = np.clip(m1_pos, 0, bar_w), np.clip(m2_pos, 0, bar_w)
             if abs(m1_pos - m2_pos) > 1:
                 cv2.line(image_bgr, (bar_x + m1_pos, bar_y), (bar_x + m1_pos, bar_y + bar_h), (255, 255, 255), 2)
                 cv2.line(image_bgr, (bar_x + m2_pos, bar_y), (bar_x + m2_pos, bar_y + bar_h), (255, 255, 255), 2)
    else: cv2.rectangle(image_bgr, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), -1)

    # Display Texts
    cv2.putText(image_bgr, f"Exercise: {current_exercise} ({current_exercise_index + 1}/{len(EXERCISES)})", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(image_bgr, feedback_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.putText(image_bgr, f"Reps: {rep_counters[current_exercise]}", (img_width - 200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3, cv2.LINE_AA)
    cv2.putText(image_bgr, f"{metric_name}: {current_metric_value:.2f}", (img_width - 350, img_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    thresh1_val = thresholds[current_exercise].get(phase1_key, 0)
    thresh2_val = thresholds[current_exercise].get(phase2_key, 0)
    cv2.putText(image_bgr, f"Thresh: {thresh1_val:.2f}/{thresh2_val:.2f} (+/-)", (50, img_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow('Hand Rehabilitation Game', image_bgr)

cap.release()
cv2.destroyAllWindows()

# --- Display Session Summary ---
print("\n--- Session Summary ---")
for ex, count in rep_counters.items():
    print(f"{ex}: {count} repetitions")
print("-----------------------")