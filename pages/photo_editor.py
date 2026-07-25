"""
pages/photo_editor.py

Step 6. Optimize Your Photo

역할:
- 사용자가 선택한 사진 불러오기
- 배경 변경 옵션 선택
- 밝기, 대비, 채도, 선명도 조절
- analysis/image_editor.py를 호출해 실제 이미지 처리
- 처리된 이미지를 image_edit_result 페이지로 전달
"""

from textwrap import dedent

import streamlit as st
from PIL import Image

from analysis.image_editor import (
    EDIT_BACKGROUND,
    EDIT_BOTH,
    EDIT_ENHANCE,
    EDIT_NONE,
    process_images
)
from utils.navigation import go_to_page


BACKGROUND_OPTIONS = [
    "Original",
    "Blur",
    "Solid Color",
    "Office",
    "Urban",
    "Nature"
]


BACKGROUND_VALUE_MAP = {
    "Original": None,
    "Blur": "blur",
    "Solid Color": "solid",
    "Office": "office",
    "Urban": "urban",
    "Nature": "nature"
}


SOLID_COLOR_OPTIONS = {
    "Soft Gray": "#D9DCE3",
    "Light Blue": "#BFD7F4",
    "Warm Beige": "#E8D4B8",
    "Soft Cream": "#F3E7D3",
    "Muted Teal": "#8CB9C7"
}


DEFAULT_IMAGE_ADJUSTMENTS = {
    "brightness": 1.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "sharpness": 1.0
}


def clean_html(html_content):
    """
    HTML이 코드 블록으로 표시되지 않도록
    들여쓰기와 불필요한 줄바꿈을 제거합니다.
    """

    return " ".join(
        line.strip()
        for line in dedent(
            html_content
        ).strip().splitlines()
        if line.strip()
    )


def render_html(html_content):
    """
    HTML을 Streamlit 화면에 렌더링합니다.
    """

    st.markdown(
        clean_html(html_content),
        unsafe_allow_html=True
    )


def extract_pil_image(image_item):
    """
    session_state에 저장된 이미지 데이터에서
    PIL 이미지를 추출합니다.
    """

    if isinstance(image_item, Image.Image):
        return image_item.convert("RGB")

    if isinstance(image_item, dict):
        possible_keys = [
            "image",
            "original_image",
            "edited_image",
            "result_image"
        ]

        for key in possible_keys:
            image = image_item.get(key)

            if isinstance(image, Image.Image):
                return image.convert("RGB")

    return None


def get_selected_photo():
    """
    사용자가 선택한 사진을 가져옵니다.

    selected_photo_index가 없으면
    best_photo_index를 사용합니다.
    """

    uploaded_images = st.session_state.get(
        "uploaded_images",
        []
    )

    if not uploaded_images:
        return None

    selected_index = st.session_state.get(
        "selected_photo_index"
    )

    if selected_index is None:
        selected_index = st.session_state.get(
            "best_photo_index",
            0
        )

    try:
        selected_index = int(
            selected_index
        )

    except (TypeError, ValueError):
        selected_index = 0

    selected_index = max(
        0,
        min(
            selected_index,
            len(uploaded_images) - 1
        )
    )

    selected_image = extract_pil_image(
        uploaded_images[selected_index]
    )

    if selected_image is None:
        return None

    return {
        "image": selected_image,
        "index": selected_index
    }


def get_color_analysis_result():
    """
    Match Report에서 저장한 퍼스널 컬러 분석 결과를
    background_editor.py에 전달합니다.
    """

    color_result = st.session_state.get(
        "match_report_color_result"
    )

    if not isinstance(
        color_result,
        dict
    ):
        return None

    raw_result = color_result.get(
        "raw_result"
    )

    if isinstance(
        raw_result,
        dict
    ):
        return raw_result

    return color_result


def initialize_editor_state():
    """
    Photo Editor 페이지에서 사용하는
    session_state 값을 초기화합니다.
    """

    st.session_state.setdefault(
        "photo_editor_background",
        "Original"
    )

    st.session_state.setdefault(
        "photo_editor_solid_color_name",
        "Light Blue"
    )

    st.session_state.setdefault(
        "photo_editor_brightness",
        0
    )

    st.session_state.setdefault(
        "photo_editor_contrast",
        0
    )

    st.session_state.setdefault(
        "photo_editor_saturation",
        0
    )

    st.session_state.setdefault(
        "photo_editor_sharpness",
        0
    )


def reset_editor_state():
    """
    모든 보정 옵션을 초기 상태로 되돌립니다.
    """

    st.session_state[
        "photo_editor_background"
    ] = "Original"

    st.session_state[
        "photo_editor_solid_color_name"
    ] = "Light Blue"

    st.session_state[
        "photo_editor_brightness"
    ] = 0

    st.session_state[
        "photo_editor_contrast"
    ] = 0

    st.session_state[
        "photo_editor_saturation"
    ] = 0

    st.session_state[
        "photo_editor_sharpness"
    ] = 0

    st.session_state.pop(
        "photo_editor_preview_result",
        None
    )

    st.session_state.pop(
        "photo_editor_error",
        None
    )


def slider_value_to_factor(
    slider_value
):
    """
    -30~30 슬라이더 값을
    이미지 보정 배율로 변환합니다.

    0   → 1.00
    15  → 1.15
    -10 → 0.90
    """

    try:
        slider_value = float(
            slider_value
        )

    except (TypeError, ValueError):
        slider_value = 0.0

    return max(
        0.5,
        min(
            1.5,
            1.0
            + slider_value
            * 0.01
        )
    )


def build_image_adjustments():
    """
    UI 슬라이더 값을 image_editor.py에서 사용하는
    보정 배율로 변환합니다.
    """

    return {
        "brightness": slider_value_to_factor(
            st.session_state.get(
                "photo_editor_brightness",
                0
            )
        ),
        "contrast": slider_value_to_factor(
            st.session_state.get(
                "photo_editor_contrast",
                0
            )
        ),
        "saturation": slider_value_to_factor(
            st.session_state.get(
                "photo_editor_saturation",
                0
            )
        ),
        "sharpness": slider_value_to_factor(
            st.session_state.get(
                "photo_editor_sharpness",
                0
            )
        )
    }


def adjustments_are_default(
    image_adjustments
):
    """
    보정값이 모두 기본값인지 확인합니다.
    """

    return all(
        abs(
            image_adjustments[key]
            - DEFAULT_IMAGE_ADJUSTMENTS[key]
        )
        < 0.001
        for key in DEFAULT_IMAGE_ADJUSTMENTS
    )


def get_edit_option(
    selected_background,
    image_adjustments
):
    """
    선택한 배경과 보정값에 따라
    편집 옵션을 결정합니다.
    """

    background_changed = (
        selected_background
        != "Original"
    )

    enhancement_changed = (
        not adjustments_are_default(
            image_adjustments
        )
    )

    if (
        background_changed
        and enhancement_changed
    ):
        return EDIT_BOTH

    if background_changed:
        return EDIT_BACKGROUND

    if enhancement_changed:
        return EDIT_ENHANCE

    return EDIT_NONE


def get_background_type(
    selected_background,
    selected_solid_color
):
    """
    UI에서 선택한 배경값을
    background_editor.py에 전달할 값으로 변환합니다.
    """

    if selected_background == "Original":
        return None

    if selected_background == "Solid Color":
        return {
            "type": "solid",
            "color": selected_solid_color
        }

    return BACKGROUND_VALUE_MAP.get(
        selected_background
    )


def run_photo_edit(
    original_image,
    selected_background,
    selected_solid_color,
    image_adjustments
):
    """
    현재 설정을 사용해 사진을 편집합니다.
    """

    edit_option = get_edit_option(
        selected_background=selected_background,
        image_adjustments=image_adjustments
    )

    background_type = get_background_type(
        selected_background=selected_background,
        selected_solid_color=selected_solid_color
    )

    color_analysis_result = (
        get_color_analysis_result()
    )

    try:
        edit_result = process_images(
            images=[
                original_image
            ],
            edit_option=edit_option,
            image_adjustments=image_adjustments,
            background_type=background_type,
            color_analysis_result=(
                color_analysis_result
            )
        )

    except Exception as error:
        return {
            "success": False,
            "message": str(error),
            "image": original_image
        }

    if not edit_result.get(
        "success",
        False
    ):
        result_items = edit_result.get(
            "results",
            []
        )

        error_message = (
            "The photo could not be edited."
        )

        if result_items:
            error_message = result_items[
                0
            ].get(
                "message",
                error_message
            )

        return {
            "success": False,
            "message": error_message,
            "image": original_image
        }

    result_items = edit_result.get(
        "results",
        []
    )

    if not result_items:
        return {
            "success": False,
            "message": (
                "No edited image was returned."
            ),
            "image": original_image
        }

    first_result = result_items[0]

    edited_image = first_result.get(
        "edited_image"
    )

    if not isinstance(
        edited_image,
        Image.Image
    ):
        return {
            "success": False,
            "message": (
                "The edited result is not a valid image."
            ),
            "image": original_image
        }

    return {
        "success": True,
        "image": edited_image.convert("RGB"),
        "descriptions": first_result.get(
            "descriptions",
            []
        ),
        "edit_option": edit_option,
        "background_type": background_type,
        "adjustments": image_adjustments
    }


def show_progress_header():
    """
    Back 버튼과 진행 단계를 표시합니다.
    """

    (
        back_column,
        progress_column,
        empty_column
    ) = st.columns(
        [1.2, 4.2, 1.2],
        vertical_alignment="center"
    )

    with back_column:
        if st.button(
            "‹ Back",
            key="photo_editor_back"
        ):
            go_to_page(
                "match_report"
            )

    with progress_column:
        render_html(
            """
            <div class="photo-editor-progress">
                <span class="photo-editor-progress-dot completed">1</span>
                <span class="photo-editor-progress-line completed"></span>

                <span class="photo-editor-progress-dot completed">2</span>
                <span class="photo-editor-progress-line completed"></span>

                <span class="photo-editor-progress-dot completed">3</span>
                <span class="photo-editor-progress-line completed"></span>

                <span class="photo-editor-progress-dot completed">4</span>
                <span class="photo-editor-progress-line completed"></span>

                <span class="photo-editor-progress-dot completed">5</span>
                <span class="photo-editor-progress-line completed"></span>

                <span class="photo-editor-progress-dot active">6</span>
            </div>
            """
        )

    with empty_column:
        st.empty()


def show_page_header():
    """
    페이지 제목과 설명을 표시합니다.
    """

    render_html(
        """
        <div class="photo-editor-header">
            <div class="photo-editor-title">
                Step 6. Optimize Your Photo
            </div>

            <div class="photo-editor-description">
                Choose editing options to match your goal.
            </div>
        </div>
        """
    )


def show_background_options():
    """
    배경 변경 옵션을 표시합니다.
    """

    st.markdown(
        "#### Background"
    )

    selected_background = st.radio(
        "Background",
        options=BACKGROUND_OPTIONS,
        key="photo_editor_background",
        label_visibility="collapsed"
    )

    selected_solid_color = None

    if selected_background == "Solid Color":
        selected_color_name = st.radio(
            "Solid background color",
            options=list(
                SOLID_COLOR_OPTIONS.keys()
            ),
            horizontal=True,
            key="photo_editor_solid_color_name",
            label_visibility="collapsed"
        )

        selected_solid_color = (
            SOLID_COLOR_OPTIONS[
                selected_color_name
            ]
        )

        render_html(
            f"""
            <div class="photo-editor-selected-color">
                Selected color:

                <span
                    style="
                        display:inline-block;
                        width:15px;
                        height:15px;
                        margin-left:7px;
                        border-radius:50%;
                        border:1px solid #d5d1df;
                        background:{selected_solid_color};
                        vertical-align:middle;
                    "
                ></span>

                {selected_solid_color}
            </div>
            """
        )

    return (
        selected_background,
        selected_solid_color
    )


def show_adjustment_options():
    """
    밝기, 대비, 채도, 선명도 옵션을 표시합니다.
    """

    st.markdown(
        "#### Adjustments"
    )

    st.slider(
        "Brightness",
        min_value=-30,
        max_value=30,
        step=1,
        key="photo_editor_brightness"
    )

    st.slider(
        "Contrast",
        min_value=-30,
        max_value=30,
        step=1,
        key="photo_editor_contrast"
    )

    st.slider(
        "Saturation",
        min_value=-30,
        max_value=30,
        step=1,
        key="photo_editor_saturation"
    )

    st.slider(
        "Sharpness",
        min_value=-30,
        max_value=30,
        step=1,
        key="photo_editor_sharpness"
    )

    return build_image_adjustments()


def show_photo_editor_page():
    """
    Step 6. Optimize Your Photo 페이지입니다.
    """

    initialize_editor_state()

    selected_photo = get_selected_photo()

    if selected_photo is None:
        st.error(
            "The selected photo could not be found."
        )

        if st.button(
            "Return to Photo Selection",
            type="primary",
            use_container_width=True,
            key="photo_editor_return_selection"
        ):
            go_to_page(
                "photo_comparison"
            )

        return

    original_image = selected_photo[
        "image"
    ]

    selected_index = selected_photo[
        "index"
    ]

    _, content_column, _ = st.columns(
        [0.45, 5, 0.45]
    )

    with content_column:
        show_progress_header()
        show_page_header()

        image_column, option_column = st.columns(
            [1.05, 1],
            gap="large"
        )

        # 왼쪽 이미지 자리를 먼저 생성합니다.
        with image_column:
            image_placeholder = st.empty()

        # 오른쪽 Background 옵션
        with option_column:
            (
                selected_background,
                selected_solid_color
            ) = show_background_options()

        render_html(
            '<div class="photo-editor-adjustment-space"></div>'
        )

        image_adjustments = (
            show_adjustment_options()
        )

        # 현재 선택된 옵션으로 편집 결과를 생성합니다.
        preview_result = run_photo_edit(
            original_image=original_image,
            selected_background=selected_background,
            selected_solid_color=selected_solid_color,
            image_adjustments=image_adjustments
        )

        if preview_result.get(
            "success",
            False
        ):
            preview_image = preview_result[
                "image"
            ]

            st.session_state[
                "photo_editor_preview_result"
            ] = preview_result

            st.session_state.pop(
                "photo_editor_error",
                None
            )

        else:
            preview_image = original_image

            error_message = preview_result.get(
                "message",
                "Preview could not be generated."
            )

            st.session_state[
                "photo_editor_error"
            ] = error_message

        # 왼쪽 영역에 현재 편집 결과를 표시합니다.
        image_placeholder.image(
            preview_image,
            use_container_width=True
        )

        editor_error = st.session_state.get(
            "photo_editor_error"
        )

        if editor_error:
            st.warning(
                editor_error
            )

        descriptions = preview_result.get(
            "descriptions",
            []
        )

        if (
            preview_result.get(
                "success",
                False
            )
            and descriptions
        ):
            with st.expander(
                "Applied changes"
            ):
                for description in descriptions:
                    st.write(
                        f"• {description}"
                    )

        render_html(
            '<div class="photo-editor-button-space"></div>'
        )

        reset_column, apply_column = st.columns(
            [1, 1.8]
        )

        with reset_column:
            if st.button(
                "Reset",
                use_container_width=True,
                key="photo_editor_reset_button"
            ):
                reset_editor_state()
                st.rerun()

        with apply_column:
            if st.button(
                "Apply & Continue",
                type="primary",
                use_container_width=True,
                key="photo_editor_apply_button",
                disabled=not preview_result.get(
                    "success",
                    False
                )
            ):
                st.session_state[
                    "photo_editor_original_image"
                ] = original_image

                st.session_state[
                    "optimized_image"
                ] = preview_image

                st.session_state[
                    "edited_image"
                ] = preview_image

                st.session_state[
                    "photo_editor_selected_index"
                ] = selected_index

                st.session_state[
                    "photo_editor_edit_option"
                ] = preview_result.get(
                    "edit_option"
                )

                st.session_state[
                    "photo_editor_background_type"
                ] = preview_result.get(
                    "background_type"
                )

                st.session_state[
                    "photo_editor_adjustments"
                ] = preview_result.get(
                    "adjustments",
                    image_adjustments
                )

                st.session_state[
                    "photo_editor_descriptions"
                ] = preview_result.get(
                    "descriptions",
                    []
                )

                go_to_page(
                    "image_edit_result"
                )