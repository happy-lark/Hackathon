"""
analysis/background_editor.py

MediaPipe Tasks ImageSegmenter를 사용해
사진 속 인물은 유지하고 배경만 변경합니다.

지원 배경:
- Blur
- Solid Color
- Office
- Urban
- Nature
"""

from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
    ImageOps
)


# ========================================
# 프로젝트 경로
# ========================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

MODEL_PATH = (
    PROJECT_ROOT
    / "assets"
    / "models"
    / "selfie_multiclass.tflite"
)


# 실제 파일이 존재하는 첫 번째 경로를 사용합니다.
BACKGROUND_FILE_CANDIDATES = {
    "office": [
        PROJECT_ROOT
        / "assets"
        / "backgrounds"
        / "office.jpg",

        PROJECT_ROOT
        / "assets"
        / "backgrounds"
        / "office.png"
    ],

    "urban": [
        PROJECT_ROOT
        / "assets"
        / "backgrounds"
        / "urban.jpg",

        PROJECT_ROOT
        / "assets"
        / "backgrounds"
        / "city.jpg",

        PROJECT_ROOT
        / "assets"
        / "backgrounds"
        / "urban.png"
    ],

    "nature": [
        PROJECT_ROOT
        / "assets"
        / "backgrounds"
        / "nature.jpg",

        PROJECT_ROOT
        / "assets"
        / "backgrounds"
        / "forest.jpg",

        PROJECT_ROOT
        / "assets"
        / "backgrounds"
        / "ocean.jpg"
    ]
}


PERSONAL_COLOR_BACKGROUNDS = {
    "Spring Warm": {
        "color": (250, 218, 174),
        "name": "Warm Peach"
    },
    "Summer Cool": {
        "color": (220, 216, 239),
        "name": "Soft Lavender"
    },
    "Autumn Warm": {
        "color": (196, 158, 117),
        "name": "Warm Camel"
    },
    "Winter Cool": {
        "color": (210, 230, 243),
        "name": "Icy Blue"
    }
}


# ========================================
# 퍼스널 컬러 결과 처리
# ========================================

def extract_personal_color_name(
    color_analysis_result
):
    """
    다양한 결과 구조에서 퍼스널 컬러 시즌명을 찾습니다.
    """

    if isinstance(
        color_analysis_result,
        str
    ):
        return color_analysis_result

    if isinstance(
        color_analysis_result,
        list
    ):
        for item in color_analysis_result:
            result = extract_personal_color_name(
                item
            )

            if result:
                return result

        return None

    if not isinstance(
        color_analysis_result,
        dict
    ):
        return None

    possible_keys = [
        "season",
        "personal_color",
        "color_type",
        "result",
        "final_result",
        "final_season",
        "dominant_season",
        "tone"
    ]

    for key in possible_keys:
        value = color_analysis_result.get(
            key
        )

        if isinstance(
            value,
            str
        ):
            return value

        nested_result = (
            extract_personal_color_name(
                value
            )
        )

        if nested_result:
            return nested_result

    for value in color_analysis_result.values():
        nested_result = (
            extract_personal_color_name(
                value
            )
        )

        if nested_result:
            return nested_result

    return None


def normalize_personal_color_name(
    personal_color_name
):
    """
    퍼스널 컬러 이름을 프로젝트의 시즌 이름으로 변환합니다.
    """

    if not personal_color_name:
        return None

    normalized_name = (
        str(personal_color_name)
        .strip()
        .lower()
    )

    aliases = {
        "spring": "Spring Warm",
        "spring warm": "Spring Warm",
        "봄": "Spring Warm",
        "봄 웜": "Spring Warm",
        "봄웜": "Spring Warm",

        "summer": "Summer Cool",
        "summer cool": "Summer Cool",
        "여름": "Summer Cool",
        "여름 쿨": "Summer Cool",
        "여름쿨": "Summer Cool",

        "autumn": "Autumn Warm",
        "autumn warm": "Autumn Warm",
        "가을": "Autumn Warm",
        "가을 웜": "Autumn Warm",
        "가을웜": "Autumn Warm",

        "winter": "Winter Cool",
        "winter cool": "Winter Cool",
        "겨울": "Winter Cool",
        "겨울 쿨": "Winter Cool",
        "겨울쿨": "Winter Cool"
    }

    return aliases.get(
        normalized_name
    )


# ========================================
# MediaPipe 인물 분할
# ========================================

def create_person_mask(
    image
):
    """
    MediaPipe Selfie Multiclass 모델을 사용해
    인물 전체 영역의 마스크를 생성합니다.

    모델 카테고리:
    0 = 배경
    1 = 머리카락
    2 = 신체 피부
    3 = 얼굴 피부
    4 = 옷
    5 = 액세서리 및 기타
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "MediaPipe segmentation model을 "
            "찾을 수 없습니다: "
            f"{MODEL_PATH}"
        )

    original_image = (
        ImageOps.exif_transpose(
            image
        )
        .convert("RGB")
    )

    image_array = np.asarray(
        original_image,
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
        running_mode=vision.RunningMode.IMAGE,
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
            "사진에서 인물 분할 마스크를 "
            "생성하지 못했습니다."
        )

    category_array = (
        category_mask
        .numpy_view()
        .copy()
    )

    image_width, image_height = (
        original_image.size
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

    # 0은 배경이며, 1 이상은 인물 구성 요소입니다.
    person_mask = (
        category_array > 0
    ).astype(
        np.float32
    )

    # 인물 내부의 작은 빈 공간을 채웁니다.
    close_kernel = np.ones(
        (7, 7),
        dtype=np.uint8
    )

    person_mask = cv2.morphologyEx(
        person_mask,
        cv2.MORPH_CLOSE,
        close_kernel
    )

    # 머리카락, 옷 가장자리 손실을 줄입니다.
    dilate_kernel = np.ones(
        (3, 3),
        dtype=np.uint8
    )

    person_mask = cv2.dilate(
        person_mask,
        dilate_kernel,
        iterations=1
    )

    # 합성 경계를 부드럽게 만듭니다.
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


# ========================================
# 배경 크기 조절
# ========================================

def fit_background_to_image(
    background_image,
    target_size
):
    """
    배경 비율을 유지하면서 원본 사진 전체를
    덮도록 확대하고 중앙을 자릅니다.
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

    if (
        background_width <= 0
        or background_height <= 0
    ):
        raise ValueError(
            "배경 이미지의 크기가 올바르지 않습니다."
        )

    width_scale = (
        target_width
        / background_width
    )

    height_scale = (
        target_height
        / background_height
    )

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

    return resized_background.crop(
        (
            left,
            top,
            left + target_width,
            top + target_height
        )
    )


# ========================================
# 배경 생성
# ========================================

def parse_hex_color(
    hex_color,
    fallback=(217, 220, 227)
):
    """
    #RRGGBB 문자열을 RGB 튜플로 변환합니다.
    """

    if not isinstance(
        hex_color,
        str
    ):
        return fallback

    cleaned_color = (
        hex_color.strip()
        .lstrip("#")
    )

    if len(cleaned_color) != 6:
        return fallback

    try:
        return tuple(
            int(
                cleaned_color[index:index + 2],
                16
            )
            for index in (
                0,
                2,
                4
            )
        )

    except ValueError:
        return fallback


def create_solid_background(
    size,
    color=None,
    personal_color_name=None
):
    """
    지정된 색상 또는 퍼스널 컬러 추천색으로
    단색 배경을 생성합니다.
    """

    if color:
        rgb_color = parse_hex_color(
            color
        )

        color_name = str(
            color
        )

    else:
        background_info = (
            PERSONAL_COLOR_BACKGROUNDS.get(
                personal_color_name,
                {
                    "color": (239, 235, 225),
                    "name": "Neutral Ivory"
                }
            )
        )

        rgb_color = background_info[
            "color"
        ]

        color_name = background_info[
            "name"
        ]

    return (
        Image.new(
            "RGB",
            size,
            rgb_color
        ),
        color_name
    )


def create_blurred_original_background(
    original_image,
    blur_radius=14
):
    """
    원본 배경 전체를 흐리게 만든 배경 이미지를 생성합니다.

    인물은 합성 단계에서 원본 상태로 다시 올라갑니다.
    """

    return original_image.filter(
        ImageFilter.GaussianBlur(
            radius=blur_radius
        )
    )


def create_generated_background(
    size,
    background_name
):
    """
    실제 배경 파일이 없을 때 사용할
    간단한 자동 생성 배경입니다.
    """

    width, height = size

    palettes = {
        "office": {
            "top": (235, 237, 241),
            "bottom": (201, 207, 218),
            "accent": (175, 181, 192)
        },
        "urban": {
            "top": (190, 205, 219),
            "bottom": (111, 124, 140),
            "accent": (75, 87, 103)
        },
        "nature": {
            "top": (198, 219, 224),
            "bottom": (104, 145, 117),
            "accent": (76, 118, 84)
        }
    }

    palette = palettes.get(
        background_name,
        palettes["office"]
    )

    background = Image.new(
        "RGB",
        size
    )

    pixels = background.load()

    for y in range(height):
        ratio = (
            y
            / max(
                height - 1,
                1
            )
        )

        color = tuple(
            int(
                palette["top"][channel]
                * (1 - ratio)
                + palette["bottom"][channel]
                * ratio
            )
            for channel in range(3)
        )

        for x in range(width):
            pixels[x, y] = color

    draw = ImageDraw.Draw(
        background,
        "RGBA"
    )

    if background_name == "office":
        # 흐릿한 창문과 벽 패널
        panel_width = max(
            40,
            int(width * 0.22)
        )

        for index in range(4):
            left = int(
                width * 0.05
            ) + index * int(
                width * 0.24
            )

            draw.rounded_rectangle(
                (
                    left,
                    int(height * 0.12),
                    left + panel_width,
                    int(height * 0.72)
                ),
                radius=12,
                fill=(255, 255, 255, 80)
            )

    elif background_name == "urban":
        # 도시 건물 실루엣
        building_width = max(
            24,
            int(width * 0.12)
        )

        for index in range(8):
            left = index * int(
                width / 8
            )

            building_height = int(
                height
                * (
                    0.25
                    + 0.08
                    * (
                        index % 4
                    )
                )
            )

            draw.rectangle(
                (
                    left,
                    height - building_height,
                    left + building_width,
                    height
                ),
                fill=(
                    palette["accent"][0],
                    palette["accent"][1],
                    palette["accent"][2],
                    150
                )
            )

    else:
        # 자연 배경 산과 수풀
        horizon = int(
            height * 0.58
        )

        draw.polygon(
            [
                (0, horizon),
                (
                    int(width * 0.28),
                    int(height * 0.30)
                ),
                (
                    int(width * 0.52),
                    horizon
                ),
                (
                    int(width * 0.75),
                    int(height * 0.36)
                ),
                (width, horizon)
            ],
            fill=(
                palette["accent"][0],
                palette["accent"][1],
                palette["accent"][2],
                155
            )
        )

    return background.filter(
        ImageFilter.GaussianBlur(
            radius=max(
                5,
                int(width * 0.01)
            )
        )
    )


def find_existing_background_path(
    background_name
):
    """
    지정된 배경 종류에서 실제 존재하는 첫 파일을 찾습니다.
    """

    candidate_paths = (
        BACKGROUND_FILE_CANDIDATES.get(
            background_name,
            []
        )
    )

    for path in candidate_paths:
        if path.exists():
            return path

    return None


def create_preset_background(
    size,
    background_name
):
    """
    Office, Urban, Nature 배경을 불러오거나
    파일이 없으면 자동으로 생성합니다.
    """

    background_path = (
        find_existing_background_path(
            background_name
        )
    )

    if background_path:
        background_image = Image.open(
            background_path
        )

        background_image = (
            fit_background_to_image(
                background_image=background_image,
                target_size=size
            )
        )

        return (
            background_image,
            background_path.name,
            False
        )

    generated_background = (
        create_generated_background(
            size=size,
            background_name=background_name
        )
    )

    return (
        generated_background,
        f"Generated {background_name} background",
        True
    )


# ========================================
# 합성
# ========================================

def composite_person_and_background(
    person_image,
    background_image,
    mask
):
    """
    인물은 원본에서 유지하고 배경 영역만 교체합니다.
    """

    person_image = (
        ImageOps.exif_transpose(
            person_image
        )
        .convert("RGB")
    )

    background_image = (
        fit_background_to_image(
            background_image,
            person_image.size
        )
    )

    person_array = np.asarray(
        person_image,
        dtype=np.float32
    )

    background_array = np.asarray(
        background_image,
        dtype=np.float32
    )

    image_width, image_height = (
        person_image.size
    )

    if mask.shape != (
        image_height,
        image_width
    ):
        mask = cv2.resize(
            mask,
            (
                image_width,
                image_height
            ),
            interpolation=cv2.INTER_LINEAR
        )

    mask_3_channels = np.repeat(
        mask[:, :, np.newaxis],
        3,
        axis=2
    ).astype(
        np.float32
    )

    composite_array = (
        person_array
        * mask_3_channels
        + background_array
        * (
            1.0
            - mask_3_channels
        )
    )

    composite_array = np.clip(
        composite_array,
        0,
        255
    ).astype(
        np.uint8
    )

    return Image.fromarray(
        composite_array
    )


# ========================================
# background_type 해석
# ========================================

def normalize_background_type(
    background_type
):
    """
    photo_editor.py에서 전달한 배경 설정을
    공통 형식으로 변환합니다.

    허용 예:
    "blur"
    "office"
    "urban"
    "nature"
    {"type": "solid", "color": "#BFD7F4"}
    """

    if isinstance(
        background_type,
        dict
    ):
        raw_type = background_type.get(
            "type",
            "solid"
        )

        normalized_type = (
            str(raw_type)
            .strip()
            .lower()
        )

        return {
            "type": normalized_type,
            "color": background_type.get(
                "color"
            ),
            "blur_radius": background_type.get(
                "blur_radius",
                14
            )
        }

    if not isinstance(
        background_type,
        str
    ):
        raise ValueError(
            "지원하지 않는 background_type입니다."
        )

    normalized_value = (
        background_type
        .strip()
        .lower()
    )

    aliases = {
        "blur": "blur",
        "블러": "blur",

        "solid": "solid",
        "solid color": "solid",
        "퍼스널컬러 추천 단색": "solid",

        "office": "office",
        "사무실": "office",

        "urban": "urban",
        "city": "urban",
        "도시": "urban",

        "nature": "nature",
        "forest": "nature",
        "자연": "nature",
        "자연환경": "nature"
    }

    normalized_type = aliases.get(
        normalized_value
    )

    if normalized_type is None:
        raise ValueError(
            "지원하지 않는 배경 유형입니다: "
            f"{background_type}"
        )

    return {
        "type": normalized_type,
        "color": None,
        "blur_radius": 14
    }


# ========================================
# 공개 함수
# ========================================

def change_background(
    image,
    background_type,
    color_analysis_result=None
):
    """
    사진 속 인물은 유지하고 배경만 변경합니다.

    Parameters
    ----------
    image:
        PIL.Image.Image

    background_type:
        "blur", "office", "urban", "nature"
        또는
        {"type": "solid", "color": "#RRGGBB"}

    color_analysis_result:
        Personal Color 분석 결과
    """

    if not isinstance(
        image,
        Image.Image
    ):
        raise TypeError(
            "image는 PIL.Image.Image 형식이어야 합니다."
        )

    original_image = (
        ImageOps.exif_transpose(
            image
        )
        .convert("RGB")
    )

    background_settings = (
        normalize_background_type(
            background_type
        )
    )

    selected_type = (
        background_settings["type"]
    )

    personal_color_name = (
        extract_personal_color_name(
            color_analysis_result
        )
    )

    personal_color_name = (
        normalize_personal_color_name(
            personal_color_name
        )
    )

    mask = create_person_mask(
        original_image
    )

    if selected_type == "blur":
        blur_radius = background_settings.get(
            "blur_radius",
            14
        )

        try:
            blur_radius = float(
                blur_radius
            )

        except (TypeError, ValueError):
            blur_radius = 14

        background_image = (
            create_blurred_original_background(
                original_image=original_image,
                blur_radius=blur_radius
            )
        )

        description = (
            "사진 속 인물은 선명하게 유지하고 "
            f"기존 배경에 블러 강도 {blur_radius:g}를 "
            "적용했습니다."
        )

    elif selected_type == "solid":
        selected_color = (
            background_settings.get(
                "color"
            )
        )

        (
            background_image,
            color_name
        ) = create_solid_background(
            size=original_image.size,
            color=selected_color,
            personal_color_name=personal_color_name
        )

        if selected_color:
            description = (
                "사진 속 인물은 유지하고 배경만 "
                f"{color_name} 단색으로 변경했습니다."
            )

        else:
            resolved_season = (
                personal_color_name
                or "Neutral"
            )

            description = (
                f"{resolved_season} 퍼스널 컬러에 어울리는 "
                f"{color_name} 계열의 단색으로 "
                "배경을 변경했습니다."
            )

    elif selected_type in {
        "office",
        "urban",
        "nature"
    }:
        (
            background_image,
            background_source,
            generated
        ) = create_preset_background(
            size=original_image.size,
            background_name=selected_type
        )
        
        # 배경만 블러 처리해서 자연스러운 심도 효과 연출
        background_image = background_image.filter(
            ImageFilter.GaussianBlur(radius=12)
        )

        display_name = (
            selected_type.capitalize()
        )

        if generated:
            source_description = (
                "실제 배경 파일이 없어 자동 생성된 "
                f"{display_name} 배경을 사용했습니다."
            )

        else:
            source_description = (
                f"{background_source} 파일을 사용했습니다."
            )

        description = (
            "사진 속 인물은 유지하고 기존 배경만 "
            f"{display_name} 배경으로 변경했습니다. "
            f"{source_description}"
        )

    else:
        raise ValueError(
            "지원하지 않는 배경 유형입니다: "
            f"{selected_type}"
        )

    changed_image = (
        composite_person_and_background(
            person_image=original_image,
            background_image=background_image,
            mask=mask
        )
    )

    return {
        "image": changed_image,
        "description": description,
        "personal_color": personal_color_name,
        "background_type": selected_type,
        "person_mask": mask,
        "background_image": background_image
    }