from PIL import ImageEnhance


def enhance_image(
    image,
    brightness=1.0,
    saturation=1.0,
    sharpness=1.0
):
    """
    밝기, 채도, 선명도를 조절한 이미지와
    적용 내역 설명을 반환합니다.
    """
    enhanced_image = image.convert("RGB")

    enhanced_image = ImageEnhance.Brightness(
        enhanced_image
    ).enhance(
        brightness
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

    description = generate_enhancement_description(
        brightness=brightness,
        saturation=saturation,
        sharpness=sharpness
    )

    return {
        "image": enhanced_image,
        "description": description,
        "settings": {
            "brightness": brightness,
            "saturation": saturation,
            "sharpness": sharpness
        }
    }


def generate_enhancement_description(
    brightness,
    saturation,
    sharpness
):
    """
    적용한 보정 내용을 문장으로 생성합니다.
    """
    descriptions = []

    if brightness > 1.0:
        descriptions.append(
            f"밝기를 {brightness:.1f}배 높였습니다."
        )

    elif brightness < 1.0:
        descriptions.append(
            f"밝기를 {brightness:.1f}배로 낮췄습니다."
        )

    else:
        descriptions.append(
            "밝기는 원본 상태를 유지했습니다."
        )

    if saturation > 1.0:
        descriptions.append(
            f"채도를 {saturation:.1f}배 높여 "
            "색감을 강조했습니다."
        )

    elif saturation < 1.0:
        descriptions.append(
            f"채도를 {saturation:.1f}배로 낮춰 "
            "차분한 색감으로 조정했습니다."
        )

    else:
        descriptions.append(
            "채도는 원본 상태를 유지했습니다."
        )

    if sharpness > 1.0:
        descriptions.append(
            f"선명도를 {sharpness:.1f}배 높여 "
            "윤곽을 선명하게 조정했습니다."
        )

    elif sharpness < 1.0:
        descriptions.append(
            f"선명도를 {sharpness:.1f}배로 낮춰 "
            "부드러운 느낌으로 조정했습니다."
        )

    else:
        descriptions.append(
            "선명도는 원본 상태를 유지했습니다."
        )

    return " ".join(
        descriptions
    )