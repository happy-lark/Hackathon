from PIL import Image

from analysis.background_editor import (
    change_background
)
from analysis.image_enhancer import (
    enhance_image
)


EDIT_NONE = "적용하지 않음"
EDIT_ENHANCE = "사진 보정"
EDIT_BACKGROUND = "배경 변경"
EDIT_BOTH = "사진 보정 + 배경 변경"


DEFAULT_IMAGE_ADJUSTMENTS = {
    "brightness": 1.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "sharpness": 1.0
}


def normalize_image_adjustments(
    image_adjustments
):
    """
    전달된 보정값을 기본값과 합쳐
    모든 키가 존재하도록 정리합니다.
    """

    if not isinstance(
        image_adjustments,
        dict
    ):
        image_adjustments = {}

    normalized_adjustments = (
        DEFAULT_IMAGE_ADJUSTMENTS.copy()
    )

    for key in DEFAULT_IMAGE_ADJUSTMENTS:
        value = image_adjustments.get(
            key,
            DEFAULT_IMAGE_ADJUSTMENTS[key]
        )

        try:
            normalized_adjustments[key] = float(
                value
            )

        except (TypeError, ValueError):
            normalized_adjustments[key] = (
                DEFAULT_IMAGE_ADJUSTMENTS[
                    key
                ]
            )

    return normalized_adjustments


def validate_edit_option(
    edit_option
):
    """
    edit_option이 허용된 값인지 확인합니다.
    """

    valid_options = {
        EDIT_NONE,
        EDIT_ENHANCE,
        EDIT_BACKGROUND,
        EDIT_BOTH
    }

    if edit_option not in valid_options:
        raise ValueError(
            f"지원하지 않는 편집 옵션입니다: "
            f"{edit_option}"
        )


def process_single_image(
    original_image,
    edit_option,
    image_adjustments,
    background_type,
    color_analysis_result
):
    """
    단일 이미지에 배경 변경과 사진 보정을 적용합니다.
    """

    if not isinstance(
        original_image,
        Image.Image
    ):
        raise TypeError(
            "original_image는 PIL.Image.Image "
            "형식이어야 합니다."
        )

    processed_image = original_image.convert(
        "RGB"
    )

    descriptions = []

    background_result = None
    enhancement_result = None

    if edit_option in {
        EDIT_BACKGROUND,
        EDIT_BOTH
    }:
        if background_type is None:
            raise ValueError(
                "배경 변경 옵션을 선택했지만 "
                "background_type이 없습니다."
            )

        background_result = change_background(
            image=processed_image,
            background_type=background_type,
            color_analysis_result=(
                color_analysis_result
            )
        )

        if not isinstance(
            background_result,
            dict
        ):
            raise TypeError(
                "change_background()의 결과는 "
                "dict 형식이어야 합니다."
            )

        background_image = (
            background_result.get(
                "image"
            )
        )

        if not isinstance(
            background_image,
            Image.Image
        ):
            raise TypeError(
                "배경 변경 결과에 유효한 "
                "PIL 이미지가 없습니다."
            )

        processed_image = (
            background_image.convert(
                "RGB"
            )
        )

        background_description = (
            background_result.get(
                "description"
            )
        )

        if background_description:
            descriptions.append(
                str(
                    background_description
                )
            )

    if edit_option in {
        EDIT_ENHANCE,
        EDIT_BOTH
    }:
        enhancement_result = enhance_image(
            image=processed_image,
            brightness=image_adjustments.get(
                "brightness",
                1.0
            ),
            contrast=image_adjustments.get(
                "contrast",
                1.0
            ),
            saturation=image_adjustments.get(
                "saturation",
                1.0
            ),
            sharpness=image_adjustments.get(
                "sharpness",
                1.0
            )
        )

        if not isinstance(
            enhancement_result,
            dict
        ):
            raise TypeError(
                "enhance_image()의 결과는 "
                "dict 형식이어야 합니다."
            )

        enhanced_image = (
            enhancement_result.get(
                "image"
            )
        )

        if not isinstance(
            enhanced_image,
            Image.Image
        ):
            raise TypeError(
                "사진 보정 결과에 유효한 "
                "PIL 이미지가 없습니다."
            )

        processed_image = (
            enhanced_image.convert(
                "RGB"
            )
        )

        enhancement_description = (
            enhancement_result.get(
                "description"
            )
        )

        if enhancement_description:
            descriptions.append(
                str(
                    enhancement_description
                )
            )

    if edit_option == EDIT_NONE:
        descriptions.append(
            "원본 이미지를 그대로 유지했습니다."
        )

    return {
        "edited_image": processed_image,
        "descriptions": descriptions,
        "background_result": (
            background_result
        ),
        "enhancement_result": (
            enhancement_result
        )
    }


def process_images(
    images,
    edit_option,
    image_adjustments=None,
    background_type=None,
    color_analysis_result=None
):
    """
    여러 이미지에 사용자가 선택한 편집 기능을 적용합니다.

    지원 기능:
    - 적용하지 않음
    - 사진 보정
    - 배경 변경
    - 사진 보정 + 배경 변경
    """

    validate_edit_option(
        edit_option
    )

    image_adjustments = (
        normalize_image_adjustments(
            image_adjustments
        )
    )

    if not isinstance(
        images,
        (list, tuple)
    ):
        raise TypeError(
            "images는 이미지 리스트 또는 "
            "튜플이어야 합니다."
        )

    results = []

    for index, original_image in enumerate(
        images
    ):
        try:
            processing_result = (
                process_single_image(
                    original_image=(
                        original_image
                    ),
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

            results.append(
                {
                    "image_index": index,
                    "success": True,
                    "original_image": (
                        original_image
                    ),
                    "edited_image": (
                        processing_result[
                            "edited_image"
                        ]
                    ),
                    "descriptions": (
                        processing_result[
                            "descriptions"
                        ]
                    ),
                    "background_result": (
                        processing_result[
                            "background_result"
                        ]
                    ),
                    "enhancement_result": (
                        processing_result[
                            "enhancement_result"
                        ]
                    ),
                    "settings": {
                        "edit_option": edit_option,
                        "image_adjustments": (
                            image_adjustments.copy()
                        ),
                        "background_type": (
                            background_type
                        )
                    }
                }
            )

        except Exception as error:
            results.append(
                {
                    "image_index": index,
                    "success": False,
                    "original_image": (
                        original_image
                    ),
                    "edited_image": None,
                    "descriptions": [],
                    "background_result": None,
                    "enhancement_result": None,
                    "settings": {
                        "edit_option": edit_option,
                        "image_adjustments": (
                            image_adjustments.copy()
                        ),
                        "background_type": (
                            background_type
                        )
                    },
                    "message": str(
                        error
                    )
                }
            )

    success_count = sum(
        1
        for result in results
        if result["success"]
    )

    failed_count = (
        len(results)
        - success_count
    )

    return {
        "success": success_count > 0,
        "results": results,
        "success_count": success_count,
        "failed_count": failed_count,
        "edit_option": edit_option,
        "image_adjustments": (
            image_adjustments.copy()
        ),
        "background_type": (
            background_type
        )
    }