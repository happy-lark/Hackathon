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


def process_images(
    images,
    edit_option,
    image_adjustments=None,
    background_type=None,
    color_analysis_result=None
):
    """
    여러 이미지에 사용자가 선택한 편집 기능을 적용합니다.
    """
    image_adjustments = (
        image_adjustments
        or {
            "brightness": 1.0,
            "saturation": 1.0,
            "sharpness": 1.0
        }
    )

    results = []

    for index, original_image in enumerate(
        images
    ):
        try:
            processed_image = (
                original_image
                .convert("RGB")
            )

            descriptions = []

            if edit_option in [
                EDIT_BACKGROUND,
                EDIT_BOTH
            ]:
                background_result = (
                    change_background(
                        image=processed_image,
                        background_type=(
                            background_type
                        ),
                        color_analysis_result=(
                            color_analysis_result
                        )
                    )
                )

                processed_image = (
                    background_result["image"]
                )

                descriptions.append(
                    background_result[
                        "description"
                    ]
                )

            if edit_option in [
                EDIT_ENHANCE,
                EDIT_BOTH
            ]:
                enhancement_result = (
                    enhance_image(
                        image=processed_image,
                        brightness=(
                            image_adjustments.get(
                                "brightness",
                                1.0
                            )
                        ),
                        saturation=(
                            image_adjustments.get(
                                "saturation",
                                1.0
                            )
                        ),
                        sharpness=(
                            image_adjustments.get(
                                "sharpness",
                                1.0
                            )
                        )
                    )
                )

                processed_image = (
                    enhancement_result["image"]
                )

                descriptions.append(
                    enhancement_result[
                        "description"
                    ]
                )

            results.append(
                {
                    "image_index": index,
                    "success": True,
                    "original_image": (
                        original_image
                    ),
                    "edited_image": (
                        processed_image
                    ),
                    "descriptions": (
                        descriptions
                    )
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
                    "message": str(error)
                }
            )

    success_count = sum(
        1
        for result in results
        if result["success"]
    )

    return {
        "success": success_count > 0,
        "results": results,
        "success_count": success_count,
        "failed_count": (
            len(results)
            - success_count
        )
    }