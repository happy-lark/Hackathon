from PIL import ImageEnhance


def clamp_factor(
    value,
    minimum=0.5,
    maximum=1.5
):
    """
    보정 배율을 안전한 범위로 제한합니다.
    """

    try:
        numeric_value = float(value)

    except (TypeError, ValueError):
        numeric_value = 1.0

    return max(
        minimum,
        min(maximum, numeric_value)
    )


def enhance_image(
    image,
    brightness=1.0,
    contrast=1.0,
    saturation=1.0,
    sharpness=1.0
):
    """
    밝기, 대비, 채도, 선명도를 조절한 이미지와
    적용 내역 설명을 반환합니다.
    """

    brightness = clamp_factor(
        brightness
    )

    contrast = clamp_factor(
        contrast
    )

    saturation = clamp_factor(
        saturation
    )

    sharpness = clamp_factor(
        sharpness
    )

    enhanced_image = image.convert(
        "RGB"
    )

    enhanced_image = ImageEnhance.Brightness(
        enhanced_image
    ).enhance(
        brightness
    )

    enhanced_image = ImageEnhance.Contrast(
        enhanced_image
    ).enhance(
        contrast
    )

    enhanced_image = ImageEnhance.Color(
        enhanced_image
    ).enhance(
        saturation
    )

    enhanced_image = ImageEnhance.Sharpness(
        enhanced_image
    ).enhance(
        sharpness
    )

    description = (
        generate_enhancement_description(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            sharpness=sharpness
        )
    )

    return {
        "image": enhanced_image,
        "description": description,
        "settings": {
            "brightness": brightness,
            "contrast": contrast,
            "saturation": saturation,
            "sharpness": sharpness
        }
    }


def describe_factor(
    label,
    factor,
    increase_text,
    decrease_text,
    keep_text
):
    """
    각 보정값에 대한 설명 문장을 생성합니다.
    """

    difference = (
        factor - 1.0
    )

    percent = round(
        abs(difference) * 100
    )

    if percent == 0:
        return keep_text

    if factor > 1.0:
        return (
            f"{label}를 약 {percent}% 높여 "
            f"{increase_text}"
        )

    return (
        f"{label}를 약 {percent}% 낮춰 "
        f"{decrease_text}"
    )


def generate_enhancement_description(
    brightness,
    contrast,
    saturation,
    sharpness
):
    """
    실제 적용된 보정값을 기반으로
    설명 문장을 생성합니다.
    """

    descriptions = [
        describe_factor(
            label="밝기",
            factor=brightness,
            increase_text=(
                "사진을 더 밝게 조정했습니다."
            ),
            decrease_text=(
                "노출을 차분하게 조정했습니다."
            ),
            keep_text=(
                "밝기는 원본 상태를 유지했습니다."
            )
        ),
        describe_factor(
            label="대비",
            factor=contrast,
            increase_text=(
                "명암 구분을 더 선명하게 했습니다."
            ),
            decrease_text=(
                "명암 차이를 부드럽게 조정했습니다."
            ),
            keep_text=(
                "대비는 원본 상태를 유지했습니다."
            )
        ),
        describe_factor(
            label="채도",
            factor=saturation,
            increase_text=(
                "색감을 더 풍부하게 조정했습니다."
            ),
            decrease_text=(
                "색감을 차분하게 조정했습니다."
            ),
            keep_text=(
                "채도는 원본 상태를 유지했습니다."
            )
        ),
        describe_factor(
            label="선명도",
            factor=sharpness,
            increase_text=(
                "윤곽과 디테일을 더 또렷하게 했습니다."
            ),
            decrease_text=(
                "윤곽을 부드럽게 조정했습니다."
            ),
            keep_text=(
                "선명도는 원본 상태를 유지했습니다."
            )
        )
    ]

    return " ".join(
        descriptions
    )