import base64

from io import BytesIO
from textwrap import dedent

import streamlit as st
from PIL import Image, ImageDraw, ImageOps


def clean_html(html_content):
    """
    HTML의 들여쓰기와 불필요한 줄바꿈을 제거합니다.
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


def extract_pil_image(value):
    """
    session_state에 저장된 여러 이미지 형식에서
    실제 PIL 이미지를 찾아 반환합니다.

    지원 형식:
    - PIL Image
    - {"image": PIL Image}
    - {"edited_image": PIL Image}
    - {"optimized_image": PIL Image}
    - {"result_image": PIL Image}
    """

    if isinstance(value, Image.Image):
        return value.convert("RGB")

    if isinstance(value, dict):
        possible_keys = [
            "optimized_image",
            "edited_image",
            "result_image",
            "image",
            "output_image"
        ]

        for key in possible_keys:
            image = value.get(key)

            if isinstance(image, Image.Image):
                return image.convert("RGB")

    return None


def get_before_image():
    """
    사용자가 선택한 원본 사진을 가져옵니다.
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

    return extract_pil_image(
        uploaded_images[selected_index]
    )


def get_after_image():
    """
    Step 6에서 보정된 결과 이미지를 가져옵니다.

    Step 6 구현 방식이 달라도 대응할 수 있도록
    여러 session_state 키를 확인합니다.
    """

    possible_keys = [
        "optimized_image",
        "edited_image",
        "image_edit_result",
        "optimized_result",
        "edit_result"
    ]

    for key in possible_keys:
        value = st.session_state.get(key)

        image = extract_pil_image(value)

        if image is not None:
            return image

    return None


def image_to_data_uri(image):
    """
    PIL 이미지를 HTML img 태그에서 사용할 수 있는
    Base64 URI로 변환합니다.
    """

    buffer = BytesIO()

    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=92
    )

    encoded_image = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return (
        "data:image/jpeg;base64,"
        f"{encoded_image}"
    )


def image_to_png_bytes(image):
    """
    일반 PNG 다운로드용 bytes를 생성합니다.
    """

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue()


def create_circle_crop_bytes(image):
    """
    이미지를 정사각형으로 자른 후
    원형 투명 PNG로 변환합니다.
    """

    crop_size = min(
        image.width,
        image.height
    )

    square_image = ImageOps.fit(
        image.convert("RGBA"),
        (
            crop_size,
            crop_size
        ),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )

    mask = Image.new(
        "L",
        (
            crop_size,
            crop_size
        ),
        0
    )

    mask_draw = ImageDraw.Draw(mask)

    mask_draw.ellipse(
        (
            0,
            0,
            crop_size - 1,
            crop_size - 1
        ),
        fill=255
    )

    circle_image = Image.new(
        "RGBA",
        (
            crop_size,
            crop_size
        ),
        (
            255,
            255,
            255,
            0
        )
    )

    circle_image.paste(
        square_image,
        (
            0,
            0
        ),
        mask
    )

    buffer = BytesIO()

    circle_image.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue()


def get_nested_score(value):
    """
    dict 안에 저장된 Match Score를 찾아 반환합니다.
    """

    if not isinstance(value, dict):
        return None

    possible_keys = [
        "optimized_match_score",
        "after_match_score",
        "match_score",
        "score"
    ]

    for key in possible_keys:
        score = value.get(key)

        if score is None:
            continue

        try:
            return round(float(score))

        except (TypeError, ValueError):
            continue

    return None


def get_match_scores():
    """
    보정 전후 Match Score를 가져옵니다.

    Step 6에서 optimized_match_score를 저장하면
    해당 값을 우선 사용합니다.
    """

    before_score = st.session_state.get(
        "best_match_score",
        0
    )

    try:
        before_score = round(
            float(before_score)
        )

    except (TypeError, ValueError):
        before_score = 0

    after_score = st.session_state.get(
        "optimized_match_score"
    )

    if after_score is None:
        after_score = get_nested_score(
            st.session_state.get(
                "image_edit_result"
            )
        )

    try:
        if after_score is not None:
            after_score = round(
                float(after_score)
            )

    except (TypeError, ValueError):
        after_score = None

    # Step 6의 실제 재분석 점수가 아직 없는 경우를 위한
    # 임시 UI용 예상 점수입니다.
    if after_score is None:
        after_score = min(
            100,
            before_score + 9
        )

    before_score = max(
        0,
        min(before_score, 100)
    )

    after_score = max(
        0,
        min(after_score, 100)
    )

    return (
        before_score,
        after_score
    )


def get_improvement_summary():
    """
    Step 6에서 저장한 개선 내용을 가져옵니다.

    저장된 내용이 없으면 기본 안내 문구를 표시합니다.
    """

    possible_keys = [
        "improvement_summary",
        "applied_improvements",
        "edit_improvements"
    ]

    for key in possible_keys:
        improvements = st.session_state.get(
            key
        )

        if isinstance(improvements, list):
            valid_items = [
                str(item)
                for item in improvements
                if item
            ]

            if valid_items:
                return valid_items[:4]

    return [
        "Brighter and clearer lighting",
        "Cleaner background",
        "Better color harmony",
        "Optimized crop for professional use"
    ]


def build_improvements_html(improvements):
    """
    Improvement Summary 항목 HTML을 생성합니다.
    """

    return "".join(
        (
            '<div class="optimized-improvement-item">'
            '<span>✓</span>'
            f'<div>{item}</div>'
            '</div>'
        )
        for item in improvements
    )


def get_score_message(after_score):
    """
    최종 점수에 맞는 메시지를 반환합니다.
    """

    if after_score >= 90:
        return "Great Match!"

    if after_score >= 80:
        return "Strong Match!"

    if after_score >= 70:
        return "Good Match!"

    return "Improved Match"


def show_progress_header():
    """
    Back 표시와 Step 7 진행 상태를 출력합니다.

    Back은 현재 클릭 기능을 연결하지 않습니다.
    """

    (
        back_column,
        progress_column,
        empty_column
    ) = st.columns(
        [1.15, 4.7, 1.15],
        vertical_alignment="center"
    )

    with back_column:
        render_html(
            """
            <div class="optimized-back-placeholder">
                ‹ Back
            </div>
            """
        )

    with progress_column:
        render_html(
            """
            <div class="optimized-progress">
                <div class="optimized-progress-dot completed">1</div>
                <div class="optimized-progress-line completed"></div>
                <div class="optimized-progress-dot completed">2</div>
                <div class="optimized-progress-line completed"></div>
                <div class="optimized-progress-dot completed">3</div>
                <div class="optimized-progress-line completed"></div>
                <div class="optimized-progress-dot completed">4</div>
                <div class="optimized-progress-line completed"></div>
                <div class="optimized-progress-dot completed">5</div>
                <div class="optimized-progress-line completed"></div>
                <div class="optimized-progress-dot completed">6</div>
                <div class="optimized-progress-line completed"></div>
                <div class="optimized-progress-dot active">7</div>
            </div>
            """
        )

    with empty_column:
        st.empty()


def show_before_after_images(
    before_image,
    after_image
):
    """
    원본과 보정 결과를 나란히 표시합니다.
    """

    before_uri = image_to_data_uri(
        before_image
    )

    after_uri = image_to_data_uri(
        after_image
    )

    render_html(
        f"""
        <div class="optimized-comparison">
            <div class="optimized-image-column">
                <div class="optimized-image-wrapper">
                    <img
                        class="optimized-image"
                        src="{before_uri}"
                        alt="Before optimization"
                    >
                </div>

                <div class="optimized-image-label">
                    Before
                </div>
            </div>

            <div class="optimized-arrow">
                →
            </div>

            <div class="optimized-image-column">
                <div class="optimized-image-wrapper">
                    <img
                        class="optimized-image"
                        src="{after_uri}"
                        alt="After optimization"
                    >
                </div>

                <div class="optimized-image-label after">
                    After
                </div>
            </div>
        </div>
        """
    )


def show_result_cards(
    improvements,
    before_score,
    after_score
):
    """
    Improvement Summary와 Match Score 카드를 표시합니다.
    """

    improvements_html = build_improvements_html(
        improvements
    )

    score_message = get_score_message(
        after_score
    )

    render_html(
        f"""
        <div class="optimized-result-grid">
            <div class="optimized-result-card">
                <div class="optimized-result-card-title">
                    Improvement Summary
                </div>

                <div class="optimized-improvement-list">
                    {improvements_html}
                </div>
            </div>

            <div class="optimized-result-card score-card">
                <div class="optimized-result-card-title">
                    Match Score
                </div>

                <div class="optimized-score">
                    <span>{before_score}%</span>
                    <strong>→</strong>
                    <span>{after_score}%</span>
                </div>

                <div class="optimized-score-message">
                    {score_message}
                </div>
            </div>
        </div>
        """
    )


def show_download_buttons(after_image):
    """
    일반 이미지와 원형 크롭 이미지 다운로드 버튼을 표시합니다.
    """

    normal_image_bytes = image_to_png_bytes(
        after_image
    )

    circle_image_bytes = (
        create_circle_crop_bytes(
            after_image
        )
    )

    download_column, circle_column = st.columns(
        2,
        gap="medium"
    )

    with download_column:
        st.download_button(
            label="Download",
            data=normal_image_bytes,
            file_name=(
                "personalab_optimized_image.png"
            ),
            mime="image/png",
            use_container_width=True,
            key="optimized_download_button"
        )

    with circle_column:
        st.download_button(
            label="Download (Circle Crop)",
            data=circle_image_bytes,
            file_name=(
                "personalab_circle_crop.png"
            ),
            mime="image/png",
            use_container_width=True,
            key="optimized_circle_download_button"
        )


def show_image_edit_result_page():
    """
    Step 7. 최종 Before / After 결과 페이지입니다.
    """

    show_progress_header()

    render_html(
        """
        <div class="optimized-page-header">
            <div class="optimized-page-title">
                Step 7. Your Optimized Image
            </div>

            <div class="optimized-page-description">
                Here is your optimized photo!
            </div>
        </div>
        """
    )

    before_image = get_before_image()
    after_image = get_after_image()

    if before_image is None:
        st.error(
            "The original selected photo could not be found."
        )

        return

    if after_image is None:
        st.warning(
            "The optimized image has not been saved yet. "
            "The original photo is displayed temporarily."
        )

        after_image = before_image.copy()

    show_before_after_images(
        before_image=before_image,
        after_image=after_image
    )

    render_html(
        '<div class="optimized-result-space"></div>'
    )

    improvements = get_improvement_summary()

    (
        before_score,
        after_score
    ) = get_match_scores()

    show_result_cards(
        improvements=improvements,
        before_score=before_score,
        after_score=after_score
    )

    render_html(
        '<div class="optimized-download-space"></div>'
    )

    show_download_buttons(
        after_image
    )