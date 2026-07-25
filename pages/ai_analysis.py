"""
pages/ai_analysis.py

Step 4. AI Analysis

업로드된 사진을 분석하고,
분석 진행 상태 및 완료 화면을 표시합니다.
"""

import base64
import time

from pathlib import Path
from textwrap import dedent

import streamlit as st

from analysis.analyzer import (
    analyze_multiple_face_personas
)
from utils.navigation import go_to_page


TOTAL_STEPS = 7
CURRENT_STEP = 4


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


MASCOT_PATH = (
    PROJECT_ROOT
    / "assets"
    / "loading_img_cutout.png"
)


ANALYSIS_STEPS = [
    "Detecting facial visibility",
    "Analyzing expression",
    "Checking lighting and color",
    "Reviewing composition",
    "Evaluating background",
    "Comparing with your target persona"
]


ANALYSIS_TIPS = [
    "Use clear, well-lit photos",
    "Make sure your face is clearly visible",
    "Avoid group photos or heavy filters"
]


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
    HTML을 현재 Streamlit 위치에 렌더링합니다.
    """

    st.markdown(
        clean_html(
            html_content
        ),
        unsafe_allow_html=True
    )


def render_placeholder_html(
    placeholder,
    html_content
):
    """
    HTML을 지정한 placeholder 내부에 렌더링합니다.
    """

    placeholder.markdown(
        clean_html(
            html_content
        ),
        unsafe_allow_html=True
    )


def build_progress_html():
    """
    현재 단계에 맞춰 1~7단계 진행 표시 HTML을 생성합니다.
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
            <span class="analysis-top-dot {state_class}">
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
                <span class="analysis-top-line {line_class}">
                </span>
                """
            )

    return "".join(
        progress_parts
    )


def reset_analysis_state():
    """
    기존 분석 상태와 사진 순위 결과를 초기화합니다.
    """

    keys_to_remove = [
        "analysis_result",
        "analysis_status",
        "analysis_error_result",
        "photo_ranking",
        "best_photo_index",
        "selected_photo_index",
        "best_match_score",
        "selected_photo_match_score",
        "selected_photo_alignment",
        "selected_photo_quality",
        "match_report_strengths",
        "match_report_improvements",
        "match_report_color_result",
        "match_report_color_index",
        "optimized_image",
        "edited_image",
        "photo_editor_preview_result"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
        )


def get_image_mime_type(image_path):
    """
    이미지 확장자에 맞는 MIME type을 반환합니다.
    """

    suffix = image_path.suffix.lower()

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }

    return mime_types.get(
        suffix,
        "image/png"
    )


def get_mascot_html():
    """
    마스코트 이미지를 HTML에서 사용할 수 있도록
    Base64 문자열로 변환합니다.
    """

    if not MASCOT_PATH.exists():
        return """
        <div class="analysis-robot-fallback">
            🤖
        </div>
        """

    encoded_image = base64.b64encode(
        MASCOT_PATH.read_bytes()
    ).decode(
        "utf-8"
    )

    mime_type = get_image_mime_type(
        MASCOT_PATH
    )

    return f"""
    <img
        class="analysis-mascot-image"
        src="data:{mime_type};base64,{encoded_image}"
        alt="PersonaLab analysis robot"
    >
    """


def show_progress_header():
    """
    Back 버튼과 상단 1~7단계 진행 상태를 표시합니다.
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
            key="analysis_top_back"
        ):
            go_to_page(
                "upload"
            )

    with progress_column:
        render_html(
            f"""
            <div class="analysis-top-progress">
                {build_progress_html()}
            </div>
            """
        )

    with empty_column:
        st.empty()


def build_analysis_visual_html(
    progress,
    finished=False
):
    """
    원형 진행률과 마스코트 HTML을 생성합니다.
    """

    progress = max(
        0,
        min(
            progress,
            100
        )
    )

    progress_angle = (
        progress
        * 3.6
    )

    mascot_html = (
        get_mascot_html()
    )

    if finished:
        status_text = (
            "Analysis Complete"
        )

        status_class = (
            "finished"
        )

    else:
        status_text = (
            f"Analyzing... {progress}%"
        )

        status_class = ""

    return f"""
    <div class="analysis-visual-wrapper">
        <div
            class="analysis-progress-ring"
            style="
                --progress-angle:
                {progress_angle}deg;
            "
        >
            <div class="analysis-progress-inner">
                {mascot_html}
            </div>
        </div>

        <div class="analysis-progress-text {status_class}">
            {status_text}
        </div>
    </div>
    """


def render_analysis_visual(
    placeholder,
    progress,
    finished=False
):
    """
    원형 진행률을 placeholder에 렌더링합니다.
    """

    visual_html = (
        build_analysis_visual_html(
            progress=progress,
            finished=finished
        )
    )

    render_placeholder_html(
        placeholder=placeholder,
        html_content=visual_html
    )


def build_analysis_steps_html(
    active_step,
    all_completed=False
):
    """
    분석 체크리스트 HTML을 생성합니다.
    """

    step_html = []

    for index, step_name in enumerate(
        ANALYSIS_STEPS
    ):
        if all_completed:
            status_class = "completed"
            icon = "✓"

        elif index < active_step:
            status_class = "completed"
            icon = "✓"

        elif index == active_step:
            status_class = "active"
            icon = ""

        else:
            status_class = "pending"
            icon = ""

        step_html.append(
            f"""
            <div class="analysis-step-item {status_class}">
                <div class="analysis-step-icon">
                    {icon}
                </div>

                <div class="analysis-step-label">
                    {step_name}
                </div>
            </div>
            """
        )

    return f"""
    <div class="analysis-step-list">
        {''.join(step_html)}
    </div>
    """


def render_analysis_steps(
    placeholder,
    active_step,
    all_completed=False
):
    """
    분석 체크리스트를 placeholder에 렌더링합니다.
    """

    steps_html = (
        build_analysis_steps_html(
            active_step=active_step,
            all_completed=all_completed
        )
    )

    render_placeholder_html(
        placeholder=placeholder,
        html_content=steps_html
    )


def update_analysis_screen(
    visual_placeholder,
    steps_placeholder,
    progress,
    active_step
):
    """
    원형 진행률과 체크리스트를 함께 갱신합니다.
    """

    render_analysis_visual(
        placeholder=visual_placeholder,
        progress=progress
    )

    render_analysis_steps(
        placeholder=steps_placeholder,
        active_step=active_step
    )

def show_analysis_finished():
    """
    분석 완료 안내와 Photo Comparison 이동 버튼을 표시합니다.
    """

    render_html(
        """
        <div class="analysis-finished-card">
            <div class="analysis-finished-icon">
                ✓
            </div>

            <div class="analysis-finished-content">
                <div class="analysis-finished-title">
                    Analysis Finished!
                </div>

                <div class="analysis-finished-description">
                    Your photos have been successfully analyzed.
                    Continue to see which photo best matches
                    your target persona.
                </div>
            </div>
        </div>
        """
    )

    render_html(
        """
        <div class="analysis-finished-button-space">
        </div>
        """
    )

    if st.button(
        "View Photo Ranking",
        type="primary",
        use_container_width=True,
        key="analysis_continue_button"
    ):
        go_to_page(
            "photo_comparison"
        )


def show_analysis_error(
    analysis_result
):
    """
    분석 실패 메시지와 재시도 버튼을 표시합니다.
    """

    error_message = (
        analysis_result.get(
            "message",
            "The photos could not be analyzed."
        )
    )

    st.error(
        error_message
    )

    individual_results = (
        analysis_result.get(
            "individual_results",
            []
        )
    )

    for item in individual_results:
        if item.get(
            "success",
            False
        ):
            continue

        image_index = (
            item.get(
                "image_index",
                0
            )
            + 1
        )

        message = item.get(
            "message",
            "The face could not be detected."
        )

        st.warning(
            f"Photo {image_index}: "
            f"{message}"
        )

    retry_column, back_column = (
        st.columns(
            2
        )
    )

    with retry_column:
        if st.button(
            "Try Again",
            type="primary",
            use_container_width=True,
            key="analysis_retry_button"
        ):
            reset_analysis_state()

            st.rerun()

    with back_column:
        if st.button(
            "Back to Upload",
            use_container_width=True,
            key="analysis_back_upload_button"
        ):
            reset_analysis_state()

            go_to_page(
                "upload"
            )


def run_analysis(images):
    """
    업로드된 사진을 분석하고 결과를 저장합니다.

    성공하면 True, 실패하면 False를 반환합니다.
    """

    st.session_state[
        "analysis_status"
    ] = "running"

    visual_placeholder = (
        st.empty()
    )

    steps_placeholder = (
        st.empty()
    )

    update_analysis_screen(
        visual_placeholder=visual_placeholder,
        steps_placeholder=steps_placeholder,
        progress=12,
        active_step=0
    )

    time.sleep(
        0.3
    )

    update_analysis_screen(
        visual_placeholder=visual_placeholder,
        steps_placeholder=steps_placeholder,
        progress=28,
        active_step=1
    )

    time.sleep(
        0.3
    )

    update_analysis_screen(
        visual_placeholder=visual_placeholder,
        steps_placeholder=steps_placeholder,
        progress=45,
        active_step=2
    )

    time.sleep(
        0.25
    )

    try:
        analysis_result = (
            analyze_multiple_face_personas(
                images
            )
        )

    except Exception as error:
        analysis_result = {
            "success": False,
            "message": (
                "An unexpected error occurred "
                f"during analysis: {error}"
            )
        }

    update_analysis_screen(
        visual_placeholder=visual_placeholder,
        steps_placeholder=steps_placeholder,
        progress=70,
        active_step=3
    )

    time.sleep(
        0.3
    )

    update_analysis_screen(
        visual_placeholder=visual_placeholder,
        steps_placeholder=steps_placeholder,
        progress=84,
        active_step=4
    )

    time.sleep(
        0.3
    )

    update_analysis_screen(
        visual_placeholder=visual_placeholder,
        steps_placeholder=steps_placeholder,
        progress=95,
        active_step=5
    )

    time.sleep(
        0.3
    )

    if not analysis_result.get(
        "success",
        False
    ):
        st.session_state[
            "analysis_status"
        ] = "error"

        st.session_state[
            "analysis_error_result"
        ] = analysis_result

        render_analysis_visual(
            placeholder=visual_placeholder,
            progress=100
        )

        render_analysis_steps(
            placeholder=steps_placeholder,
            active_step=5
        )

        return False

    st.session_state[
        "analysis_result"
    ] = analysis_result

    st.session_state[
        "analysis_status"
    ] = "finished"

    st.session_state.pop(
        "analysis_error_result",
        None
    )

    ranking_keys = [
        "photo_ranking",
        "best_photo_index",
        "selected_photo_index",
        "best_match_score",
        "selected_photo_match_score",
        "selected_photo_alignment",
        "selected_photo_quality",
        "match_report_strengths",
        "match_report_improvements",
        "match_report_color_result",
        "match_report_color_index"
    ]

    for key in ranking_keys:
        st.session_state.pop(
            key,
            None
        )

    render_analysis_visual(
        placeholder=visual_placeholder,
        progress=100,
        finished=True
    )

    render_analysis_steps(
        placeholder=steps_placeholder,
        active_step=len(
            ANALYSIS_STEPS
        ),
        all_completed=True
    )

    return True


def show_completed_analysis():
    """
    이미 분석이 완료된 상태에서 페이지가 다시 실행되면
    분석을 반복하지 않고 완료 화면을 유지합니다.
    """

    visual_placeholder = (
        st.empty()
    )

    steps_placeholder = (
        st.empty()
    )

    render_analysis_visual(
        placeholder=visual_placeholder,
        progress=100,
        finished=True
    )

    render_analysis_steps(
        placeholder=steps_placeholder,
        active_step=len(
            ANALYSIS_STEPS
        ),
        all_completed=True
    )

    show_analysis_finished()


def show_ai_analysis_page():
    """
    Step 4. AI Analysis 페이지를 표시합니다.
    """

    _, content_column, _ = st.columns(
        [0.45, 5.1, 0.45]
    )

    with content_column:
        show_progress_header()

        render_html(
            """
            <div class="analysis-page-header">
                <div class="analysis-page-title">
                    Step 4. AI is Analyzing Your Photos
                </div>

                <div class="analysis-page-description">
                    This may take a few moments.
                </div>
            </div>
            """
        )

        images = st.session_state.get(
            "uploaded_images",
            []
        )

        if not images:
            st.error(
                "No uploaded photos were found. "
                "Please upload at least one photo."
            )

            if st.button(
                "Back to Upload",
                type="primary",
                use_container_width=True,
                key="analysis_no_images_back"
            ):
                reset_analysis_state()

                go_to_page(
                    "upload"
                )

            return

        render_html(
            """
            <div class="analysis-content-space">
            </div>
            """
        )

        analysis_status = (
            st.session_state.get(
                "analysis_status",
                "idle"
            )
        )

        if (
            analysis_status == "finished"
            and st.session_state.get(
                "analysis_result"
            )
        ):
            show_completed_analysis()

        elif analysis_status == "error":
            analysis_error_result = (
                st.session_state.get(
                    "analysis_error_result",
                    {
                        "success": False,
                        "message": (
                            "The photos could not be analyzed."
                        )
                    }
                )
            )

            show_analysis_error(
                analysis_error_result
            )

        else:
            analysis_success = (
                run_analysis(
                    images
                )
            )

            if analysis_success:
                show_analysis_finished()

            else:
                analysis_error_result = (
                    st.session_state.get(
                        "analysis_error_result",
                        {
                            "success": False,
                            "message": (
                                "The photos could not be analyzed."
                            )
                        }
                    )
                )

                show_analysis_error(
                    analysis_error_result
                )