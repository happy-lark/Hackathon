from PIL import Image, ImageEnhance, ImageFilter

import streamlit as st

from utils.navigation import go_to_page
from analysis.image_editor import process_images
from analysis.background_editor import (
    change_background,
    blur_background,
    apply_solid_color_background,
    apply_generated_background,
)

SOLID_COLORS = ["#B39DDB", "#8B5E3C", "#D9C7A3", "#6FA8DC"]
# =========================================
# Step 9. Photo Editor 화면 (신규 추가)
# =========================================

def apply_background_choice(image, choice, solid_color=None):
    if choice == "Original":
        return image
    if choice == "Blur":
        return blur_background(image)
    if choice == "Solid Color":
        return apply_solid_color_background(image, solid_color)
    if choice in ("Office", "Urban"):
        return apply_generated_background(image, choice)
    if choice == "Nature":
        result = change_background(image, "자연환경", None)
        return result["image"]
    return image


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
            options=["Original", "Blur", "Solid Color", "Office", "Urban", "Nature"],
            label_visibility="collapsed",
            key="editor_background_choice",
        )

        solid_color = None
        if background_choice == "Solid Color":
            solid_color = st.radio(
                "색상 선택",
                options=SOLID_COLORS,
                format_func=lambda c: " ",
                horizontal=True,
                label_visibility="collapsed",
                key="editor_solid_color",
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
            image_adjustments = {
                "brightness": brightness,
                "saturation": saturation,
                "sharpness": sharpness,
            }

            with st.spinner("Applying your edits..."):
                image_edit_result = process_images(
                    images=[base_image],
                    edit_option="사진 보정",
                    image_adjustments=image_adjustments,
                    background_type=None,
                    color_analysis_result=None,
                )

                if image_edit_result["success"] and background_choice != "Original":
                    item = image_edit_result["results"][0]
                    item["edited_image"] = apply_background_choice(
                        item["edited_image"], background_choice, solid_color
                    )
                    item["descriptions"].append(f"배경을 {background_choice}(으)로 변경했습니다.")

            if image_edit_result["success"]:
                st.session_state["image_edit_result"] = image_edit_result
                go_to_page("image_edit_result")
            else:
                st.error("이미지를 편집하지 못했습니다.")
                for item in image_edit_result["results"]:
                    if not item["success"]:
                        st.warning(item.get("message", "Unknown error"))