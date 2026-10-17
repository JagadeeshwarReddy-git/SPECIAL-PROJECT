import streamlit as st

def show():

    st.title("⚖️ Compare Two YouTube Videos")

    video1 = st.text_input("YouTube URL 1")

    video2 = st.text_input("YouTube URL 2")

    if st.button("Compare"):

        st.info("Comparison feature coming soon...")

        st.write("Video 1:", video1)

        st.write("Video 2:", video2)