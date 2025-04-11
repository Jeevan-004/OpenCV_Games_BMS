import cv2
import mediapipe as mp
import pygame
import sys

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
cap = cv2.VideoCapture(0)

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 640, 480
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🧠 Head Tilt Maze")

clock = pygame.time.Clock()
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLUE = (100, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 100)

# Player Dot
dot_radius = 10
dot_x, dot_y = 60, 60
dot_speed = 4
start_pos = (60, 60)

# New Curvy Maze Walls
walls = [
    pygame.Rect(50, 100, 300, 20),
    pygame.Rect(330, 100, 20, 100),
    pygame.Rect(100, 180, 250, 20),
    pygame.Rect(100, 180, 20, 100),
    pygame.Rect(100, 260, 250, 20),
    pygame.Rect(330, 260, 20, 100),
    pygame.Rect(100, 340, 250, 20),
    pygame.Rect(100, 340, 20, 100),
    pygame.Rect(100, 420, 250, 20),

    # Outer bounds
    pygame.Rect(0, 0, WIDTH, 20),
    pygame.Rect(0, HEIGHT - 20, WIDTH, 20),
    pygame.Rect(0, 0, 20, HEIGHT),
    pygame.Rect(WIDTH - 20, 0, 20, HEIGHT),
]

# Finish Zone
finish_zone = pygame.Rect(340, 420, 50, 30)

prev_nose_x = None

def draw_maze():
    win.fill(WHITE)
    for wall in walls:
        pygame.draw.rect(win, BLUE, wall)
    pygame.draw.circle(win, RED, (dot_x, dot_y), dot_radius)
    pygame.draw.rect(win, GREEN, finish_zone)
    pygame.display.update()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    # Quit logic
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    # Face movement
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        nose = landmarks[1]
        nose_x = int(nose.x * WIDTH)

        if prev_nose_x:
            dx = nose_x - prev_nose_x
            if dx > 5:
                dot_x += dot_speed
            elif dx < -5:
                dot_x -= dot_speed

        prev_nose_x = nose_x

    # Collision detection
    dot_rect = pygame.Rect(dot_x - dot_radius, dot_y - dot_radius, dot_radius * 2, dot_radius * 2)
    if any(dot_rect.colliderect(wall) for wall in walls):
        dot_x, dot_y = start_pos

    # Check finish
    if dot_rect.colliderect(finish_zone):
        print("🎉 You Reached the Finish Line!")
        dot_x, dot_y = start_pos

    draw_maze()
    clock.tick(FPS)
