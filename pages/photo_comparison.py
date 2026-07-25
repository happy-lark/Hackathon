import base64
import html

from io import BytesIO
from textwrap import dedent

import streamlit as st
from PIL import Image

from utils.navigation import go_to_page


PERSONA_ATTRIBUTES = [
    "Professional",
    "Confident",
    "Approachable",
    "Creative"
]


ATTRIBUTE_ALIASES = {
    "Professional": [
        "professional"
    ],
    "Confident": [
        "confident",
        "confidence"
    ],
    "Approachable": [
        "approachable",
        "approachability"
    ],
    "Creative": [
        "creative",
        "creativity"
    ]
}


TARGET_WIDGET_KEYS = {
    "Professional": "target_professional_slider",
    "Confident": "target_confident_slider",
    "Approachable": "target_approachable_slider",
    "Creative": "target_creative_slider"
}


def clean_html(html_content):
    """
    Streamlit에서 HTML이 코드 블록으로 출력되지 않도록
    줄바꿈과 들여쓰기를 제거합니다.
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
    HTML을 Streamlit 화면에 출력합니다.
    """

    st.markdown(
        clean_html(html_content),
        unsafe_allow_html=True
    )


def clamp_score(value):
    """
    점수를 0~100 범위로 제한합니다.
    """

    try:
        numeric_value = float(value)

    except (TypeError, ValueError):
        return None

    # 분석값이 0~1 범위이면 퍼센트로 변환
    if 0 <= numeric_value <= 1:
        numeric_value *= 100

    return round(
        max(
            0,
            min(numeric_value, 100)
        ),
        2
    )


def extract_numeric_value(value):
    """
    숫자 또는 {"score": 80} 형태의 값을 숫자로 변환합니다.
    """

    if isinstance(value, dict):
        for key in [
            "score",
            "value",
            "percentage"
        ]:
            if key in value:
                return clamp_score(
                    value[key]
                )

        return None

    return clamp_score(value)


def normalize_persona_scores(raw_scores):
    """
    분석 결과의 다양한 키 형식을
    PersonaLab의 네 가지 Persona 점수로 변환합니다.
    """

    if not isinstance(raw_scores, dict):
        return None

    normalized_lookup = {
        str(key)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " "): value
        for key, value in raw_scores.items()
    }

    normalized_scores = {}

    for attribute in PERSONA_ATTRIBUTES:
        aliases = ATTRIBUTE_ALIASES[
            attribute
        ]

        score = None

        for alias in aliases:
            normalized_alias = (
                alias.lower()
                .replace("_", " ")
                .replace("-", " ")
            )

            if normalized_alias in normalized_lookup:
                score = extract_numeric_value(
                    normalized_lookup[
                        normalized_alias
                    ]
                )

                break

        if score is None:
            return None

        normalized_scores[
            attribute
        ] = score

    return normalized_scores


def get_target_persona():
    """
    Target 페이지에서 사용자가 선택한 Persona 값을 가져옵니다.
    """

    possible_keys = [
        "target_persona",
        "target_persona_scores",
        "target_scores",
        "persona_target"
    ]

    for session_key in possible_keys:
        raw_target = st.session_state.get(
            session_key
        )

        normalized_target = (
            normalize_persona_scores(
                raw_target
            )
        )

        if normalized_target:
            return normalized_target

    # Target slider의 widget key에서 직접 가져오기
    widget_target = {}

    for attribute, widget_key in (
        TARGET_WIDGET_KEYS.items()
    ):
        value = st.session_state.get(
            widget_key
        )

        if value is None:
            return None

        widget_target[
            attribute
        ] = value

    return normalize_persona_scores(
        widget_target
    )


def get_individual_results():
    """
    analyzer.py가 반환한 사진별 분석 결과를 가져옵니다.
    """

    analysis_result = st.session_state.get(
        "analysis_result",
        {}
    )

    if not isinstance(
        analysis_result,
        dict
    ):
        return []

    possible_keys = [
        "individual_results",
        "photo_results",
        "results",
        "images"
    ]

    for key in possible_keys:
        results = analysis_result.get(
            key
        )

        if isinstance(results, list):
            return results

    return []


def extract_photo_scores(photo_result):
    """
    사진 한 장의 Persona 점수를 추출합니다.
    """

    if not isinstance(
        photo_result,
        dict
    ):
        return None

    possible_score_keys = [
        "persona_scores",
        "scores",
        "detected_persona",
        "persona",
        "traits",
        "attributes"
    ]

    for key in possible_score_keys:
        raw_scores = photo_result.get(
            key
        )

        normalized_scores = (
            normalize_persona_scores(
                raw_scores
            )
        )

        if normalized_scores:
            return normalized_scores

    # 점수가 photo_result 최상단에 있는 경우
    return normalize_persona_scores(
        photo_result
    )


def calculate_match_score(
    photo_scores,
    target_scores
):
    """
    사진과 Target Persona의 가중 평균 차이로
    Match Score를 계산합니다.

    Target 값이 높을수록 해당 항목의 비중도 커집니다.
    """

    target_total = sum(
        target_scores.values()
    )

    if target_total <= 0:
        weights = {
            attribute: 1 / len(
                PERSONA_ATTRIBUTES
            )
            for attribute in PERSONA_ATTRIBUTES
        }

    else:
        weights = {
            attribute: (
                target_scores[attribute]
                / target_total
            )
            for attribute in PERSONA_ATTRIBUTES
        }

    weighted_difference = sum(
        weights[attribute]
        * abs(
            photo_scores[attribute]
            - target_scores[attribute]
        )
        for attribute in PERSONA_ATTRIBUTES
    )

    match_score = (
        100
        - weighted_difference
    )

    return round(
        max(
            0,
            min(match_score, 100)
        )
    )


def get_existing_feedback(photo_result):
    """
    analyzer.py에 이미 사진별 피드백이 있다면 가져옵니다.
    """

    if not isinstance(
        photo_result,
        dict
    ):
        return []

    possible_keys = [
        "feedback",
        "strengths",
        "recommendations",
        "messages"
    ]

    for key in possible_keys:
        feedback = photo_result.get(
            key
        )

        if isinstance(feedback, list):
            return [
                str(item)
                for item in feedback
                if item
            ][:4]

        if isinstance(feedback, str):
            return [feedback]

    return []


def create_alignment_feedback(
    photo_scores,
    target_scores
):
    """
    Target Persona와의 차이를 기반으로 피드백을 생성합니다.
    """

    differences = {
        attribute: abs(
            photo_scores[attribute]
            - target_scores[attribute]
        )
        for attribute in PERSONA_ATTRIBUTES
    }

    closest_attributes = sorted(
        PERSONA_ATTRIBUTES,
        key=lambda attribute: (
            differences[attribute]
        )
    )

    largest_gap_attribute = max(
        PERSONA_ATTRIBUTES,
        key=lambda attribute: (
            differences[attribute]
        )
    )

    feedback = []

    for attribute in closest_attributes[:2]:
        feedback.append(
            f"{attribute} closely matches "
            f"your target persona"
        )

    largest_gap = differences[
        largest_gap_attribute
    ]

    photo_value = photo_scores[
        largest_gap_attribute
    ]

    target_value = target_scores[
        largest_gap_attribute
    ]

    if largest_gap <= 10:
        feedback.append(
            "Strong overall balance across "
            "your selected persona"
        )

    elif photo_value < target_value:
        feedback.append(
            f"{largest_gap_attribute} could "
            f"be strengthened slightly"
        )

    else:
        feedback.append(
            f"{largest_gap_attribute} appears "
            f"stronger than your selected target"
        )

    feedback.append(
        "Good potential for further optimization"
    )

    return feedback[:4]


def image_to_data_uri(image):
    """
    PIL 이미지를 HTML에서 사용할 수 있는
    Base64 이미지 URI로 변환합니다.
    """

    if not isinstance(image, Image.Image):
        return ""

    buffer = BytesIO()

    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=90
    )

    encoded_image = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return (
        "data:image/jpeg;base64,"
        f"{encoded_image}"
    )


def build_photo_ranking():
    """
    업로드된 모든 사진을 Target Persona와 비교하여
    Match Score가 높은 순으로 정렬합니다.
    """

    uploaded_images = st.session_state.get(
        "uploaded_images",
        []
    )

    uploaded_filenames = st.session_state.get(
        "uploaded_filenames",
        []
    )

    target_scores = get_target_persona()
    individual_results = (
        get_individual_results()
    )

    if not target_scores:
        return {
            "success": False,
            "message": (
                "Target Persona values were not found. "
                "Please return to the Target page."
            )
        }

    if not uploaded_images:
        return {
            "success": False,
            "message": (
                "Uploaded photos were not found."
            )
        }

    if not individual_results:
        return {
            "success": False,
            "message": (
                "Individual photo analysis results "
                "were not found."
            )
        }

    ranking = []

    for fallback_index, photo_result in enumerate(
        individual_results
    ):
        if not isinstance(
            photo_result,
            dict
        ):
            continue

        if photo_result.get(
            "success"
        ) is False:
            continue

        photo_scores = extract_photo_scores(
            photo_result
        )

        if not photo_scores:
            continue

        image_index = photo_result.get(
            "image_index",
            fallback_index
        )

        try:
            image_index = int(
                image_index
            )

        except (TypeError, ValueError):
            image_index = fallback_index

        if not (
            0
            <= image_index
            < len(uploaded_images)
        ):
            continue

        match_score = calculate_match_score(
            photo_scores=photo_scores,
            target_scores=target_scores
        )

        existing_feedback = (
            get_existing_feedback(
                photo_result
            )
        )

        feedback = (
            existing_feedback
            or create_alignment_feedback(
                photo_scores=photo_scores,
                target_scores=target_scores
            )
        )

        if image_index < len(
            uploaded_filenames
        ):
            filename = (
                uploaded_filenames[
                    image_index
                ]
            )

        else:
            filename = (
                f"Photo {image_index + 1}"
            )

        ranking.append(
            {
                "image_index": image_index,
                "photo_number": (
                    image_index + 1
                ),
                "filename": filename,
                "scores": photo_scores,
                "match_score": match_score,
                "feedback": feedback
            }
        )

    if not ranking:
        return {
            "success": False,
            "message": (
                "Persona scores could not be found "
                "in the individual analysis results."
            )
        }

    ranking.sort(
        key=lambda item: (
            item["match_score"]
        ),
        reverse=True
    )

    for rank_number, item in enumerate(
        ranking,
        start=1
    ):
        item["rank"] = rank_number

    return {
        "success": True,
        "ranking": ranking,
        "target_scores": target_scores
    }


def show_progress_header():
    """
    Back 버튼과 Step 5 진행 상태를 표시합니다.
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
        if st.button(
            "‹ Back",
            key="comparison_top_back"
        ):
            go_to_page("ai_analysis")

    with progress_column:
        render_html(
            """
            <div class="comparison-progress">
                <div class="comparison-progress-dot completed">1</div>
                <div class="comparison-progress-line completed"></div>
                <div class="comparison-progress-dot completed">2</div>
                <div class="comparison-progress-line completed"></div>
                <div class="comparison-progress-dot completed">3</div>
                <div class="comparison-progress-line completed"></div>
                <div class="comparison-progress-dot completed">4</div>
                <div class="comparison-progress-line completed"></div>
                <div class="comparison-progress-dot active">5</div>
            </div>
            """
        )

    with empty_column:
        st.empty()


def show_best_photo_card(
    best_photo,
    uploaded_images
):
    """
    1위 사진을 크게 표시합니다.
    """

    image_index = best_photo[
        "image_index"
    ]

    image_uri = image_to_data_uri(
        uploaded_images[
            image_index
        ]
    )

    escaped_filename = html.escape(
        str(
            best_photo["filename"]
        )
    )

    feedback_html = "".join(
        f"""
        <div class="comparison-feedback-item">
            <span>✓</span>
            <div>{html.escape(str(item))}</div>
        </div>
        """
        for item in best_photo[
            "feedback"
        ]
    )

    render_html(
        f"""
        <div class="comparison-best-card">
            <div class="comparison-best-rank">
                1
            </div>

            <div class="comparison-best-image-wrapper">
                <img
                    class="comparison-best-image"
                    src="{image_uri}"
                    alt="{escaped_filename}"
                >
            </div>

            <div class="comparison-best-content">
                <div class="comparison-photo-title">
                    Photo {best_photo["photo_number"]}
                </div>

                <div class="comparison-photo-filename">
                    {escaped_filename}
                </div>

                <div class="comparison-feedback-list">
                    {feedback_html}
                </div>
            </div>

            <div class="comparison-best-score">
                <div class="comparison-score-number">
                    {best_photo["match_score"]}%
                </div>

                <div class="comparison-score-label">
                    Match
                </div>
            </div>
        </div>
        """
    )


def show_ranked_photo_row(
    photo,
    uploaded_images
):
    """
    2위 이하의 사진을 한 줄 카드로 표시합니다.
    """

    image_index = photo[
        "image_index"
    ]

    image_uri = image_to_data_uri(
        uploaded_images[
            image_index
        ]
    )

    escaped_filename = html.escape(
        str(
            photo["filename"]
        )
    )

    render_html(
        f"""
        <div class="comparison-ranked-card">
            <div class="comparison-rank-number">
                {photo["rank"]}
            </div>

            <img
                class="comparison-ranked-image"
                src="{image_uri}"
                alt="{escaped_filename}"
            >

            <div class="comparison-ranked-info">
                <div class="comparison-ranked-title">
                    Photo {photo["photo_number"]}
                </div>

                <div class="comparison-ranked-filename">
                    {escaped_filename}
                </div>
            </div>

            <div class="comparison-ranked-score">
                {photo["match_score"]}% Match
            </div>
        </div>
        """
    )


def save_ranking_to_session(ranking):
    """
    Ranking 결과와 추천 사진 번호를 session_state에 저장합니다.
    """

    st.session_state[
        "photo_ranking"
    ] = [
        {
            "rank": item["rank"],
            "image_index": item[
                "image_index"
            ],
            "photo_number": item[
                "photo_number"
            ],
            "filename": item[
                "filename"
            ],
            "match_score": item[
                "match_score"
            ],
            "scores": item[
                "scores"
            ],
            "feedback": item[
                "feedback"
            ]
        }
        for item in ranking
    ]

    best_photo = ranking[0]

    st.session_state[
        "best_photo_index"
    ] = best_photo[
        "image_index"
    ]

    st.session_state[
        "selected_photo_index"
    ] = best_photo[
        "image_index"
    ]

    st.session_state[
        "best_match_score"
    ] = best_photo[
        "match_score"
    ]


def show_photo_comparison_page():
    """
    Step 5. Photo Comparison 페이지입니다.
    """

    show_progress_header()

    render_html(
        """
        <div class="comparison-page-header">
            <div class="comparison-page-title">
                Step 5. Photo Comparison
            </div>

            <div class="comparison-page-description">
                We found the best match for your target persona.
            </div>
        </div>
        """
    )

    ranking_result = (
        build_photo_ranking()
    )

    if not ranking_result[
        "success"
    ]:
        st.error(
            ranking_result[
                "message"
            ]
        )

        back_column, retry_column = (
            st.columns(2)
        )

        with back_column:
            if st.button(
                "Back to Upload",
                use_container_width=True,
                key="comparison_error_back"
            ):
                go_to_page("upload")

        with retry_column:
            if st.button(
                "Run Analysis Again",
                type="primary",
                use_container_width=True,
                key="comparison_error_retry"
            ):
                st.session_state.pop(
                    "analysis_result",
                    None
                )

                st.session_state.pop(
                    "analysis_status",
                    None
                )

                go_to_page(
                    "ai_analysis"
                )

        return

    ranking = ranking_result[
        "ranking"
    ]

    uploaded_images = (
        st.session_state.get(
            "uploaded_images",
            []
        )
    )

    save_ranking_to_session(
        ranking
    )

    show_best_photo_card(
        best_photo=ranking[0],
        uploaded_images=uploaded_images
    )

    for photo in ranking[1:]:
        show_ranked_photo_row(
            photo=photo,
            uploaded_images=uploaded_images
        )

    render_html(
        '<div class="comparison-button-space"></div>'
    )

    if st.button(
        "Continue to Report",
        type="primary",
        use_container_width=True,
        key="comparison_continue_button"
    ):
        go_to_page("match_report")