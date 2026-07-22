import streamlit as st

from utils.navigation import go_to_page

def show_analysis_type_page():
    st.title("Choose Your Analysis")

    st.write(
        "사진으로 확인하고 싶은 분석 유형을 선택해주세요."
    )

    persona_col, color_col = st.columns(2)

    with persona_col:
        st.subheader("✨ Persona Analysis")

        st.write(
            "표정, 시선, 얼굴 방향을 분석해서 "
            "사진이 전달하는 인상을 확인합니다."
        )

        if st.button(
            "Persona Analysis 시작",
            use_container_width=True,
            key="choose_persona",
        ):
            st.session_state["analysis_type"] = "persona"
            go_to_page("mode")

    with color_col:
        st.subheader("🎨 Personal Color")

        st.write(
            "얼굴 피부색의 밝기, 채도, 색조를 분석해서 "
            "퍼스널 컬러를 확인합니다."
        )

        if st.button(
            "Personal Color 시작",
            use_container_width=True,
            key="choose_personal_color",
        ):
            st.session_state["analysis_type"] = "personal_color"
            go_to_page("personal_color")

    if st.button("← Back"):
        go_to_page("landing")