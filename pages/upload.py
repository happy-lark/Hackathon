import streamlit as st
from PIL import Image

from analysis.analyzer import (
    analyze_multiple_face_personas
)
from utils.navigation import (
    go_to_page,
    reset_analysis
)


MAX_IMAGES = 5


def load_uploaded_images(uploaded_files):
    """
    Streamlit UploadedFile 목록을 PIL 이미지 목록으로 변환합니다.
    """
    images = []
    errors = []

    for index, uploaded_file in enumerate(
        uploaded_files
    ):
        try:
            image = Image.open(
                uploaded_file
            ).convert("RGB")

            images.append(image)

        except Exception:
            errors.append(
                index + 1
            )

    return images, errors


def show_image_previews(images):
    """
    업로드한 이미지를 최대 3열 형태로 표시합니다.
    """
    st.markdown(
        f"#### Uploaded Photos ({len(images)}/{MAX_IMAGES})"
    )

    columns = st.columns(3)

    for index, image in enumerate(images):
        column = columns[index % 3]

        with column:
            st.image(
                image,
                caption=f"Photo {index + 1}",
                use_container_width=True
            )


def show_upload_page():
    st.markdown(
        '<div class="step-text">STEP 3 OF 3</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-title">
            Upload Your Photos
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-description">
            같은 사람의 얼굴이 선명하게 보이는 사진을
            최대 5장까지 업로드해주세요.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="info-card">
            📸 권장 사진 조건<br>
            · 모든 사진에 같은 사람만 포함<br>
            · 얼굴이 정면에 가까운 사진<br>
            · 한 사진에 한 사람만 포함<br>
            · 눈, 코, 입이 가려지지 않은 사진<br>
            · 얼굴이 너무 작지 않은 사진
        </div>
        """,
        unsafe_allow_html=True
    )

    uploader_version = st.session_state.get(
        "uploader_version",
        0
    )

    uploaded_files = st.file_uploader(
        "Upload your photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=f"photo_uploader_{uploader_version}"
    )

    too_many_images = (
        uploaded_files is not None
        and len(uploaded_files) > MAX_IMAGES
    )

    if too_many_images:
        st.error(
            "사진은 최대 5장까지만 업로드할 수 있습니다. "
            "사진 수를 줄여주세요."
        )

        st.session_state.pop(
            "uploaded_images",
            None
        )

    elif uploaded_files:
        images, image_errors = load_uploaded_images(
            uploaded_files
        )

        if image_errors:
            error_numbers = ", ".join(
                str(number)
                for number in image_errors
            )

            st.error(
                f"{error_numbers}번째 이미지 파일을 "
                "열 수 없습니다."
            )

        if images:
            st.session_state[
                "uploaded_images"
            ] = images

            st.session_state.pop(
                "analysis_result",
                None
            )

            st.session_state.pop(
                "color_analysis_result",
                None
            )

    else:
        st.session_state.pop(
            "uploaded_images",
            None
        )

    images = st.session_state.get(
        "uploaded_images",
        []
    )

    if images:
        show_image_previews(
            images
        )

    st.write("")

    back_column, analyze_column, color_column = (
        st.columns(3)
    )

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True
        ):
            go_to_page("target")

    with analyze_column:
        analyze_clicked = st.button(
            "✨ Analyze",
            type="primary",
            use_container_width=True,
            disabled=(
                not images
                or too_many_images
            )
        )

    with color_column:
        personal_color_clicked = st.button(
            "🎨 Personal Color",
            use_container_width=True,
            disabled=(
                not images
                or too_many_images
            )
        )

    if personal_color_clicked:
        go_to_page(
            "personal_color"
        )

    if analyze_clicked:
        with st.spinner(
            "Analyzing all uploaded photos..."
        ):
            analysis_result = (
                analyze_multiple_face_personas(
                    images
                )
            )

        if analysis_result["success"]:
            st.session_state[
                "analysis_result"
            ] = analysis_result

            go_to_page(
                "result"
            )

        else:
            st.session_state.pop(
                "analysis_result",
                None
            )

            st.error(
                analysis_result["message"]
            )

            individual_results = analysis_result.get(
                "individual_results",
                []
            )

            for item in individual_results:
                if not item["success"]:
                    st.warning(
                        f'Photo {item["image_index"] + 1}: '
                        f'{item["message"]}'
                    )

    if st.button(
        "Clear uploaded photos",
        use_container_width=True,
        key="clear_uploaded_photos"
    ):
        reset_analysis()

        st.session_state["uploader_version"] = (
            st.session_state.get(
                "uploader_version",
                0
            ) + 1
        )

        st.rerun()