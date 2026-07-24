import streamlit as st

from PIL import Image
from textwrap import dedent

from analysis.analyzer import (
    analyze_multiple_face_personas
)
from utils.navigation import go_to_page


MAX_IMAGES = 5


def render_html(html):
    """
    여러 줄 HTML의 들여쓰기를 제거한 후 출력합니다.

    들여쓰기된 HTML이 Markdown 코드 블록으로
    표시되는 문제를 방지합니다.
    """

    cleaned_html = dedent(html).strip()

    st.markdown(
        cleaned_html,
        unsafe_allow_html=True
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

    정상적으로 열린 이미지와 해당 파일 정보만 반환합니다.
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
            ).convert("RGB")

            images.append(image)
            filenames.append(
                uploaded_file.name
            )
            file_keys.append(
                get_file_key(uploaded_file)
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


def clear_upload_results():
    """
    업로드 사진과 관련된 기존 분석 결과를 제거합니다.
    """

    keys_to_remove = [
        "uploaded_images",
        "uploaded_filenames",
        "uploaded_file_signature",
        "analysis_result",
        "color_analysis_result",
        "image_edit_result"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
        )


def show_progress_header():
    """
    Back 버튼과 5단계 진행 상태를 표시합니다.

    현재 Upload 페이지는 Step 3입니다.
    """

    back_column, progress_column, empty_column = (
        st.columns(
            [1.15, 4.7, 1.15],
            vertical_alignment="center"
        )
    )

    with back_column:
        if st.button(
            "‹ Back",
            key="upload_top_back"
        ):
            go_to_page("target")

    with progress_column:
        render_html(
            """
            <div class="upload-progress">
                <div class="upload-progress-dot completed">1</div>
                <div class="upload-progress-line completed"></div>
                <div class="upload-progress-dot completed">2</div>
                <div class="upload-progress-line completed"></div>
                <div class="upload-progress-dot active">3</div>
                <div class="upload-progress-line"></div>
                <div class="upload-progress-dot">4</div>
                <div class="upload-progress-line"></div>
                <div class="upload-progress-dot">5</div>
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

    st.session_state.pop(
        "analysis_result",
        None
    )

    st.session_state.pop(
        "color_analysis_result",
        None
    )

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

    for index in range(MAX_IMAGES):
        with columns[index]:
            if index < len(images):
                _, remove_column = st.columns(
                    [4, 1],
                    gap="small"
                )

                with remove_column:
                    remove_clicked = st.button(
                        "×",
                        key=(
                            f"remove_uploaded_photo_"
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
                <div>Use clear, well-lit photos</div>
            </div>
            <div class="upload-tip-item">
                <span>✓</span>
                <div>Make sure your face is clearly visible</div>
            </div>
            <div class="upload-tip-item">
                <span>✓</span>
                <div>Avoid group photos or heavy filters</div>
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
            f'({error["filename"]}) could not be opened.'
        )


def run_persona_analysis(images):
    """
    업로드한 사진의 Persona 분석을 실행합니다.
    """

    with st.spinner(
        "Analyzing all uploaded photos..."
    ):
        analysis_result = (
            analyze_multiple_face_personas(
                images
            )
        )

    if analysis_result.get(
        "success",
        False
    ):
        st.session_state[
            "analysis_result"
        ] = analysis_result

        go_to_page("result")

        return

    st.session_state.pop(
        "analysis_result",
        None
    )

    error_message = analysis_result.get(
        "message",
        "The photos could not be analyzed."
    )

    st.error(error_message)

    individual_results = analysis_result.get(
        "individual_results",
        []
    )

    for item in individual_results:
        if not item.get(
            "success",
            False
        ):
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
                f"Photo {image_index}: {message}"
            )


def show_upload_page():
    """
    Step 3. 사진 업로드 페이지입니다.
    """

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
        key=f"photo_uploader_{uploader_version}"
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

    # 사용자가 file_uploader의 파일 목록을 변경한 경우
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

        clear_upload_results()

    removed_file_keys = st.session_state.get(
        "removed_upload_file_keys",
        []
    )

    active_files = [
        uploaded_file
        for uploaded_file in (
            uploaded_files or []
        )
        if get_file_key(
            uploaded_file
        ) not in removed_file_keys
    ]

    too_many_images = (
        len(active_files) > MAX_IMAGES
    )

    if too_many_images:
        st.error(
            "You can upload up to 5 photos. "
            "Please remove extra files."
        )

    # 5장을 초과한 경우에도 앞의 5장은 미리보기로 표시합니다.
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

        else:
            clear_upload_results()

    else:
        images = []
        filenames = []
        active_file_keys = []

        clear_upload_results()

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
        run_persona_analysis(
            images
        )