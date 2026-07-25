"""
pages/match_report.py

선택된 사진과 Target Persona의 일치도를 보여주는
Image Match Report 페이지입니다.

사용 데이터:
- 선택된 사진의 Persona 분석 결과
- Target Persona
- 얼굴 특징
- 이미지 품질 특징
- Usage Context
- Personal Color 분석 결과
"""

from textwrap import dedent

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from analysis.color_analyzer import (
    analyze_multiple_personal_colors
)
from utils.navigation import go_to_page


PERSONA_AXES = [
    "Professional",
    "Confident",
    "Approachable",
    "Creative"
]


SEASON_PALETTES = {
    "Spring Warm": [
        "#4F8EDC",
        "#F39A67",
        "#F3C969",
        "#75B798",
        "#FFF0D4",
        "#C98B65"
    ],
    "Summer Cool": [
        "#7197CE",
        "#8F8DBD",
        "#C8B9D9",
        "#9FB7C9",
        "#E8DDE8",
        "#7C879F"
    ],
    "Autumn Warm": [
        "#8A5A44",
        "#B87942",
        "#C7A24A",
        "#6F7B45",
        "#D6B98C",
        "#55473F"
    ],
    "Winter Cool": [
        "#355FA8",
        "#26345C",
        "#828796",
        "#D6D6D6",
        "#F2F2F2",
        "#A88E7A"
    ]
}


PERSONA_IMPROVEMENT_MESSAGES = {
    "Professional": (
        "Use a straighter pose and a cleaner composition "
        "to strengthen the professional impression"
    ),
    "Confident": (
        "Look more directly toward the camera to create "
        "a stronger confident impression"
    ),
    "Approachable": (
        "Try a slightly softer expression or natural smile "
        "to improve approachability"
    ),
    "Creative": (
        "Use a more distinctive composition or color accent "
        "to strengthen the creative impression"
    )
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
    HTML을 Streamlit에 렌더링합니다.
    """

    st.markdown(
        clean_html(html_content),
        unsafe_allow_html=True
    )


def clamp(
    value,
    minimum=0.0,
    maximum=100.0
):
    """
    숫자를 지정된 범위로 제한합니다.
    """

    return max(
        minimum,
        min(maximum, value)
    )


def extract_pil_image(value):
    """
    session_state의 다양한 이미지 저장 형식에서
    PIL 이미지를 추출합니다.
    """

    if isinstance(value, Image.Image):
        return value.convert("RGB")

    if isinstance(value, dict):
        possible_keys = [
            "image",
            "original_image",
            "edited_image",
            "result_image"
        ]

        for key in possible_keys:
            image = value.get(key)

            if isinstance(image, Image.Image):
                return image.convert("RGB")

    return None


def normalize_persona_scores(raw_scores):
    """
    Persona 점수를 표준 키와 0~100 값으로 변환합니다.
    """

    if not isinstance(raw_scores, dict):
        return None

    normalized_lookup = {
        str(key).strip().lower(): value
        for key, value in raw_scores.items()
    }

    normalized_scores = {}

    for axis in PERSONA_AXES:
        value = normalized_lookup.get(
            axis.lower()
        )

        if value is None:
            return None

        try:
            numeric_value = float(value)

        except (TypeError, ValueError):
            return None

        if 0 <= numeric_value <= 1:
            numeric_value *= 100

        normalized_scores[axis] = round(
            clamp(numeric_value),
            1
        )

    return normalized_scores


def get_selected_photo_data():
    """
    선택된 사진, 사진 번호, 사진별 분석 결과를 가져옵니다.
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
        selected_index = int(selected_index)

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

    analysis_result = st.session_state.get(
        "analysis_result",
        {}
    )

    individual_results = analysis_result.get(
        "individual_results",
        []
    )

    selected_analysis = None

    for fallback_index, result in enumerate(
        individual_results
    ):
        if not isinstance(result, dict):
            continue

        image_index = result.get(
            "image_index",
            fallback_index
        )

        try:
            image_index = int(image_index)

        except (TypeError, ValueError):
            image_index = fallback_index

        if image_index == selected_index:
            selected_analysis = result
            break

    # 사진이 한 장뿐인 경우 전체 결과를 보조적으로 사용합니다.
    if selected_analysis is None:
        selected_analysis = analysis_result

    return {
        "image": selected_image,
        "image_index": selected_index,
        "analysis": selected_analysis
    }


def extract_selected_scores(
    selected_analysis
):
    """
    선택된 사진 분석 결과에서 Persona 점수를 추출합니다.
    """

    possible_keys = [
        "persona_scores",
        "scores",
        "detected_persona"
    ]

    for key in possible_keys:
        scores = normalize_persona_scores(
            selected_analysis.get(key)
        )

        if scores:
            return scores

    return normalize_persona_scores(
        selected_analysis
    )


def get_target_persona():
    """
    사용자가 설정한 Target Persona를 가져옵니다.
    """

    possible_keys = [
        "target_persona",
        "target_slider_values",
        "target_persona_scores"
    ]

    for key in possible_keys:
        scores = normalize_persona_scores(
            st.session_state.get(key)
        )

        if scores:
            return scores

    return None


def calculate_axis_alignment(
    detected_persona,
    target_persona
):
    """
    Persona 축별 유사도를 계산합니다.

    Target과 사진 점수 차이가 작을수록
    Alignment 값이 높습니다.
    """

    return {
        axis: round(
            clamp(
                100
                - abs(
                    detected_persona[axis]
                    - target_persona[axis]
                )
            )
        )
        for axis in PERSONA_AXES
    }


def calculate_overall_match_score(
    detected_persona,
    target_persona
):
    """
    Target Persona가 높은 항목에 더 큰 가중치를 주어
    전체 Match Score를 계산합니다.
    """

    target_total = sum(
        target_persona.values()
    )

    if target_total <= 0:
        weights = {
            axis: 1 / len(PERSONA_AXES)
            for axis in PERSONA_AXES
        }

    else:
        weights = {
            axis: (
                target_persona[axis]
                / target_total
            )
            for axis in PERSONA_AXES
        }

    weighted_difference = sum(
        weights[axis]
        * abs(
            detected_persona[axis]
            - target_persona[axis]
        )
        for axis in PERSONA_AXES
    )

    return round(
        clamp(
            100 - weighted_difference
        )
    )


def measure_image_quality(
    image
):
    """
    OpenCV를 사용해 이미지 품질 특징을 측정합니다.

    Background Complexity는 사진 가장자리 영역의
    엣지 밀도를 사용한 시각적 복잡도 추정치입니다.
    """

    rgb_array = np.asarray(
        image.convert("RGB")
    )

    gray_array = cv2.cvtColor(
        rgb_array,
        cv2.COLOR_RGB2GRAY
    )

    brightness = (
        float(
            np.mean(gray_array)
        )
        / 255
        * 100
    )

    contrast = (
        float(
            np.std(gray_array)
        )
        / 64
        * 100
    )

    sharpness_raw = cv2.Laplacian(
        gray_array,
        cv2.CV_64F
    ).var()

    sharpness = (
        float(sharpness_raw)
        / 500
        * 100
    )

    edge_map = cv2.Canny(
        gray_array,
        70,
        150
    )

    height, width = gray_array.shape

    border_mask = np.ones(
        (height, width),
        dtype=bool
    )

    center_y_start = int(
        height * 0.18
    )
    center_y_end = int(
        height * 0.82
    )
    center_x_start = int(
        width * 0.22
    )
    center_x_end = int(
        width * 0.78
    )

    border_mask[
        center_y_start:center_y_end,
        center_x_start:center_x_end
    ] = False

    border_edges = edge_map[
        border_mask
    ]

    if border_edges.size:
        edge_ratio = float(
            np.mean(
                border_edges > 0
            )
        )

    else:
        edge_ratio = 0.0

    background_complexity = (
        edge_ratio
        / 0.18
        * 100
    )

    return {
        "Brightness": round(
            clamp(brightness),
            1
        ),
        "Contrast": round(
            clamp(contrast),
            1
        ),
        "Sharpness": round(
            clamp(sharpness),
            1
        ),
        "Background Complexity": round(
            clamp(background_complexity),
            1
        )
    }


def get_feature(
    features,
    feature_name
):
    """
    얼굴 특징 점수를 안전하게 가져옵니다.
    """

    try:
        return float(
            features.get(
                feature_name,
                0
            )
        )

    except (TypeError, ValueError):
        return 0.0


def add_unique_candidate(
    candidates,
    priority,
    text
):
    """
    중복되지 않는 피드백 후보를 추가합니다.
    """

    existing_texts = {
        item[1]
        for item in candidates
    }

    if text not in existing_texts:
        candidates.append(
            (
                priority,
                text
            )
        )


def generate_strengths_and_improvements(
    features,
    image_quality,
    target_persona,
    detected_persona,
    axis_alignment,
    usage_context
):
    """
    얼굴 특징, 이미지 품질, Persona 차이,
    Usage Context를 바탕으로 피드백을 생성합니다.

    API나 랜덤 문장을 사용하지 않으며,
    사진의 실제 분석값에 따라 결과가 달라집니다.
    """

    strengths = []
    improvements = []

    face_centering = get_feature(
        features,
        "Face Centering"
    )

    frontality = get_feature(
        features,
        "Frontality"
    )

    head_level = get_feature(
        features,
        "Head Level"
    )

    smile = get_feature(
        features,
        "Smile"
    )

    eye_openness = get_feature(
        features,
        "Eye Openness"
    )

    mouth_control = get_feature(
        features,
        "Mouth Control"
    )

    brightness = image_quality[
        "Brightness"
    ]

    contrast = image_quality[
        "Contrast"
    ]

    sharpness = image_quality[
        "Sharpness"
    ]

    background_complexity = image_quality[
        "Background Complexity"
    ]

    # =========================
    # Strengths
    # =========================

    if face_centering >= 72:
        add_unique_candidate(
            strengths,
            face_centering,
            "Face is clearly visible and well centered"
        )

    if frontality >= 75:
        add_unique_candidate(
            strengths,
            frontality,
            "Direct camera angle creates a clear impression"
        )

    if head_level >= 75:
        add_unique_candidate(
            strengths,
            head_level,
            "Level head position gives the photo a polished look"
        )

    if smile >= 42:
        add_unique_candidate(
            strengths,
            smile,
            "Natural expression supports approachability"
        )

    if eye_openness >= 65:
        add_unique_candidate(
            strengths,
            eye_openness,
            "Open eyes improve clarity and engagement"
        )

    if mouth_control >= 68:
        add_unique_candidate(
            strengths,
            mouth_control,
            "Controlled expression creates a composed appearance"
        )

    if 43 <= brightness <= 75:
        add_unique_candidate(
            strengths,
            82,
            "Lighting is balanced across the face"
        )

    if contrast >= 30:
        add_unique_candidate(
            strengths,
            min(contrast, 90),
            "Clear tonal contrast helps facial details stand out"
        )

    if sharpness >= 30:
        add_unique_candidate(
            strengths,
            min(sharpness, 90),
            "Facial details appear clear and sharp"
        )

    for axis in PERSONA_AXES:
        if axis_alignment[axis] >= 85:
            add_unique_candidate(
                strengths,
                axis_alignment[axis],
                (
                    f"{axis} impression closely matches "
                    "your selected target"
                )
            )

    # =========================
    # Areas to Improve
    # =========================

    if face_centering < 62:
        add_unique_candidate(
            improvements,
            100 - face_centering,
            "Use a tighter crop and place the face closer to the center"
        )

    if frontality < 65:
        add_unique_candidate(
            improvements,
            100 - frontality,
            "Turn slightly more toward the camera"
        )

    if head_level < 65:
        add_unique_candidate(
            improvements,
            100 - head_level,
            "Keep the head more level for a balanced composition"
        )

    if eye_openness < 52:
        add_unique_candidate(
            improvements,
            100 - eye_openness,
            "Choose a frame where the eyes are more open"
        )

    if brightness < 40:
        add_unique_candidate(
            improvements,
            100 - brightness,
            "Increase brightness slightly to make the face clearer"
        )

    elif brightness > 82:
        add_unique_candidate(
            improvements,
            brightness,
            "Reduce exposure slightly to preserve facial detail"
        )

    if contrast < 24:
        add_unique_candidate(
            improvements,
            100 - contrast,
            "Increase color contrast slightly"
        )

    if sharpness < 20:
        add_unique_candidate(
            improvements,
            100 - sharpness,
            "Use a sharper image with clearer facial details"
        )

    if background_complexity >= 58:
        add_unique_candidate(
            improvements,
            background_complexity,
            "Use a simpler background with fewer visual distractions"
        )

    for axis in PERSONA_AXES:
        gap = (
            target_persona[axis]
            - detected_persona[axis]
        )

        if gap >= 12:
            add_unique_candidate(
                improvements,
                gap,
                PERSONA_IMPROVEMENT_MESSAGES[
                    axis
                ]
            )

    # Usage Context에 따른 추가 판단
    if usage_context in {
        "professional_profile",
        "resume"
    }:
        if (
            axis_alignment["Professional"]
            < 78
        ):
            add_unique_candidate(
                improvements,
                80,
                (
                    "For a professional profile, use a cleaner "
                    "background and a more formal composition"
                )
            )

    elif usage_context == "networking":
        if (
            axis_alignment["Approachable"]
            < 78
        ):
            add_unique_candidate(
                improvements,
                80,
                (
                    "For networking use, a slightly warmer "
                    "expression would feel more inviting"
                )
            )

    elif usage_context == "creator":
        if (
            axis_alignment["Creative"]
            < 78
        ):
            add_unique_candidate(
                improvements,
                80,
                (
                    "For personal branding, consider a more "
                    "distinctive color or composition"
                )
            )

    strengths.sort(
        key=lambda item: item[0],
        reverse=True
    )

    improvements.sort(
        key=lambda item: item[0],
        reverse=True
    )

    strength_texts = [
        item[1]
        for item in strengths[:4]
    ]

    improvement_texts = [
        item[1]
        for item in improvements[:4]
    ]

    if not strength_texts:
        strength_texts = [
            "The photo maintains a consistent overall presentation"
        ]

    if not improvement_texts:
        improvement_texts = [
            "No major visual issues were detected"
        ]

    return (
        strength_texts,
        improvement_texts
    )


def find_personal_color_season(
    value
):
    """
    color_analyzer.py의 반환 구조가 달라도
    계절 타입 문자열을 재귀적으로 찾습니다.
    """

    if isinstance(value, str):
        normalized_value = (
            value.strip()
            .lower()
        )

        for season_name in SEASON_PALETTES:
            if (
                season_name.lower()
                in normalized_value
            ):
                return season_name

        return None

    if isinstance(value, dict):
        preferred_keys = [
            "season",
            "personal_color",
            "predicted_season",
            "dominant_season",
            "result",
            "tone"
        ]

        for key in preferred_keys:
            if key in value:
                season = find_personal_color_season(
                    value[key]
                )

                if season:
                    return season

        for nested_value in value.values():
            season = find_personal_color_season(
                nested_value
            )

            if season:
                return season

    if isinstance(value, list):
        for item in value:
            season = find_personal_color_season(
                item
            )

            if season:
                return season

    return None


def analyze_selected_personal_color(
    selected_image,
    selected_index
):
    """
    선택된 사진의 Personal Color를 분석합니다.

    페이지 rerun 때마다 다시 분석하지 않도록
    session_state에 결과를 저장합니다.
    """

    cached_result = st.session_state.get(
        "match_report_color_result"
    )

    cached_index = st.session_state.get(
        "match_report_color_index"
    )

    if (
        cached_result
        and cached_index == selected_index
    ):
        return cached_result

    try:
        raw_result = (
            analyze_multiple_personal_colors(
                [selected_image]
            )
        )

        season = find_personal_color_season(
            raw_result
        )

    except Exception as error:
        raw_result = {
            "success": False,
            "error": str(error)
        }

        season = None

    result = {
        "season": season,
        "colors": (
            SEASON_PALETTES.get(
                season,
                []
            )
        ),
        "raw_result": raw_result
    }

    st.session_state[
        "match_report_color_result"
    ] = result

    st.session_state[
        "match_report_color_index"
    ] = selected_index

    return result


def get_match_label(
    score
):
    """
    Match Score에 따른 문구를 반환합니다.
    """

    if score >= 90:
        return (
            "Excellent Match",
            "Your photo strongly aligns with your goal."
        )

    if score >= 75:
        return (
            "Good Match",
            "You're on the right track!"
        )

    if score >= 60:
        return (
            "Fair Match",
            "A few adjustments could improve the match."
        )

    return (
        "Needs Improvement",
        "This photo can be optimized further."
    )


def build_alignment_html(
    detected_persona,
    target_persona,
    axis_alignment
):
    """
    Persona Alignment 카드 HTML을 생성합니다.
    """

    rows = []

    for axis in PERSONA_AXES:
        alignment = axis_alignment[
            axis
        ]

        target_value = round(
            target_persona[axis]
        )

        detected_value = round(
            detected_persona[axis]
        )

        rows.append(
            f"""
            <div class="match-alignment-row">
                <div class="match-alignment-heading">
                    <span>{axis}</span>
                    <strong>{alignment}%</strong>
                </div>

                <div class="match-alignment-meta">
                    Target {target_value}% · Photo {detected_value}%
                </div>

                <div class="match-alignment-track">
                    <div
                        class="match-alignment-fill"
                        style="width: {alignment}%;"
                    ></div>
                </div>
            </div>
            """
        )

    return "".join(rows)


def build_feedback_html(
    items,
    positive=True
):
    """
    Strengths 또는 Areas to Improve 목록 HTML을 생성합니다.
    """

    icon = "✓" if positive else "×"

    item_class = (
        "positive"
        if positive
        else "negative"
    )

    return "".join(
        f"""
        <div class="match-feedback-item {item_class}">
            <span>{icon}</span>
            <div>{item}</div>
        </div>
        """
        for item in items
    )


def build_color_swatches_html(
    colors
):
    """
    추천 색상 Swatch HTML을 생성합니다.
    """

    return "".join(
        f"""
        <div
            class="match-color-swatch"
            style="background-color: {hex_color};"
            title="{hex_color}"
        ></div>
        """
        for hex_color in colors
    )


def show_page_header():
    """
    Back 버튼과 페이지 제목을 표시합니다.
    """

    if st.button(
        "‹ Back",
        key="match_report_back"
    ):
        go_to_page(
            "photo_comparison"
        )

    render_html(
        """
        <div class="match-report-header">
            <div class="match-report-title">
                Your Image Match Report
            </div>

            <div class="match-report-description">
                Based on your target persona and selected context.
            </div>
        </div>
        """
    )


def show_match_report_page():
    """
    Image Match Report 페이지를 표시합니다.
    """

    show_page_header()

    selected_photo_data = (
        get_selected_photo_data()
    )

    target_persona = (
        get_target_persona()
    )

    if (
        selected_photo_data is None
        or target_persona is None
    ):
        st.error(
            "The selected photo or target persona "
            "could not be found."
        )

        if st.button(
            "Return to Upload",
            type="primary",
            use_container_width=True,
            key="match_report_return_upload"
        ):
            go_to_page("upload")

        return

    selected_image = selected_photo_data[
        "image"
    ]

    selected_index = selected_photo_data[
        "image_index"
    ]

    selected_analysis = selected_photo_data[
        "analysis"
    ]

    detected_persona = extract_selected_scores(
        selected_analysis
    )

    if detected_persona is None:
        st.error(
            "Persona scores for the selected photo "
            "could not be found."
        )

        return

    features = selected_analysis.get(
        "features",
        {}
    )

    usage_context = st.session_state.get(
        "usage_context",
        "other"
    )

    axis_alignment = (
        calculate_axis_alignment(
            detected_persona=detected_persona,
            target_persona=target_persona
        )
    )

    match_score = (
        calculate_overall_match_score(
            detected_persona=detected_persona,
            target_persona=target_persona
        )
    )

    match_label, match_message = (
        get_match_label(
            match_score
        )
    )

    image_quality = measure_image_quality(
        selected_image
    )

    strengths, improvements = (
        generate_strengths_and_improvements(
            features=features,
            image_quality=image_quality,
            target_persona=target_persona,
            detected_persona=detected_persona,
            axis_alignment=axis_alignment,
            usage_context=usage_context
        )
    )

    color_result = (
        analyze_selected_personal_color(
            selected_image=selected_image,
            selected_index=selected_index
        )
    )

    # 이후 편집 페이지에서도 사용할 수 있도록 저장합니다.
    st.session_state[
        "selected_photo_match_score"
    ] = match_score

    st.session_state[
        "selected_photo_alignment"
    ] = axis_alignment

    st.session_state[
        "selected_photo_quality"
    ] = image_quality

    st.session_state[
        "match_report_strengths"
    ] = strengths

    st.session_state[
        "match_report_improvements"
    ] = improvements

    alignment_html = build_alignment_html(
        detected_persona=detected_persona,
        target_persona=target_persona,
        axis_alignment=axis_alignment
    )

    render_html(
        f"""
        <div class="match-report-main-grid">
            <div class="match-score-card">
                <div class="match-card-title">
                    Overall Match Score
                </div>

                <div class="match-score-number">
                    {match_score}%
                </div>

                <div class="match-score-label">
                    {match_label}
                </div>

                <div class="match-score-message">
                    {match_message}
                </div>
            </div>

            <div class="match-alignment-card">
                <div class="match-card-title">
                    Persona Alignment
                </div>

                <div class="match-alignment-list">
                    {alignment_html}
                </div>
            </div>
        </div>
        """
    )

    strengths_html = build_feedback_html(
        strengths,
        positive=True
    )

    improvements_html = build_feedback_html(
        improvements,
        positive=False
    )

    render_html(
        f"""
        <div class="match-feedback-grid">
            <div class="match-feedback-card">
                <div class="match-card-title">
                    Strengths
                </div>

                <div class="match-feedback-list">
                    {strengths_html}
                </div>
            </div>

            <div class="match-feedback-card">
                <div class="match-card-title">
                    Areas to Improve
                </div>

                <div class="match-feedback-list">
                    {improvements_html}
                </div>
            </div>
        </div>
        """
    )

    season = color_result.get(
        "season"
    )

    colors = color_result.get(
        "colors",
        []
    )

    if season and colors:
        swatches_html = (
            build_color_swatches_html(
                colors
            )
        )

        color_description = (
            f"{season} colors are recommended "
            "based on the detected skin-tone features."
        )

    else:
        swatches_html = ""
        color_description = (
            "A reliable personal color result could "
            "not be calculated from this photo."
        )

    render_html(
        f"""
        <div class="match-color-card">
            <div class="match-card-title">
                Color Recommendation
            </div>

            <div class="match-color-description">
                {color_description}
            </div>

            <div class="match-color-swatches">
                {swatches_html}
            </div>
        </div>
        """
    )

    render_html(
        """
        <div class="match-report-notice">
            This report does not evaluate the person's actual
            personality, ability, intelligence, or suitability
            for a job. It only compares visual features in the
            selected photo with the image goal chosen by the user.
            Personal color results are also visual estimates and
            may vary depending on lighting and camera conditions.
        </div>
        """
    )

    render_html(
        '<div class="match-report-button-space"></div>'
    )

    if st.button(
        "Continue to Editing →",
        type="primary",
        use_container_width=True,
        key="match_report_continue_button"
    ):
        go_to_page(
            "photo_editor"
        )