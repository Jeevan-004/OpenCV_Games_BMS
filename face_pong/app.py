import streamlit as st
from face_pong_utils import run_face_pong

st.set_page_config(page_title="Face Pong 🎮", layout="centered")

st.title("🎮 Face Pong - Move your face to play!")
st.markdown("""
Control the paddle using your face 👦👧  
Bounce the ball and try not to miss!  
Fun, hands-free game for kids aged 10–13 😄
""")

if st.button("Start Game"):
    stframe = st.empty()
    for frame_bytes, gameover in run_face_pong():
        stframe.image(frame_bytes, channels="BGR", use_column_width=True)
        if gameover:
            st.success("Game Over! Want to try again?")
            break
