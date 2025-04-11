# face_pong.py
import cv2
import numpy as np
import streamlit as st

# Streamlit page setup
st.set_page_config(page_title="Face Pong Game", layout="centered")
st.title("🎮 Face Pong")
st.markdown("Move your face left/right to control the paddle!")

# Game settings
width, height = 640, 480
paddle_width, paddle_height = 100, 15
ball_radius = 10
ball_speed_x, ball_speed_y = 8, 8  # Increased speed

# Start video capture
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Game state
ball_x = width // 2
ball_y = height // 2
ball_dx = ball_speed_x
ball_dy = ball_speed_y

score = 0

st_frame = st.empty()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Paddle position
    paddle_x = width // 2
    for (x, y, w, h) in faces:
        center_x = x + w // 2
        paddle_x = np.clip(center_x - paddle_width // 2, 0, width - paddle_width)
        break  # Only first face

    # Update ball position
    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collision with walls
    if ball_x <= 0 or ball_x >= width:
        ball_dx *= -1
    if ball_y <= 0:
        ball_dy *= -1

    # Ball collision with paddle
    if height - 30 <= ball_y + ball_radius <= height:
        if paddle_x <= ball_x <= paddle_x + paddle_width:
            ball_dy *= -1
            score += 1

    # Ball missed
    if ball_y > height:
        score = 0
        ball_x = width // 2
        ball_y = height // 2
        ball_dx = ball_speed_x
        ball_dy = ball_speed_y

    # Draw everything
    game_frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.circle(game_frame, (ball_x, ball_y), ball_radius, (0, 255, 255), -1)
    cv2.rectangle(game_frame, (paddle_x, height - 20), (paddle_x + paddle_width, height - 5), (0, 255, 0), -1)

    # Add face preview in the corner
    small_frame = cv2.resize(frame, (160, 120))
    game_frame[height - 120:height, width - 160:width] = small_frame

    # Add score
    cv2.putText(game_frame, f"Score: {score}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Show frame in Streamlit
    st_frame.image(game_frame, channels="BGR", use_container_width=True)

# Release resources
cap.release()
cv2.destroyAllWindows()
