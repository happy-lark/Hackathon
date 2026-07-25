"""
pages/photo_editor.py

Step 6. Optimize Your Photo

역할:
- 선택된 사진 불러오기
- 배경 옵션 선택
- 단색 배경 색상 선택
- 밝기, 대비, 채도, 선명도 조절
- analysis/image_editor.py를 통해 실제 이미지 편집
- 최종 편집 이미지를 다음 페이지로 전달
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
    "Office": "office",
    "Urban": "urban",
    "Nature": "nature"
}


SOLID_COLOR_OPTIONS = {
    "Soft Gray": "#D9DCE3",
    "Light Blue": "#BFD7F4",
    "Warm Beige": "#D6A56F",
    "Soft Cream": "#F1E2C7",
    "Muted Teal": "#72AFC4"
}


PERSONAL_COLOR_RECOMMENDATIONS = {
    "Spring Warm": "Warm Beige",
    "Summer Cool": "Light Blue",
    "Autumn Warm": "Warm Beige",
    "Winter Cool": "Soft Gray"
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
    들여쓰기와 줄바꿈을 제거합니다.
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
    HTML을 Streamlit 화면에 표시합니다.
    """

    st.markdown(
        clean_html(html_content),
        unsafe_allow_html=True
    )


def extract_pil_image(image_item):
    """
    session_state에 저장된 여러 이미지 형식에서
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
    Match Report에서 저장한 퍼스널컬러 결과를 가져옵니다.
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


def get_personal_color_season():
    """
    Match Report에서 저장된 계절 타입을 가져옵니다.
    """

    color_result = st.session_state.get(
        "match_report_color_result",
        {}
    )

    if not isinstance(
        color_result,
        dict
    ):
        return None

    season = color_result.get(
        "season"
    )

    if isinstance(
        season,
        str
    ):
        return season

    return None


def get_recommended_color_name():
    """
    퍼스널컬러에 따라 추천 단색 배경 이름을 반환합니다.
    """

    season = get_personal_color_season()

    return PERSONAL_COLOR_RECOMMENDATIONS.get(
        season,
        "Light Blue"
    )


def initialize_editor_state():
    """
    Photo Editor에 필요한 session_state를 초기화합니다.
    """

    recommended_color = (
        get_recommended_color_name()
    )

    st.session_state.setdefault(
        "photo_editor_background",
        "Original"
    )

    st.session_state.setdefault(
        "photo_editor_solid_color_name",
        recommended_color
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
    모든 편집 값을 기본 상태로 초기화합니다.
    """

    st.session_state[
        "photo_editor_background"
    ] = "Original"

    st.session_state[
        "photo_editor_solid_color_name"
    ] = get_recommended_color_name()

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
    0.70~1.30 보정 배율로 변환합니다.
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
            + slider_value * 0.01
        )
    )


def build_image_adjustments():
    """
    슬라이더 값을 이미지 편집 배율로 변환합니다.
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
    모든 보정값이 기본값인지 확인합니다.
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
    배경과 Adjustments 설정을 기반으로
    이미지 편집 유형을 결정합니다.
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
    선택된 배경 설정을 background_editor 형식으로 변환합니다.
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
    현재 설정으로 실제 이미지 편집을 실행합니다.
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
    상단 Back 버튼과 진행 단계를 표시합니다.
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


def show_solid_color_options():
    """
    원형 색상 Swatch와 추천 색상을 표시합니다.
    """

    recommended_color_name = (
        get_recommended_color_name()
    )

    personal_color_season = (
        get_personal_color_season()
    )

    render_html(
        f"""
        <div class="photo-editor-color-header">
            <span>Recommended colors</span>

            <small>
                Based on {personal_color_season or "your photo"}
            </small>
        </div>
        """
    )

    color_names = list(
        SOLID_COLOR_OPTIONS.keys()
    )

    color_columns = st.columns(
        len(color_names)
    )

    for column, color_name in zip(
        color_columns,
        color_names
    ):
        hex_color = SOLID_COLOR_OPTIONS[
            color_name
        ]

        is_selected = (
            st.session_state.get(
                "photo_editor_solid_color_name"
            )
            == color_name
        )

        is_recommended = (
            color_name
            == recommended_color_name
        )

        key_suffix = (
            color_name.lower()
            .replace(" ", "_")
        )

        with column:
            button_text = (
                "✓"
                if is_selected
                else ""
            )

            if st.button(
                button_text,
                key=(
                    "photo_editor_color_"
                    f"{key_suffix}"
                ),
                use_container_width=True
            ):
                st.session_state[
                    "photo_editor_solid_color_name"
                ] = color_name

                st.rerun()

            recommended_html = (
                '<span class="recommended-badge">'
                'Recommended'
                '</span>'
                if is_recommended
                else ""
            )

            render_html(
                f"""
                <div class="photo-editor-color-label">
                    <span>{color_name}</span>
                    {recommended_html}
                </div>
                """
            )

    selected_color_name = st.session_state.get(
        "photo_editor_solid_color_name",
        recommended_color_name
    )

    return SOLID_COLOR_OPTIONS[
        selected_color_name
    ]


def show_background_options():
    """
    Background 카드 옵션과 단색 추천색을 표시합니다.
    """

    render_html(
        """
        <div class="photo-editor-section-title">
            Background
        </div>
        """
    )

    selected_background = st.radio(
        "Background",
        options=BACKGROUND_OPTIONS,
        key="photo_editor_background",
        label_visibility="collapsed"
    )

    selected_solid_color = None

    if selected_background == "Solid Color":
        selected_solid_color = (
            show_solid_color_options()
        )

    return (
        selected_background,
        selected_solid_color
    )


def show_adjustment_options():
    """
    이미지 보정 슬라이더를 표시합니다.
    """

    render_html(
        """
        <div class="photo-editor-adjustments-title">
            Adjustments
        </div>
        """
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

        with image_column:
            image_placeholder = st.empty()

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

            st.session_state[
                "photo_editor_error"
            ] = preview_result.get(
                "message",
                "Preview could not be generated."
            )

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