import cv2
import mediapipe as mp
import numpy as np
import random

# Init
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

# Game settings
paddle_height = 120
paddle_width = 20
ball_radius = 20
ball_speed = [10, 10]
ball_pos = [640, 360]
score_left = 0
score_right = 0

def draw_paddle(img, x, y, color=(255, 255, 255)):
    cv2.rectangle(img, (x, y - paddle_height // 2), (x + paddle_width, y + paddle_height // 2), color, -1)

def draw_ball(img, pos):
    cv2.circle(img, tuple(pos), ball_radius, (0, 255, 255), -1)

# Game Loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    lh_y, rh_y = 360, 360  # Default paddle Y positions

    if result.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(result.multi_hand_landmarks, result.multi_handedness):
            cx = int(hand_landmarks.landmark[0].x * img.shape[1])
            cy = int(hand_landmarks.landmark[0].y * img.shape[0])

            label = hand_info.classification[0].label
            if label == "Left":
                lh_y = cy
            else:
                rh_y = cy

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Draw paddles
    draw_paddle(img, 50, lh_y, (0, 255, 0))
    draw_paddle(img, 1210, rh_y, (0, 0, 255))

    # Draw ball
    draw_ball(img, ball_pos)

    # Move ball
    ball_pos[0] += ball_speed[0]
    ball_pos[1] += ball_speed[1]

    # Bounce from top/bottom
    if ball_pos[1] <= 0 or ball_pos[1] >= 720:
        ball_speed[1] *= -1

    # Left paddle collision
    if 50 <= ball_pos[0] <= 70 and lh_y - paddle_height//2 < ball_pos[1] < lh_y + paddle_height//2:
        ball_speed[0] *= -1

    # Right paddle collision
    if 1210 <= ball_pos[0] <= 1230 and rh_y - paddle_height//2 < ball_pos[1] < rh_y + paddle_height//2:
        ball_speed[0] *= -1

    # Score check
    if ball_pos[0] <= 0:
        score_right += 1
        ball_pos = [640, 360]
        ball_speed = [random.choice([-10, 10]), random.choice([-10, 10])]
    elif ball_pos[0] >= 1280:
        score_left += 1
        ball_pos = [640, 360]
        ball_speed = [random.choice([-10, 10]), random.choice([-10, 10])]

    # Scoreboard
    cv2.putText(img, f'{score_left}', (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
    cv2.putText(img, f'{score_right}', (750, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)

    # Show
    cv2.imshow("Hand Pong", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
