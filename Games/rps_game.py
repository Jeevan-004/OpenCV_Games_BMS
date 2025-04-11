import cv2
import mediapipe as mp
import random
import time
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Get hand gesture from landmarks
def get_hand_gesture(hand_landmarks):
    finger_tips_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb (special case)
    if hand_landmarks.landmark[finger_tips_ids[0]].x < hand_landmarks.landmark[finger_tips_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for tip_id in finger_tips_ids[1:]:
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    if fingers == [0, 0, 0, 0, 0]:
        return "Rock"
    elif fingers == [1, 1, 1, 1, 1]:
        return "Paper"
    elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
        return "Scissors"
    else:
        return "Unknown"

# Initialize webcam and MediaPipe Hands
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

player_move = "None"
comp_move = "None"
result = "Make your move!"

# Scoreboard variables
player_score = 0
comp_score = 0

start_time = time.time()
delay = 5  # seconds delay between moves

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # mirror image for a natural feel
    h, w, c = frame.shape

    # Convert frame for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Detect hand gesture (process just the first hand detected)
    gesture = ""
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = get_hand_gesture(hand_landmarks)
            break

    # Update game logic after a fixed delay
    if time.time() - start_time > delay:
        if gesture != "Unknown" and gesture != "":
            player_move = gesture
            comp_move = random.choice(["Rock", "Paper", "Scissors"])
            
            # Determine round outcome
            if player_move == comp_move:
                result = "It's a Tie!"
            elif (player_move == "Rock" and comp_move == "Scissors") or \
                 (player_move == "Scissors" and comp_move == "Paper") or \
                 (player_move == "Paper" and comp_move == "Rock"):
                result = "You Win!"
                player_score += 1
            else:
                result = "Computer Wins!"
                comp_score += 1
        else:
            result = "Move not detected"
        start_time = time.time()

    # Create a semi-transparent overlay for the scoreboard/header
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 90), (0, 0, 0), -1)
    alpha = 0.4
    frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    # Draw scoreboard information
    cv2.putText(frame, f"Player: {player_score}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Computer: {comp_score}", (w - 250, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Display the moves (at the bottom)
    cv2.putText(frame, f"Your Move: {player_move}", (10, h - 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
    cv2.putText(frame, f"Computer: {comp_move}", (10, h - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2)
    
    # Center the result text with a shadow effect for visual impact
    text = f"Result: {result}"
    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
    text_x = (w - text_width) // 2
    text_y = h // 2
    # Draw shadow
    cv2.putText(frame, text, (text_x + 2, text_y + 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 4)
    # Draw main text
    cv2.putText(frame, text, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    
    # Add visual effects based on outcome
    if result == "You Win!":
        # Confetti effect: draw random colorful circles
        for i in range(30):
            x = random.randint(0, w)
            y = random.randint(0, h)
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            cv2.circle(frame, (x, y), radius=4, color=color, thickness=-1)
    elif result == "Computer Wins!":
        # Rain effect: draw thin red lines
        for i in range(30):
            x = random.randint(0, w)
            y = random.randint(0, h)
            cv2.line(frame, (x, y), (x, y+10), (0, 0, 255), 2)

    # Instructional prompt at the bottom of the frame
    cv2.putText(frame, "Show Rock / Paper / Scissors", (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

    cv2.imshow("Rock Paper Scissors - OpenCV", frame)
    if cv2.waitKey(1) == 27:  # press ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
