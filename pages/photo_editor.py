from PIL import Image, ImageEnhance, ImageFilter


PURPOSE_SETTINGS = {
    "Resume": {
        "brightness": 1.06,
        "contrast": 1.08,
        "color": 0.96,
        "sharpness": 1.10
    },
    "LinkedIn": {
        "brightness": 1.05,
        "contrast": 1.07,
        "color": 1.04,
        "sharpness": 1.10
    },
    "Corporate Headshot": {
        "brightness": 1.04,
        "contrast": 1.10,
        "color": 0.98,
        "sharpness": 1.13
    }
}


PERSONAL_COLOR_SETTINGS = {
    "Spring Warm": {
        "red": 1.025,
        "green": 1.010,
        "blue": 0.980,
        "color": 1.04
    },
    "Summer Cool": {
        "red": 0.990,
        "green": 1.000,
        "blue": 1.025,
        "color": 0.98
    },
    "Autumn Warm": {
        "red": 1.030,
        "green": 1.005,
        "blue": 0.970,
        "color": 1.01
    },
    "Winter Cool": {
        "red": 0.985,
        "green": 0.995,
        "blue": 1.030,
        "color": 1.03
    }
}


def apply_rgb_balance(
    image,
    red_factor=1.0,
    green_factor=1.0,
    blue_factor=1.0
):
    """
    RGB 채널을 약하게 조절해 색온도를 보정합니다.
    """

    image = image.convert("RGB")

    red_channel, green_channel, blue_channel = image.split()

    red_channel = red_channel.point(
        lambda value: min(
            255,
            max(0, int(value * red_factor))
        )
    )

    green_channel = green_channel.point(
        lambda value: min(
            255,
            max(0, int(value * green_factor))
        )
    )

    blue_channel = blue_channel.point(
        lambda value: min(
            255,
            max(0, int(value * blue_factor))
        )
    )

    return Image.merge(
        "RGB",
        (
            red_channel,
            green_channel,
            blue_channel
        )
    )


def get_personal_color_name(color_analysis_result):
    """
    퍼스널컬러 분석 결과에서 계절명을 가져옵니다.
    """

    if not isinstance(color_analysis_result, dict):
        return None

    possible_keys = [
        "season",
        "personal_color",
        "result",
        "tone"
    ]

    for key in possible_keys:
        value = color_analysis_result.get(key)

        if isinstance(value, str):
            return value

    return None


def apply_personal_color_adjustment(
    image,
    personal_color=None
):
    """
    퍼스널컬러 결과에 따라 약한 색감 보정을 적용합니다.
    """

    if not personal_color:
        return image

    setting = PERSONAL_COLOR_SETTINGS.get(
        personal_color
    )

    if setting is None:
        return image

    adjusted_image = apply_rgb_balance(
        image=image,
        red_factor=setting["red"],
        green_factor=setting["green"],
        blue_factor=setting["blue"]
    )

    adjusted_image = ImageEnhance.Color(
        adjusted_image
    ).enhance(
        setting["color"]
    )

    return adjusted_image


def enhance_photo(
    image,
    purpose="Resume",
    personal_color=None
):
    """
    사용 목적과 퍼스널컬러에 따라 사진을 자연스럽게 보정합니다.

    적용 항목:
    - 밝기
    - 대비
    - 채도
    - 선명도
    - 퍼스널컬러 기반 색온도
    """

    if not isinstance(image, Image.Image):
        raise TypeError(
            "image는 PIL.Image.Image 형식이어야 합니다."
        )

    setting = PURPOSE_SETTINGS.get(
        purpose,
        PURPOSE_SETTINGS["Resume"]
    )

    enhanced_image = image.convert("RGB").copy()

    enhanced_image = ImageEnhance.Brightness(
        enhanced_image
    ).enhance(
        setting["brightness"]
    )

    enhanced_image = ImageEnhance.Contrast(
        enhanced_image
    ).enhance(
        setting["contrast"]
    )

    enhanced_image = ImageEnhance.Color(
        enhanced_image
    ).enhance(
        setting["color"]
    )

    enhanced_image = apply_personal_color_adjustment(
        image=enhanced_image,
        personal_color=personal_color
    )

    enhanced_image = ImageEnhance.Sharpness(
        enhanced_image
    ).enhance(
        setting["sharpness"]
    )

    enhanced_image = enhanced_image.filter(
        ImageFilter.UnsharpMask(
            radius=1,
            percent=35,
            threshold=4
        )
    )

    return enhanced_image