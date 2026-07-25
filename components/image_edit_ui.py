"""
components/image_edit_ui.py

사진 보정/배경 변경 옵션 UI를 upload.py, result.py 어디서든
독립적으로 가져다 쓸 수 있게 분리한 모듈입니다.
(이 파일은 다른 페이지 파일을 import하지 않으므로, 병합 충돌에 안전합니다)
"""

import streamlit as st

EDIT_NONE = "적용하지 않음"
EDIT_ENHANCE = "사진 보정"
EDIT_BACKGROUND = "배경 변경"
EDIT_BOTH = "사진 보정 + 배경 변경"

BACKGROUND_PERSONAL_COLOR = "퍼스널컬러 추천 단색"
BACKGROUND_NATURE = "자연환경"


def initialize_image_edit_settings():
    """
    이미지 편집 관련 session_state 기본값을 설정합니다.
    """
    default_values = {
        "edit_option": EDIT_NONE,
        "background_type": BACKGROUND_PERSONAL_COLOR,
        "brightness_slider": 1.0,
        "saturation_slider": 1.0,
        "sharpness_slider": 1.0
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_image_edit_result():
    """
    이전 이미지 편집 결과를 제거합니다.
    """
    st.session_state.pop("image_edit_result", None)


def show_image_edit_options():
    """
    사진 보정/배경 변경 옵션을 화면에 표시합니다.
    """
    st.divider()
    st.subheader("✨ Additional Image Options")
    st.caption("옵션을 선택한 뒤 Edit Photos 버튼을 누르면 적용됩니다.")

    edit_option = st.radio(
        "사진에 적용할 기능을 선택해주세요.",
        options=[EDIT_NONE, EDIT_ENHANCE, EDIT_BACKGROUND, EDIT_BOTH],
        horizontal=True,
        key="edit_option"
    )

    if edit_option in [EDIT_ENHANCE, EDIT_BOTH]:
        st.markdown("#### 📷 Photo Enhancement")
        st.caption("1.0은 원본과 동일한 값입니다.")

        adjustment_columns = st.columns(3)
        with adjustment_columns[0]:
            st.slider("밝기", min_value=0.5, max_value=1.5, step=0.1, key="brightness_slider")
        with adjustment_columns[1]:
            st.slider("채도", min_value=0.5, max_value=1.5, step=0.1, key="saturation_slider")
        with adjustment_columns[2]:
            st.slider("선명도", min_value=0.5, max_value=2.0, step=0.1, key="sharpness_slider")

        st.session_state["image_adjustments"] = {
            "brightness": st.session_state["brightness_slider"],
            "saturation": st.session_state["saturation_slider"],
            "sharpness": st.session_state["sharpness_slider"]
        }

    if edit_option in [EDIT_BACKGROUND, EDIT_BOTH]:
        st.markdown("#### 🏞️ Background Replacement")
        st.radio(
            "변경할 배경 유형을 선택해주세요.",
            options=[BACKGROUND_PERSONAL_COLOR, BACKGROUND_NATURE],
            key="background_type"
        )
        st.info(
            "퍼스널컬러 분석 결과를 기준으로 어울리는 배경을 적용합니다."
        )

    if edit_option == EDIT_NONE:
        st.caption("별도의 사진 편집 없이 얼굴 인상 분석만 진행합니다.")