"""
pages/upload.py

Step 3. Upload Your Photos

사용자가 최대 5장의 사진을 업로드하고
분석에 사용할 사진을 미리 확인하는 페이지입니다.
"""

from textwrap import dedent

import streamlit as st
from PIL import Image, ImageOps

from utils.navigation import go_to_page


TOTAL_STEPS = 7
CURRENT_STEP = 3
MAX_IMAGES = 5


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
            <span class="upload-progress-dot {state_class}">
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
                <span class="upload-progress-line {line_class}">
                </span>
                """
            )

    return "".join(
        progress_parts
    )


def get_file_key(uploaded_file):
    """
    업로드된 파일을 구분하기 위한 키를 반환합니다.
    """

    return (
        uploaded_file.name,
        uploaded_file.size
    )


def create_upload_signature(uploaded_files):
    """
    현재 file_uploader의 파일 목록을 나타내는
    signature를 생성합니다.
    """

    if not uploaded_files:
        return None

    return tuple(
        get_file_key(uploaded_file)
        for uploaded_file in uploaded_files
    )


def load_uploaded_images(uploaded_files):
    """
    Streamlit UploadedFile 목록을 PIL 이미지로 변환합니다.

    정상적으로 열린 이미지와 파일 정보만 반환합니다.
    """

    images = []
    filenames = []
    file_keys = []
    errors = []

    for index, uploaded_file in enumerate(
        uploaded_files
    ):
        try:
            uploaded_file.seek(0)

            image = Image.open(
                uploaded_file
            )

            image = (
                ImageOps.exif_transpose(
                    image
                )
                .convert("RGB")
            )

            images.append(
                image
            )

            filenames.append(
                uploaded_file.name
            )

            file_keys.append(
                get_file_key(
                    uploaded_file
                )
            )

        except Exception:
            errors.append(
                {
                    "index": index + 1,
                    "filename": uploaded_file.name
                }
            )

    return (
        images,
        filenames,
        file_keys,
        errors
    )


def clear_analysis_results():
    """
    업로드 사진이 변경된 경우 기존 분석 결과를 제거합니다.
    """

    keys_to_remove = [
        "analysis_result",
        "analysis_status",
        "analysis_error_result",
        "color_analysis_result",
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
        "image_edit_result",
        "photo_editor_preview_result",
        "improvement_summary",
        "improvement_report"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
        )


def clear_uploaded_images():
    """
    저장된 업로드 이미지와 관련 정보를 제거합니다.
    """

    keys_to_remove = [
        "uploaded_images",
        "uploaded_filenames",
        "uploaded_file_signature"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
        )

    clear_analysis_results()


def show_progress_header():
    """
    Back 버튼과 1~7단계 진행 상태를 표시합니다.

    현재 Upload 페이지는 Step 3입니다.
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
            key="upload_top_back"
        ):
            go_to_page(
                "context"
            )

    with progress_column:
        render_html(
            f"""
            <div class="upload-progress">
                {build_progress_html()}
            </div>
            """
        )

    with empty_column:
        st.empty()


def remove_uploaded_photo(file_key):
    """
    선택한 사진을 미리보기와 분석 대상에서 제외합니다.
    """

    removed_file_keys = list(
        st.session_state.get(
            "removed_upload_file_keys",
            []
        )
    )

    if file_key not in removed_file_keys:
        removed_file_keys.append(
            file_key
        )

    st.session_state[
        "removed_upload_file_keys"
    ] = removed_file_keys

    clear_analysis_results()

    st.rerun()


def show_image_previews(
    images,
    file_keys
):
    """
    업로드된 사진을 최대 5열로 표시합니다.

    사진이 없는 자리에는 빈 미리보기 카드가 표시됩니다.
    """

    columns = st.columns(
        MAX_IMAGES,
        gap="small"
    )

    for index in range(
        MAX_IMAGES
    ):
        with columns[index]:
            if index < len(images):
                (
                    empty_column,
                    remove_column
                ) = st.columns(
                    [4, 1],
                    gap="small"
                )

                with empty_column:
                    st.empty()

                with remove_column:
                    remove_clicked = st.button(
                        "×",
                        key=(
                            "remove_uploaded_photo_"
                            f"{index}"
                        ),
                        help="Remove photo"
                    )

                if remove_clicked:
                    remove_uploaded_photo(
                        file_keys[index]
                    )

                st.image(
                    images[index],
                    use_container_width=True
                )

            else:
                render_html(
                    """
                    <div class="upload-empty-photo">
                        <span>＋</span>
                    </div>
                    """
                )


def show_upload_tips():
    """
    더 좋은 분석 결과를 위한 사진 안내를 표시합니다.
    """

    render_html(
        """
        <div class="upload-tips-card">
            <div class="upload-tips-title">
                Tips for better results
            </div>

            <div class="upload-tip-item">
                <span>✓</span>
                <div>
                    Use clear, well-lit photos
                </div>
            </div>

            <div class="upload-tip-item">
                <span>✓</span>
                <div>
                    Make sure your face is clearly visible
                </div>
            </div>

            <div class="upload-tip-item">
                <span>✓</span>
                <div>
                    Avoid group photos or heavy filters
                </div>
            </div>
        </div>
        """
    )


def show_image_errors(image_errors):
    """
    열 수 없는 이미지가 있을 경우 오류 메시지를 표시합니다.
    """

    for error in image_errors:
        st.error(
            f'Photo {error["index"]} '
            f'({error["filename"]}) '
            "could not be opened."
        )


def save_uploaded_images(
    images,
    filenames,
    active_file_keys
):
    """
    정상적으로 불러온 업로드 이미지를 session_state에 저장합니다.
    """

    st.session_state[
        "uploaded_images"
    ] = images

    st.session_state[
        "uploaded_filenames"
    ] = filenames

    st.session_state[
        "uploaded_file_signature"
    ] = tuple(
        active_file_keys
    )


def show_upload_page():
    """
    Step 3. 사진 업로드 페이지입니다.
    """

    _, content_column, _ = st.columns(
        [0.45, 5.1, 0.45]
    )

    with content_column:
        show_progress_header()

        render_html(
            """
            <div class="upload-page-header">
                <div class="upload-page-title">
                    Step 3. Upload Your Photos
                </div>

                <div class="upload-page-description">
                    Add up to 5 photos with your face clearly visible.
                </div>
            </div>
            """
        )

        uploader_version = st.session_state.get(
            "uploader_version",
            0
        )

        uploaded_files = st.file_uploader(
            "Upload your photos",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=(
                f"photo_uploader_"
                f"{uploader_version}"
            )
        )

        current_widget_signature = (
            create_upload_signature(
                uploaded_files
            )
        )

        previous_widget_signature = (
            st.session_state.get(
                "upload_widget_signature"
            )
        )

        # file_uploader의 파일 목록 자체가 변경된 경우
        if (
            current_widget_signature
            != previous_widget_signature
        ):
            st.session_state[
                "upload_widget_signature"
            ] = current_widget_signature

            st.session_state[
                "removed_upload_file_keys"
            ] = []

            clear_analysis_results()

        removed_file_keys = (
            st.session_state.get(
                "removed_upload_file_keys",
                []
            )
        )

        active_files = [
            uploaded_file
            for uploaded_file in (
                uploaded_files
                or []
            )
            if get_file_key(
                uploaded_file
            ) not in removed_file_keys
        ]

        too_many_images = (
            len(active_files)
            > MAX_IMAGES
        )

        if too_many_images:
            st.error(
                "You can upload up to 5 photos. "
                "Please remove extra files."
            )

        # 5장을 초과한 경우에도 앞의 5장은
        # 미리보기로 표시합니다.
        preview_files = active_files[
            :MAX_IMAGES
        ]

        if preview_files:
            (
                images,
                filenames,
                active_file_keys,
                image_errors
            ) = load_uploaded_images(
                preview_files
            )

            if image_errors:
                show_image_errors(
                    image_errors
                )

            if not too_many_images:
                save_uploaded_images(
                    images=images,
                    filenames=filenames,
                    active_file_keys=active_file_keys
                )

            else:
                clear_uploaded_images()

        else:
            images = []
            filenames = []
            active_file_keys = []

            clear_uploaded_images()

        render_html(
            '<div class="upload-preview-space"></div>'
        )

        show_image_previews(
            images=images,
            file_keys=active_file_keys
        )

        show_upload_tips()

        render_html(
            '<div class="upload-continue-space"></div>'
        )

        continue_disabled = (
            not images
            or too_many_images
        )

        continue_clicked = st.button(
            "Continue",
            type="primary",
            use_container_width=True,
            disabled=continue_disabled,
            key="upload_continue_button"
        )

        if continue_clicked:
            clear_analysis_results()

            go_to_page(
                "ai_analysis"
            )