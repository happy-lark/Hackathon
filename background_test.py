from io import BytesIO
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import streamlit as st
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image


MODEL_PATH = Path(
    "assets/models/selfie_multiclass.tflite"
)

def create_person_mask(image):
    """
    MediaPipe Selfie Multiclass 모델을 이용해
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
        model_asset_path=str(MODEL_PATH)
    )

    options = vision.ImageSegmenterOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        output_category_mask=True,
        output_confidence_masks=False
    )

    with vision.ImageSegmenter.create_from_options(
        options
    ) as segmenter:
        segmentation_result = segmenter.segment(
            mp_image
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

    image_width, image_height = image.size

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

    # 0은 배경, 1~5는 사람의 구성 요소
    person_mask = (
        category_array > 0
    ).astype(
        np.float32
    )

    # 사람 영역 내부의 작은 구멍 채우기
    close_kernel = np.ones(
        (7, 7),
        dtype=np.uint8
    )

    person_mask = cv2.morphologyEx(
        person_mask,
        cv2.MORPH_CLOSE,
        close_kernel
    )

    # 사람 영역을 약간 넓혀 얼굴이나 머리카락 손실 방지
    dilate_kernel = np.ones(
        (3, 3),
        dtype=np.uint8
    )

    person_mask = cv2.dilate(
        person_mask,
        dilate_kernel,
        iterations=1
    )

    # 경계를 자연스럽게 처리
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

def hex_to_rgb(hex_color):
    """
    #DCE8F2 형태의 색상값을 RGB 튜플로 변환합니다.
    """
    normalized_hex = hex_color.lstrip(
        "#"
    )

    if len(normalized_hex) != 6:
        raise ValueError(
            "올바르지 않은 색상 형식입니다."
        )

    return tuple(
        int(
            normalized_hex[index:index + 2],
            16
        )
        for index in (
            0,
            2,
            4
        )
    )


def change_background_color(
    image,
    background_color
):
    """
    사람 영역은 원본으로 유지하고
    배경 영역만 지정한 색으로 변경합니다.
    """
    original_image = image.convert(
        "RGB"
    )

    original_array = np.array(
        original_image,
        dtype=np.float32
    )

    person_mask = create_person_mask(
        original_image
    )

    background_array = np.full(
        original_array.shape,
        background_color,
        dtype=np.float32
    )

    mask_3d = np.repeat(
        person_mask[:, :, np.newaxis],
        3,
        axis=2
    )

    result_array = (
        original_array * mask_3d
        + background_array * (
            1.0 - mask_3d
        )
    )

    result_array = np.clip(
        result_array,
        0,
        255
    ).astype(
        np.uint8
    )

    return Image.fromarray(
        result_array
    )


def image_to_bytes(image):
    """
    PIL 이미지를 PNG bytes로 변환합니다.
    """
    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    return buffer.getvalue()


st.set_page_config(
    page_title="Background Test",
    page_icon="🖼️"
)

st.title(
    "인물 배경 변경 테스트"
)

st.caption(
    "사진 속 사람은 유지하고 "
    "배경만 선택한 단색으로 변경합니다."
)

if not MODEL_PATH.exists():
    st.error(
        "모델 파일이 없습니다: "
        "assets/models/selfie_segmenter.tflite"
    )

    st.code(
        """
New-Item -ItemType Directory -Force assets\\models

Invoke-WebRequest `
  -Uri "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite" `
  -OutFile "assets\\models\\selfie_segmenter.tflite"
        """,
        language="powershell"
    )

uploaded_file = st.file_uploader(
    "사람이 포함된 사진을 업로드해주세요.",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)

background_hex = st.color_picker(
    "변경할 배경색을 선택해주세요.",
    value="#DCE8F2"
)


if uploaded_file is not None:
    current_file_signature = (
        uploaded_file.name,
        uploaded_file.size
    )

    previous_file_signature = (
        st.session_state.get(
            "background_test_file_signature"
        )
    )

    if (
        current_file_signature
        != previous_file_signature
    ):
        st.session_state.pop(
            "background_test_result",
            None
        )

        st.session_state[
            "background_test_file_signature"
        ] = current_file_signature

    original_image = Image.open(
        uploaded_file
    ).convert(
        "RGB"
    )

    st.subheader(
        "Original"
    )

    st.image(
        original_image,
        use_container_width=True
    )

    test_clicked = st.button(
        "배경 변경 테스트",
        type="primary",
        use_container_width=True,
        disabled=not MODEL_PATH.exists()
    )

    if test_clicked:
        try:
            background_color = hex_to_rgb(
                background_hex
            )

            with st.spinner(
                "사람과 배경을 분리하고 있습니다..."
            ):
                edited_image = (
                    change_background_color(
                        image=original_image,
                        background_color=(
                            background_color
                        )
                    )
                )

            st.session_state[
                "background_test_result"
            ] = edited_image

            st.session_state[
                "background_test_color"
            ] = background_hex

        except Exception as error:
            st.error(
                "배경 변경 중 오류가 발생했습니다: "
                f"{error}"
            )

    edited_image = st.session_state.get(
        "background_test_result"
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

        applied_color = (
            st.session_state.get(
                "background_test_color",
                background_hex
            )
        )

        st.success(
            "인물 영역은 유지하고 "
            f"배경을 {applied_color} 색상으로 변경했습니다."
        )

        st.download_button(
            "변경된 이미지 다운로드",
            data=image_to_bytes(
                edited_image
            ),
            file_name=(
                "background_changed.png"
            ),
            mime="image/png",
            use_container_width=True
        )