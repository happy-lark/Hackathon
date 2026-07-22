import streamlit as st
from utils.navigation import go_to_page


def show_personal_color_page():
    st.title("🎨 Personal Color Analysis")

    st.write("퍼스널 컬러 분석 페이지입니다.")

    if st.button("← Back"):
        go_to_page("upload")