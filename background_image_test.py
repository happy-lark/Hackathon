from io import BytesIO
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import (
    Image,
    ImageFilter,
    ImageOps
)


MODEL_PATH = Path(
    "assets/models/selfie_multiclass.tflite"
)


PRESET_BACKGROUNDS = {
    "🌲 숲": Path(
        "assets/backgrounds/forest.jpg"
    ),
    "🌊 바다": Path(
        "assets/backgrounds/ocean.jpg"
    ),
    "🌿 자연": Path(
        "assets/backgrounds/nature.jpg"
    )
}


def create_person_mask(image):
    """
    MediaPipe Selfie Multiclass 모델을 사용해
    사람 전체 영역을 마스크로 생성합니다.

    카테고리:
    0 = 배경
    1 = 머리카락
    2 = 신체 피부
    3 = 얼굴 피부
    4 = 옷
    5 = 액세서리 및 기타
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "모델 파일을 찾을 수 없습니다: "
            f"{MODEL_PATH}"
        )

    image_array = np.array(
        image.convert("RGB"),
        dtype=np.uint8
    )

    image_array = np.ascontiguousarray(
        image_array
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=image_array
    )

    base_options = python.BaseOptions(
        model_asset_path=str(
            MODEL_PATH
        )
    )

    options = vision.ImageSegmenterOptions(
        base_options=base_options,
        running_mode=(
            vision.RunningMode.IMAGE
        ),
        output_category_mask=True,
        output_confidence_masks=False
    )

    with vision.ImageSegmenter.create_from_options(
        options
    ) as segmenter:
        segmentation_result = (
            segmenter.segment(
                mp_image
            )
        )

    category_mask = (
        segmentation_result.category_mask
    )

    if category_mask is None:
        raise ValueError(
            "인물 분할 마스크를 생성하지 못했습니다."
        )

    category_array = (
        category_mask
        .numpy_view()
        .copy()
    )

    image_width, image_height = (
        image.size
    )

    if category_array.shape != (
        image_height,
        image_width
    ):
        category_array = cv2.resize(
            category_array,
            (
                image_width,
                image_height
            ),
            interpolation=cv2.INTER_NEAREST
        )

    # 0은 배경, 1 이상은 사람의 구성 요소
    person_mask = (
        category_array > 0
    ).astype(
        np.float32
    )

    # 인물 내부의 작은 빈 공간 제거
    close_kernel = np.ones(
        (7, 7),
        dtype=np.uint8
    )

    person_mask = cv2.morphologyEx(
        person_mask,
        cv2.MORPH_CLOSE,
        close_kernel
    )

    # 머리카락이나 얼굴 가장자리가
    # 잘리는 것을 줄이기 위해 약간 확장
    dilate_kernel = np.ones(
        (3, 3),
        dtype=np.uint8
    )

    person_mask = cv2.dilate(
        person_mask,
        dilate_kernel,
        iterations=1
    )

    # 가장자리를 자연스럽게 처리
    person_mask = cv2.GaussianBlur(
        person_mask,
        (9, 9),
        0
    )

    return np.clip(
        person_mask,
        0.0,
        1.0
    )


def fit_background_to_image(
    background_image,
    target_size
):
    """
    배경 이미지가 찌그러지지 않도록 비율을 유지하면서
    원본 사진 크기에 맞게 확대하고 중앙을 잘라냅니다.

    Zoom의 가상 배경과 비슷한 cover 방식입니다.
    """
    target_width, target_height = (
        target_size
    )

    background_image = (
        ImageOps.exif_transpose(
            background_image
        )
        .convert("RGB")
    )

    background_width, background_height = (
        background_image.size
    )

    width_scale = (
        target_width
        / background_width
    )

    height_scale = (
        target_height
        / background_height
    )

    # 빈 공간이 생기지 않도록 더 큰 배율 사용
    scale = max(
        width_scale,
        height_scale
    )

    resized_width = max(
        1,
        round(
            background_width
            * scale
        )
    )

    resized_height = max(
        1,
        round(
            background_height
            * scale
        )
    )

    resized_background = (
        background_image.resize(
            (
                resized_width,
                resized_height
            ),
            Image.Resampling.LANCZOS
        )
    )

    left = max(
        0,
        (
            resized_width
            - target_width
        ) // 2
    )

    top = max(
        0,
        (
            resized_height
            - target_height
        ) // 2
    )

    right = (
        left
        + target_width
    )

    bottom = (
        top
        + target_height
    )

    return resized_background.crop(
        (
            left,
            top,
            right,
            bottom
        )
    )


def change_background_to_image(
    image,
    background_image,
    blur_radius=0
):
    """
    원본 사진의 인물은 유지하고
    배경 영역만 선택한 이미지로 변경합니다.
    """
    original_image = (
        ImageOps.exif_transpose(
            image
        )
        .convert("RGB")
    )

    prepared_background = (
        fit_background_to_image(
            background_image=background_image,
            target_size=original_image.size
        )
    )

    if blur_radius > 0:
        prepared_background = (
            prepared_background.filter(
                ImageFilter.GaussianBlur(
                    radius=blur_radius
                )
            )
        )

    person_mask = create_person_mask(
        original_image
    )

    original_array = np.array(
        original_image,
        dtype=np.float32
    )

    background_array = np.array(
        prepared_background,
        dtype=np.float32
    )

    mask_3d = np.repeat(
        person_mask[
            :,
            :,
            np.newaxis
        ],
        3,
        axis=2
    )

    result_array = (
        original_array
        * mask_3d
        + background_array
        * (
            1.0
            - mask_3d
        )
    )

    result_array = np.clip(
        result_array,
        0,
        255
    ).astype(
        np.uint8
    )

    return {
        "edited_image": Image.fromarray(
            result_array
        ),
        "person_mask": person_mask,
        "prepared_background": (
            prepared_background
        )
    }


def mask_to_image(person_mask):
    """
    0~1 범위의 마스크를 화면에 표시할 수 있는
    흑백 PIL 이미지로 변환합니다.
    """
    mask_array = (
        person_mask
        * 255
    ).astype(
        np.uint8
    )

    return Image.fromarray(
        mask_array,
        mode="L"
    )


def image_to_bytes(image):
    """
    PIL 이미지를 다운로드용 PNG bytes로 변환합니다.
    """
    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    return buffer.getvalue()


def clear_previous_result():
    """
    이전 편집 결과를 session_state에서 제거합니다.
    """
    keys_to_remove = [
        "background_image_result",
        "background_person_mask",
        "background_prepared_image",
        "background_result_description"
    ]

    for key in keys_to_remove:
        st.session_state.pop(
            key,
            None
        )


st.set_page_config(
    page_title="Image Background Test",
    page_icon="🏞️",
    layout="centered"
)


st.title(
    "사진 배경 이미지 변경 테스트"
)

st.caption(
    "사진 속 인물은 유지하고 배경만 "
    "숲, 바다, 자연 또는 직접 업로드한 사진으로 변경합니다."
)


if not MODEL_PATH.exists():
    st.error(
        "모델 파일을 찾을 수 없습니다: "
        f"{MODEL_PATH}"
    )


uploaded_person_file = st.file_uploader(
    "인물이 포함된 사진을 업로드해주세요.",
    type=[
        "jpg",
        "jpeg",
        "png"
    ],
    key="person_image_uploader"
)


st.divider()

st.subheader(
    "🏞️ 배경 선택"
)


background_source = st.radio(
    "배경을 선택하는 방법",
    options=[
        "준비된 배경 사용",
        "배경 사진 직접 업로드"
    ],
    horizontal=True
)


background_image = None
background_description = None
background_signature = None


if background_source == "준비된 배경 사용":
    selected_preset = st.selectbox(
        "사용할 배경을 선택해주세요.",
        options=list(
            PRESET_BACKGROUNDS.keys()
        )
    )

    selected_background_path = (
        PRESET_BACKGROUNDS[
            selected_preset
        ]
    )

    background_signature = (
        "preset",
        selected_preset
    )

    if selected_background_path.exists():
        background_image = Image.open(
            selected_background_path
        ).convert("RGB")

        background_description = (
            f"{selected_preset} 프리셋"
        )

        st.image(
            background_image,
            caption=(
                f"Selected Background: "
                f"{selected_preset}"
            ),
            use_container_width=True
        )

    else:
        st.warning(
            "선택한 배경 이미지 파일이 없습니다: "
            f"{selected_background_path}"
        )

        st.info(
            "assets/backgrounds 폴더에 "
            "forest.jpg, ocean.jpg, nature.jpg를 "
            "추가해주세요."
        )


else:
    uploaded_background_file = (
        st.file_uploader(
            "새 배경으로 사용할 사진을 업로드해주세요.",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            key="custom_background_uploader"
        )
    )

    if uploaded_background_file is not None:
        background_image = Image.open(
            uploaded_background_file
        ).convert("RGB")

        background_description = (
            f"직접 업로드한 배경 "
            f"({uploaded_background_file.name})"
        )

        background_signature = (
            "upload",
            uploaded_background_file.name,
            uploaded_background_file.size
        )

        st.image(
            background_image,
            caption="Uploaded Background",
            use_container_width=True
        )


blur_radius = st.slider(
    "배경 흐림 정도",
    min_value=0,
    max_value=20,
    value=0,
    step=1,
    help=(
        "인물은 선명하게 유지하고 "
        "새 배경에만 블러를 적용합니다."
    )
)


show_person_mask = st.checkbox(
    "인물 마스크 확인하기",
    value=False,
    help=(
        "흰색은 인물로 유지되는 영역이고 "
        "검은색은 교체되는 배경 영역입니다."
    )
)


if uploaded_person_file is not None:
    original_image = Image.open(
        uploaded_person_file
    )

    original_image = (
        ImageOps.exif_transpose(
            original_image
        )
        .convert("RGB")
    )

    person_signature = (
        uploaded_person_file.name,
        uploaded_person_file.size
    )

    current_signature = (
        person_signature,
        background_signature,
        blur_radius
    )

    previous_signature = (
        st.session_state.get(
            "background_image_test_signature"
        )
    )

    if (
        current_signature
        != previous_signature
    ):
        clear_previous_result()

        st.session_state[
            "background_image_test_signature"
        ] = current_signature

    st.divider()

    st.subheader(
        "Original Photo"
    )

    st.image(
        original_image,
        use_container_width=True
    )

    test_clicked = st.button(
        "🪄 배경 이미지 변경",
        type="primary",
        use_container_width=True,
        disabled=(
            not MODEL_PATH.exists()
            or background_image is None
        )
    )

    if test_clicked:
        try:
            with st.spinner(
                "인물을 분리하고 새 배경을 적용하고 있습니다..."
            ):
                edit_result = (
                    change_background_to_image(
                        image=original_image,
                        background_image=(
                            background_image
                        ),
                        blur_radius=blur_radius
                    )
                )

            st.session_state[
                "background_image_result"
            ] = edit_result[
                "edited_image"
            ]

            st.session_state[
                "background_person_mask"
            ] = edit_result[
                "person_mask"
            ]

            st.session_state[
                "background_prepared_image"
            ] = edit_result[
                "prepared_background"
            ]

            st.session_state[
                "background_result_description"
            ] = (
                f"사진 속 인물 영역은 유지하고 "
                f"기존 배경만 {background_description}으로 "
                "변경했습니다. "
                f"배경 흐림 강도는 {blur_radius}입니다."
            )

        except Exception as error:
            st.error(
                "배경 이미지 변경 중 오류가 발생했습니다: "
                f"{error}"
            )


edited_image = st.session_state.get(
    "background_image_result"
)


if edited_image is not None:
    st.divider()

    st.subheader(
        "Result"
    )

    original_column, result_column = (
        st.columns(2)
    )

    with original_column:
        st.markdown(
            "#### Original"
        )

        st.image(
            original_image,
            use_container_width=True
        )

    with result_column:
        st.markdown(
            "#### Edited"
        )

        st.image(
            edited_image,
            use_container_width=True
        )

    result_description = (
        st.session_state.get(
            "background_result_description",
            "배경 이미지를 변경했습니다."
        )
    )

    st.success(
        result_description
    )

    if show_person_mask:
        person_mask = (
            st.session_state.get(
                "background_person_mask"
            )
        )

        prepared_background = (
            st.session_state.get(
                "background_prepared_image"
            )
        )

        debug_column1, debug_column2 = (
            st.columns(2)
        )

        if person_mask is not None:
            with debug_column1:
                st.markdown(
                    "#### Person Mask"
                )

                st.image(
                    mask_to_image(
                        person_mask
                    ),
                    caption=(
                        "흰색: 인물 / 검은색: 배경"
                    ),
                    use_container_width=True
                )

        if prepared_background is not None:
            with debug_column2:
                st.markdown(
                    "#### Prepared Background"
                )

                st.image(
                    prepared_background,
                    caption=(
                        "원본 사진 크기에 맞게 조정된 배경"
                    ),
                    use_container_width=True
                )

    st.download_button(
        "변경된 이미지 다운로드",
        data=image_to_bytes(
            edited_image
        ),
        file_name=(
            "image_background_changed.png"
        ),
        mime="image/png",
        use_container_width=True
    )