from PIL import Image, ImageEnhance, ImageFilter

import streamlit as st

from utils.navigation import go_to_page
from analysis.image_editor import process_images


# =========================================
# Step 9. Photo Editor 화면 (신규 추가)
# =========================================

BACKGROUND_MAP = {
    "Original": None,
    "Nature": "자연환경",
}


def show_photo_editor_page():
    if st.button("← Back", key="editor_back"):
        go_to_page("match_report")

    st.markdown("### Step 6. Optimize Your Photo")
    st.caption("Choose editing options to match your goal.")
    st.write("")

    images = st.session_state.get("uploaded_images", [])
    if not images:
        st.error("사진을 찾을 수 없습니다. 다시 업로드해주세요.")
        if st.button("Return to Upload"):
            go_to_page("upload")
        return

    base_image = images[0]

    preview_col, option_col = st.columns([1, 1])

    with preview_col:
        st.image(base_image, use_container_width=True)

    with option_col:
        st.markdown("**Background**")
        background_choice = st.radio(
            "Background",
            options=list(BACKGROUND_MAP.keys()),
            label_visibility="collapsed",
            key="editor_background_choice",
        )
        st.caption(
            "Blur / Solid Color / Office / Urban 옵션은 이번 데모에서는 지원하지 않습니다."
        )

    st.write("")
    st.markdown("**Adjustments**")

    brightness = st.slider("Brightness", 0.5, 1.5, 1.0, 0.05, key="editor_brightness")
    saturation = st.slider("Saturation", 0.5, 1.5, 1.0, 0.05, key="editor_saturation")
    sharpness = st.slider("Sharpness", 0.5, 2.0, 1.0, 0.05, key="editor_sharpness")

    st.write("")
    reset_col, apply_col = st.columns([1, 2])

    with reset_col:
        if st.button("Reset", use_container_width=True):
            for key in ["editor_brightness", "editor_saturation", "editor_sharpness"]:
                st.session_state.pop(key, None)
            st.rerun()

    with apply_col:
        if st.button("Apply & Continue →", type="primary", use_container_width=True):
            background_type = BACKGROUND_MAP[background_choice]
            edit_option = "사진 보정 + 배경 변경" if background_type else "사진 보정"

            image_adjustments = {
                "brightness": brightness,
                "saturation": saturation,
                "sharpness": sharpness,
            }

            with st.spinner("Applying your edits..."):
                image_edit_result = process_images(
                    images=[base_image],
                    edit_option=edit_option,
                    image_adjustments=image_adjustments,
                    background_type=background_type,
                    color_analysis_result=None,
                )

            if image_edit_result["success"]:
                st.session_state["image_edit_result"] = image_edit_result
                go_to_page("image_edit_result")
            else:
                st.error("이미지를 편집하지 못했습니다.")
                for item in image_edit_result["results"]:
                    if not item["success"]:
                        st.warning(item.get("message", "Unknown error"))