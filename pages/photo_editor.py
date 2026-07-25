"""
pages/photo_editor.py

Step 7. Optimize Your Photo

역할:
- 선택된 사진 불러오기
- 배경 옵션 선택
- Match Report의 추천 색상을 단색 배경 후보로 사용
- 밝기, 대비, 채도, 선명도 조절
- analysis/image_editor.py를 통해 실제 이미지 편집
- Applied Changes를 영어로 표시
- 최종 편집 이미지를 다음 페이지로 전달
"""

import re

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


TOTAL_STEPS = 7
CURRENT_STEP = 7


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


# Match Report의 추천 색상 결과가 없을 때만 사용합니다.
DEFAULT_RECOMMENDED_COLORS = [
    "#D9DCE3",
    "#BFD7F4",
    "#D6A56F",
    "#F1E2C7",
    "#72AFC4",
    "#8F8DBD"
]


DEFAULT_IMAGE_ADJUSTMENTS = {
    "brightness": 1.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "sharpness": 1.0
}


def clean_html(html_content):
    """
    HTML이 Streamlit 코드 블록으로 표시되지 않도록
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
        clean_html(
            html_content
        ),
        unsafe_allow_html=True
    )


def build_progress_html():
    """
    현재 단계에 맞춰 1~7 진행 표시 HTML을 생성합니다.
    """

    progress_parts = []

    for step in range(
        1,
        TOTAL_STEPS + 1
    ):
        if step < CURRENT_STEP:
            state_class = "completed"

        elif step == CURRENT_STEP:
            state_class = "active"

        else:
            state_class = ""

        progress_parts.append(
            f"""
            <span class="photo-editor-progress-dot {state_class}">
                {step}
            </span>
            """
        )

        if step < TOTAL_STEPS:
            line_class = (
                "completed"
                if step < CURRENT_STEP
                else ""
            )

            progress_parts.append(
                f"""
                <span
                    class="photo-editor-progress-line {line_class}"
                ></span>
                """
            )

    return "".join(
        progress_parts
    )


def extract_pil_image(image_item):
    """
    session_state에 저장된 여러 이미지 형식에서
    PIL 이미지를 추출합니다.
    """

    if isinstance(
        image_item,
        Image.Image
    ):
        return image_item.convert(
            "RGB"
        )

    if isinstance(
        image_item,
        dict
    ):
        possible_keys = [
            "image",
            "original_image",
            "edited_image",
            "result_image"
        ]

        for key in possible_keys:
            image = image_item.get(
                key
            )

            if isinstance(
                image,
                Image.Image
            ):
                return image.convert(
                    "RGB"
                )

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
        uploaded_images[
            selected_index
        ]
    )

    if selected_image is None:
        return None

    return {
        "image": selected_image,
        "index": selected_index
    }


def normalize_hex_color(value):
    """
    색상값을 올바른 #RRGGBB 형식으로 변환합니다.
    """

    if not isinstance(
        value,
        str
    ):
        return None

    value = value.strip().upper()

    if not value.startswith("#"):
        value = f"#{value}"

    if len(value) != 7:
        return None

    valid_characters = set(
        "0123456789ABCDEF"
    )

    if not all(
        character in valid_characters
        for character in value[1:]
    ):
        return None

    return value


def get_color_analysis_result():
    """
    Match Report에서 저장한 퍼스널컬러 분석 원본 결과를 가져옵니다.
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


def get_recommended_palette():
    """
    Match Report의 Color Recommendation에서 사용한
    추천 색상 목록을 그대로 가져옵니다.

    결과가 없거나 잘못된 경우 기본 팔레트를 반환합니다.
    """

    color_result = st.session_state.get(
        "match_report_color_result",
        {}
    )

    if not isinstance(
        color_result,
        dict
    ):
        return DEFAULT_RECOMMENDED_COLORS.copy()

    raw_colors = color_result.get(
        "colors",
        []
    )

    if not isinstance(
        raw_colors,
        list
    ):
        return DEFAULT_RECOMMENDED_COLORS.copy()

    normalized_colors = []

    for color in raw_colors:
        normalized_color = normalize_hex_color(
            color
        )

        if (
            normalized_color
            and normalized_color
            not in normalized_colors
        ):
            normalized_colors.append(
                normalized_color
            )

    if not normalized_colors:
        return DEFAULT_RECOMMENDED_COLORS.copy()

    return normalized_colors


def get_default_recommended_color():
    """
    추천 팔레트의 첫 번째 색상을 기본 선택값으로 사용합니다.
    """

    recommended_palette = (
        get_recommended_palette()
    )

    return recommended_palette[0]


def initialize_editor_state():
    """
    Photo Editor에 필요한 session_state를 초기화합니다.
    """

    recommended_palette = (
        get_recommended_palette()
    )

    default_color = (
        recommended_palette[0]
    )

    st.session_state.setdefault(
        "photo_editor_background",
        "Original"
    )

    selected_color = st.session_state.get(
        "photo_editor_solid_color"
    )

    if selected_color not in recommended_palette:
        st.session_state[
            "photo_editor_solid_color"
        ] = default_color

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
        "photo_editor_solid_color"
    ] = get_default_recommended_color()

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
            + slider_value
            * 0.01
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
            color_analysis_result=color_analysis_result
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
        "image": edited_image.convert(
            "RGB"
        ),
        "descriptions": first_result.get(
            "descriptions",
            []
        ),
        "edit_option": edit_option,
        "background_type": background_type,
        "adjustments": image_adjustments
    }


def translate_applied_change(
    description
):
    """
    이미지 편집 모듈이 반환한 한국어 설명을
    발표용 영어 문장으로 변환합니다.

    이미 영어인 설명은 그대로 반환합니다.
    """

    if not isinstance(
        description,
        str
    ):
        return str(description)

    translated = description.strip()

    if not translated:
        return ""

    # ========================================
    # 배경 변경 설명
    # ========================================

    background_match = re.search(
        (
            r"사진 속 인물은 유지하고 "
            r"기존 배경만 (.+?) 배경으로 "
            r"변경했습니다"
        ),
        translated
    )

    if background_match:
        background_name = (
            background_match.group(1)
            .strip()
        )

        if (
            "실제 배경 파일이 없어"
            in translated
            or "자동 생성된"
            in translated
        ):
            return (
                "The person was preserved while the original "
                f"background was replaced with a {background_name} "
                "background. Because no background image file was "
                f"available, an automatically generated "
                f"{background_name} background was used."
            )

        return (
            "The person was preserved while the original "
            f"background was replaced with a "
            f"{background_name} background."
        )

    # ========================================
    # Blur 배경
    # ========================================

    if "블러" in translated:
        blur_match = re.search(
            r"블러 강도\s*([0-9.]+)",
            translated
        )

        if blur_match:
            blur_strength = (
                blur_match.group(1)
            )

            return (
                "The person was kept sharp while a blur "
                f"strength of {blur_strength} was applied "
                "to the original background."
            )

        return (
            "The person was kept sharp while the "
            "original background was blurred."
        )

    # ========================================
    # 단색 배경
    # ========================================

    solid_color_match = re.search(
        (
            r"배경만\s*"
            r"(#[0-9A-Fa-f]{6}|.+?)\s*"
            r"단색으로 변경했습니다"
        ),
        translated
    )

    if solid_color_match:
        color_value = (
            solid_color_match.group(1)
            .strip()
        )

        return (
            "The person was preserved while the background "
            f"was replaced with the solid color {color_value}."
        )

    # ========================================
    # 이미지 보정 설명
    # ========================================

    adjustment_sentences = []

    brightness_up = re.search(
        r"밝기를 약\s*(\d+)%\s*높여",
        translated
    )

    brightness_down = re.search(
        r"밝기를 약\s*(\d+)%\s*낮춰",
        translated
    )

    contrast_up = re.search(
        r"대비를 약\s*(\d+)%\s*높여",
        translated
    )

    contrast_down = re.search(
        r"대비를 약\s*(\d+)%\s*낮춰",
        translated
    )

    saturation_up = re.search(
        r"채도를 약\s*(\d+)%\s*높여",
        translated
    )

    saturation_down = re.search(
        r"채도를 약\s*(\d+)%\s*낮춰",
        translated
    )

    sharpness_up = re.search(
        r"선명도를 약\s*(\d+)%\s*높여",
        translated
    )

    sharpness_down = re.search(
        r"선명도를 약\s*(\d+)%\s*낮춰",
        translated
    )

    if brightness_up:
        adjustment_sentences.append(
            "Brightness was increased by approximately "
            f"{brightness_up.group(1)}% to make the photo brighter."
        )

    elif brightness_down:
        adjustment_sentences.append(
            "Brightness was reduced by approximately "
            f"{brightness_down.group(1)}% to lower the exposure."
        )

    elif (
        "밝기는 원본 상태" in translated
        or "밝기는 원본 상태를 유지" in translated
    ):
        adjustment_sentences.append(
            "Brightness was kept at its original level."
        )

    if contrast_up:
        adjustment_sentences.append(
            "Contrast was increased by approximately "
            f"{contrast_up.group(1)}% to make tonal differences clearer."
        )

    elif contrast_down:
        adjustment_sentences.append(
            "Contrast was reduced by approximately "
            f"{contrast_down.group(1)}% to create softer tonal transitions."
        )

    elif (
        "대비는 원본 상태" in translated
        or "대비는 원본 상태를 유지" in translated
    ):
        adjustment_sentences.append(
            "Contrast was kept at its original level."
        )

    if saturation_up:
        adjustment_sentences.append(
            "Saturation was increased by approximately "
            f"{saturation_up.group(1)}% to enhance the colors."
        )

    elif saturation_down:
        adjustment_sentences.append(
            "Saturation was reduced by approximately "
            f"{saturation_down.group(1)}% for a more muted appearance."
        )

    elif (
        "채도는 원본 상태" in translated
        or "채도는 원본 상태를 유지" in translated
    ):
        adjustment_sentences.append(
            "Saturation was kept at its original level."
        )

    if sharpness_up:
        adjustment_sentences.append(
            "Sharpness was increased by approximately "
            f"{sharpness_up.group(1)}% to enhance image details."
        )

    elif sharpness_down:
        adjustment_sentences.append(
            "Sharpness was reduced by approximately "
            f"{sharpness_down.group(1)}% for a softer appearance."
        )

    elif (
        "선명도는 원본 상태" in translated
        or "선명도는 원본 상태를 유지" in translated
    ):
        adjustment_sentences.append(
            "Sharpness was kept at its original level."
        )

    if adjustment_sentences:
        return " ".join(
            adjustment_sentences
        )

    # 변환 규칙에 해당하지 않는 영어 문장은 그대로 표시합니다.
    return translated


def inject_palette_button_styles(
    palette
):
    """
    Match Report의 추천 색상에 맞게
    각 Streamlit 색상 버튼의 배경 CSS를 동적으로 생성합니다.
    """

    style_rules = []

    for index, hex_color in enumerate(
        palette
    ):
        style_rules.append(
            f"""
            .st-key-photo_editor_palette_{index} button {{
                background: {hex_color} !important;
            }}

            .st-key-photo_editor_palette_{index} button:hover {{
                background: {hex_color} !important;
            }}

            .st-key-photo_editor_palette_{index} button:focus {{
                background: {hex_color} !important;
            }}
            """
        )

    render_html(
        f"""
        <style>
            {''.join(style_rules)}
        </style>
        """
    )


def show_progress_header():
    """
    상단 Back 버튼과 1~7 진행 단계를 표시합니다.
    """

    (
        back_column,
        progress_column,
        empty_column
    ) = st.columns(
        [1.05, 5.4, 1.05],
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
            f"""
            <div class="photo-editor-progress">
                {build_progress_html()}
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
                Step 7. Optimize Your Photo
            </div>

            <div class="photo-editor-description">
                Choose editing options to match your goal.
            </div>
        </div>
        """
    )


def show_solid_color_options():
    """
    Match Report의 Color Recommendation 팔레트를
    단색 배경 선택지로 표시합니다.
    """

    recommended_palette = (
        get_recommended_palette()
    )

    personal_color_season = (
        get_personal_color_season()
    )

    selected_color = st.session_state.get(
        "photo_editor_solid_color",
        recommended_palette[0]
    )

    if selected_color not in recommended_palette:
        selected_color = (
            recommended_palette[0]
        )

        st.session_state[
            "photo_editor_solid_color"
        ] = selected_color

    inject_palette_button_styles(
        recommended_palette
    )

    render_html(
        f"""
        <div class="photo-editor-color-header">
            <span>
                Recommended colors
            </span>

            <small>
                Based on {personal_color_season or "your photo"}
            </small>
        </div>
        """
    )

    color_columns = st.columns(
        len(recommended_palette)
    )

    for index, (
        column,
        hex_color
    ) in enumerate(
        zip(
            color_columns,
            recommended_palette
        )
    ):
        is_selected = (
            selected_color
            == hex_color
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
                    f"photo_editor_palette_{index}"
                ),
                use_container_width=True,
                help=hex_color
            ):
                st.session_state[
                    "photo_editor_solid_color"
                ] = hex_color

                st.rerun()

            selected_badge = (
                """
                <span class="recommended-badge">
                    Selected
                </span>
                """
                if is_selected
                else ""
            )

            render_html(
                f"""
                <div class="photo-editor-color-label">
                    <span>
                        {hex_color}
                    </span>

                    {selected_badge}
                </div>
                """
            )

    return st.session_state.get(
        "photo_editor_solid_color",
        recommended_palette[0]
    )


def show_background_options():
    """
    Background 카드 옵션과 추천 단색 팔레트를 표시합니다.
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
    Step 7. Optimize Your Photo 페이지입니다.
    """

    initialize_editor_state()

    selected_photo = (
        get_selected_photo()
    )

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
            image_placeholder = (
                st.empty()
            )

        with option_column:
            (
                selected_background,
                selected_solid_color
            ) = show_background_options()

        render_html(
            """
            <div class="photo-editor-adjustment-space">
            </div>
            """
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
                "Applied Changes",
                expanded=True
            ):
                for description in descriptions:
                    english_description = (
                        translate_applied_change(
                            description
                        )
                    )

                    if english_description:
                        st.write(
                            f"• {english_description}"
                        )

        render_html(
            """
            <div class="photo-editor-button-space">
            </div>
            """
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

                english_descriptions = [
                    translate_applied_change(
                        description
                    )
                    for description in preview_result.get(
                        "descriptions",
                        []
                    )
                ]

                st.session_state[
                    "photo_editor_descriptions"
                ] = english_descriptions

                go_to_page(
                    "image_edit_result"
                )