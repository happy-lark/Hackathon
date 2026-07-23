import streamlit as st
from PIL import Image

from analysis.analyzer import (
    analyze_multiple_face_personas
)
from analysis.image_editor import (
    process_images
)
from utils.navigation import (
    go_to_page,
    reset_analysis
)


MAX_IMAGES = 5

EDIT_NONE = "적용하지 않음"
EDIT_ENHANCE = "사진 보정"
EDIT_BACKGROUND = "배경 변경"
EDIT_BOTH = "사진 보정 + 배경 변경"

BACKGROUND_PERSONAL_COLOR = (
    "퍼스널컬러 추천 단색"
)
BACKGROUND_NATURE = "자연환경"


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


def create_upload_signature(uploaded_files):
    """
    실제 업로드 파일이 변경되었는지 확인하기 위한
    파일 정보 묶음을 생성합니다.
    """
    if not uploaded_files:
        return None

    return tuple(
        (
            uploaded_file.name,
            uploaded_file.size
        )
        for uploaded_file in uploaded_files
    )


def show_image_previews(images):
    """
    업로드한 이미지를 최대 3열 형태로 표시합니다.
    """
    st.markdown(
        f"#### Uploaded Photos "
        f"({len(images)}/{MAX_IMAGES})"
    )

    columns = st.columns(3)

    for index, image in enumerate(images):
        column = columns[
            index % 3
        ]

        with column:
            st.image(
                image,
                caption=f"Photo {index + 1}",
                use_container_width=True
            )


def initialize_image_edit_settings():
    """
    이미지 편집 관련 session_state 기본값을 설정합니다.
    """
    default_values = {
        "edit_option": EDIT_NONE,
        "background_type": (
            BACKGROUND_PERSONAL_COLOR
        ),
        "brightness_slider": 1.0,
        "saturation_slider": 1.0,
        "sharpness_slider": 1.0
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_image_edit_result():
    """
    이전 이미지 편집 결과를 제거합니다.
    """
    st.session_state.pop(
        "image_edit_result",
        None
    )


def show_image_edit_options():
    """
    사진 업로드 전에도 이미지 편집 옵션을 표시합니다.
    """
    st.divider()

    st.subheader(
        "✨ Additional Image Options"
    )

    st.caption(
        "사진을 업로드한 뒤 Edit Photos 버튼을 누르면 "
        "선택한 설정이 적용됩니다."
    )

    edit_option = st.radio(
        "사진에 적용할 기능을 선택해주세요.",
        options=[
            EDIT_NONE,
            EDIT_ENHANCE,
            EDIT_BACKGROUND,
            EDIT_BOTH
        ],
        horizontal=True,
        key="edit_option"
    )

    if edit_option in [
        EDIT_ENHANCE,
        EDIT_BOTH
    ]:
        st.markdown(
            "#### 📷 Photo Enhancement"
        )

        st.caption(
            "1.0은 원본과 동일한 값입니다."
        )

        adjustment_columns = st.columns(
            3
        )

        with adjustment_columns[0]:
            st.slider(
                "밝기",
                min_value=0.5,
                max_value=1.5,
                step=0.1,
                key="brightness_slider"
            )

        with adjustment_columns[1]:
            st.slider(
                "채도",
                min_value=0.5,
                max_value=1.5,
                step=0.1,
                key="saturation_slider"
            )

        with adjustment_columns[2]:
            st.slider(
                "선명도",
                min_value=0.5,
                max_value=2.0,
                step=0.1,
                key="sharpness_slider"
            )

        st.session_state[
            "image_adjustments"
        ] = {
            "brightness": (
                st.session_state[
                    "brightness_slider"
                ]
            ),
            "saturation": (
                st.session_state[
                    "saturation_slider"
                ]
            ),
            "sharpness": (
                st.session_state[
                    "sharpness_slider"
                ]
            )
        }

    if edit_option in [
        EDIT_BACKGROUND,
        EDIT_BOTH
    ]:
        st.markdown(
            "#### 🏞️ Background Replacement"
        )

        st.radio(
            "변경할 배경 유형을 선택해주세요.",
            options=[
                BACKGROUND_PERSONAL_COLOR,
                BACKGROUND_NATURE
            ],
            key="background_type"
        )

        st.info(
            "퍼스널컬러 분석 결과를 기준으로 "
            "어울리는 배경을 적용합니다. "
            "배경 변경 전 Personal Color 분석을 "
            "먼저 진행해주세요."
        )

    if edit_option == EDIT_NONE:
        st.caption(
            "별도의 사진 편집 없이 얼굴 인상 분석만 진행합니다."
        )


def show_upload_page():
    initialize_image_edit_settings()

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
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
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

        st.session_state.pop(
            "uploaded_file_signature",
            None
        )

        clear_image_edit_result()

    elif uploaded_files:
        current_signature = (
            create_upload_signature(
                uploaded_files
            )
        )

        previous_signature = (
            st.session_state.get(
                "uploaded_file_signature"
            )
        )

        if (
            current_signature
            != previous_signature
        ):
            images, image_errors = (
                load_uploaded_images(
                    uploaded_files
                )
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

                st.session_state[
                    "uploaded_file_signature"
                ] = current_signature

                st.session_state.pop(
                    "analysis_result",
                    None
                )

                st.session_state.pop(
                    "color_analysis_result",
                    None
                )

                clear_image_edit_result()

    else:
        st.session_state.pop(
            "uploaded_images",
            None
        )

        st.session_state.pop(
            "uploaded_file_signature",
            None
        )

        clear_image_edit_result()

    images = st.session_state.get(
        "uploaded_images",
        []
    )

    if images:
        show_image_previews(
            images
        )

    # 사진이 없어도 항상 표시
    show_image_edit_options()

    st.write("")

    (
        back_column,
        analyze_column,
        color_column,
        edit_column
    ) = st.columns(4)

    with back_column:
        if st.button(
            "← Back",
            use_container_width=True
        ):
            go_to_page(
                "target"
            )

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

    edit_option = st.session_state.get(
        "edit_option",
        EDIT_NONE
    )

    with edit_column:
        edit_clicked = st.button(
            "🪄 Edit Photos",
            use_container_width=True,
            disabled=(
                not images
                or too_many_images
                or edit_option == EDIT_NONE
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

            individual_results = (
                analysis_result.get(
                    "individual_results",
                    []
                )
            )

            for item in individual_results:
                if not item["success"]:
                    st.warning(
                        f'Photo '
                        f'{item["image_index"] + 1}: '
                        f'{item["message"]}'
                    )

    if edit_clicked:
        uses_background = (
            edit_option in [
                EDIT_BACKGROUND,
                EDIT_BOTH
            ]
        )

        color_analysis_result = (
            st.session_state.get(
                "color_analysis_result"
            )
        )

        if (
            uses_background
            and not color_analysis_result
        ):
            st.warning(
                "배경을 변경하려면 먼저 "
                "Personal Color 분석을 진행해주세요."
            )

        else:
            image_adjustments = (
                st.session_state.get(
                    "image_adjustments",
                    {
                        "brightness": 1.0,
                        "saturation": 1.0,
                        "sharpness": 1.0
                    }
                )
            )

            background_type = (
                st.session_state.get(
                    "background_type",
                    BACKGROUND_PERSONAL_COLOR
                )
            )

            with st.spinner(
                "Editing uploaded photos..."
            ):
                image_edit_result = (
                    process_images(
                        images=images,
                        edit_option=edit_option,
                        image_adjustments=(
                            image_adjustments
                        ),
                        background_type=(
                            background_type
                        ),
                        color_analysis_result=(
                            color_analysis_result
                        )
                    )
                )

            if image_edit_result["success"]:
                st.session_state[
                    "image_edit_result"
                ] = image_edit_result

                go_to_page(
                    "image_edit_result"
                )

            else:
                st.error(
                    "이미지를 편집하지 못했습니다."
                )

                for item in image_edit_result[
                    "results"
                ]:
                    if not item["success"]:
                        st.warning(
                            f'Photo '
                            f'{item["image_index"] + 1}: '
                            f'{item.get("message", "Unknown error")}'
                        )

    if st.button(
        "Clear uploaded photos",
        use_container_width=True,
        key="clear_uploaded_photos"
    ):
        reset_analysis()

        keys_to_remove = [
            "uploaded_images",
            "uploaded_file_signature",
            "analysis_result",
            "color_analysis_result",
            "image_edit_result",
            "image_adjustments",
            "edit_option",
            "background_type",
            "brightness_slider",
            "saturation_slider",
            "sharpness_slider"
        ]

        for key in keys_to_remove:
            st.session_state.pop(
                key,
                None
            )

        st.session_state[
            "uploader_version"
        ] = (
            st.session_state.get(
                "uploader_version",
                0
            ) + 1
        )

        st.rerun()