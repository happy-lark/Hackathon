from pathlib import Path
import urllib.request

import mediapipe as mp
import numpy as np
import streamlit as st
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_DIRECTORY = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIRECTORY / "face_landmarker.task"

MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/"
    "face_landmarker.task"
)


# Target 페이지와 동일한 Persona 항목
PERSONA_NAMES = [
    "Professional",
    "Confident",
    "Approachable",
    "Creative"
]


def clamp(
    value,
    minimum=0.0,
    maximum=100.0
):
    """
    값을 지정된 범위로 제한합니다.
    """

    return max(
        minimum,
        min(maximum, value)
    )


def prepare_model():
    """
    MediaPipe 얼굴 분석 모델이 없을 경우 다운로드합니다.
    """

    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    if not MODEL_PATH.exists():
        urllib.request.urlretrieve(
            MODEL_URL,
            MODEL_PATH
        )

    return str(MODEL_PATH)


@st.cache_resource
def create_face_landmarker():
    """
    Face Landmarker 모델을 한 번만 생성합니다.
    """

    model_path = prepare_model()

    options = (
        mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=model_path
            ),
            running_mode=(
                mp.tasks.vision.RunningMode.IMAGE
            ),
            num_faces=2,
            output_face_blendshapes=True,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
    )

    return (
        mp.tasks.vision.FaceLandmarker
        .create_from_options(options)
    )


def get_blendshape_score(
    blendshapes,
    name
):
    """
    MediaPipe blendshape 결과에서 원하는 점수를 찾습니다.
    """

    for item in blendshapes:
        if item.category_name == name:
            return float(item.score)

    return 0.0


def calculate_frontality(landmarks):
    """
    얼굴이 카메라 정면을 향하는 정도를 계산합니다.
    """

    left_eye = landmarks[33]
    right_eye = landmarks[263]
    nose = landmarks[1]

    left_distance = abs(
        nose.x - left_eye.x
    )

    right_distance = abs(
        right_eye.x - nose.x
    )

    total_distance = (
        left_distance
        + right_distance
    )

    if total_distance == 0:
        return 0.0

    asymmetry = (
        abs(
            left_distance
            - right_distance
        )
        / total_distance
    )

    frontality = (
        1 - asymmetry
    ) * 100

    return clamp(frontality)


def calculate_head_level(landmarks):
    """
    양쪽 눈의 높이 차이로 고개가 수평인지 계산합니다.
    """

    left_eye = landmarks[33]
    right_eye = landmarks[263]

    horizontal_distance = abs(
        right_eye.x
        - left_eye.x
    )

    vertical_distance = abs(
        right_eye.y
        - left_eye.y
    )

    if horizontal_distance == 0:
        return 0.0

    slope = (
        vertical_distance
        / horizontal_distance
    )

    head_level = (
        1 - slope * 3
    ) * 100

    return clamp(head_level)


def calculate_face_centering(landmarks):
    """
    얼굴 중심이 사진 중앙에 가까운 정도를 계산합니다.
    """

    x_values = [
        landmark.x
        for landmark in landmarks
    ]

    y_values = [
        landmark.y
        for landmark in landmarks
    ]

    face_center_x = (
        min(x_values)
        + max(x_values)
    ) / 2

    face_center_y = (
        min(y_values)
        + max(y_values)
    ) / 2

    distance_from_center = np.sqrt(
        (face_center_x - 0.5) ** 2
        + (face_center_y - 0.5) ** 2
    )

    centering = (
        1
        - distance_from_center * 2
    ) * 100

    return clamp(centering)


def check_face_size(landmarks):
    """
    얼굴이 사진에서 충분히 크게 보이는지 확인합니다.
    """

    x_values = [
        landmark.x
        for landmark in landmarks
    ]

    y_values = [
        landmark.y
        for landmark in landmarks
    ]

    face_width = (
        max(x_values)
        - min(x_values)
    )

    face_height = (
        max(y_values)
        - min(y_values)
    )

    return (
        face_width >= 0.15
        and face_height >= 0.15
    )


def calculate_persona_from_features(
    features
):
    """
    얼굴 특징을 네 가지 Persona 점수로 변환합니다.

    각 점수는 서로 독립적인 0~100 값입니다.
    합계를 100으로 정규화하지 않습니다.
    """

    smile = features["Smile"]

    eye_openness = (
        features["Eye Openness"]
    )

    frontality = (
        features["Frontality"]
    )

    head_level = (
        features["Head Level"]
    )

    mouth_control = (
        features["Mouth Control"]
    )

    face_centering = (
        features["Face Centering"]
    )

    # 고개 기울기 정도
    head_tilt = clamp(
        100 - head_level
    )

    professional = (
        frontality * 0.30
        + head_level * 0.30
        + mouth_control * 0.25
        + face_centering * 0.15
    )

    confident = (
        frontality * 0.35
        + eye_openness * 0.25
        + head_level * 0.25
        + face_centering * 0.15
    )

    approachable = (
        smile * 0.55
        + eye_openness * 0.25
        + frontality * 0.20
    )

    # Creative는 표정의 생동감, 시선 개방성,
    # 약간의 포즈 변화 등을 이용한 휴리스틱 점수입니다.
    creative = (
        smile * 0.35
        + eye_openness * 0.25
        + head_tilt * 0.15
        + face_centering * 0.15
        + frontality * 0.10
    )

    return {
        "Professional": round(
            clamp(professional),
            1
        ),
        "Confident": round(
            clamp(confident),
            1
        ),
        "Approachable": round(
            clamp(approachable),
            1
        ),
        "Creative": round(
            clamp(creative),
            1
        )
    }


def analyze_face_persona(
    image: Image.Image
):
    """
    사진 한 장의 얼굴 특징과 Persona 점수를 반환합니다.
    """

    try:
        image = image.convert("RGB")
        image_array = np.asarray(image)

        image_array = np.ascontiguousarray(
            image_array
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_array
        )

        landmarker = create_face_landmarker()

        result = landmarker.detect(
            mp_image
        )

    except Exception as error:
        return {
            "success": False,
            "message": (
                "사진을 분석하는 중 오류가 발생했습니다. "
                "JPG, JPEG 또는 PNG 형식의 다른 사진을 "
                "사용해주세요."
            ),
            "error": str(error)
        }

    if not result.face_landmarks:
        return {
            "success": False,
            "message": (
                "얼굴을 감지하지 못했습니다. "
                "사람의 얼굴이 선명하게 보이는 정면 사진을 "
                "업로드해주세요."
            )
        }

    if len(result.face_landmarks) > 1:
        return {
            "success": False,
            "message": (
                "여러 명의 얼굴이 감지되었습니다. "
                "한 사람의 얼굴만 포함된 사진을 "
                "업로드해주세요."
            )
        }

    landmarks = result.face_landmarks[0]

    if not check_face_size(landmarks):
        return {
            "success": False,
            "message": (
                "사진 속 얼굴이 너무 작습니다. "
                "얼굴이 화면에 더 크게 보이는 사진을 "
                "업로드해주세요."
            )
        }

    if not result.face_blendshapes:
        return {
            "success": False,
            "message": (
                "얼굴 표정을 분석하지 못했습니다. "
                "조명이 밝고 얼굴이 가려지지 않은 사진을 "
                "사용해주세요."
            )
        }

    blendshapes = (
        result.face_blendshapes[0]
    )

    smile_left = get_blendshape_score(
        blendshapes,
        "mouthSmileLeft"
    )

    smile_right = get_blendshape_score(
        blendshapes,
        "mouthSmileRight"
    )

    blink_left = get_blendshape_score(
        blendshapes,
        "eyeBlinkLeft"
    )

    blink_right = get_blendshape_score(
        blendshapes,
        "eyeBlinkRight"
    )

    jaw_open = get_blendshape_score(
        blendshapes,
        "jawOpen"
    )

    smile = (
        (
            smile_left
            + smile_right
        )
        / 2
        * 100
    )

    eye_openness = (
        1
        - (
            blink_left
            + blink_right
        ) / 2
    ) * 100

    mouth_control = (
        1 - jaw_open
    ) * 100

    frontality = calculate_frontality(
        landmarks
    )

    head_level = calculate_head_level(
        landmarks
    )

    face_centering = (
        calculate_face_centering(
            landmarks
        )
    )

    features = {
        "Smile": round(
            clamp(smile),
            1
        ),
        "Eye Openness": round(
            clamp(eye_openness),
            1
        ),
        "Frontality": round(
            clamp(frontality),
            1
        ),
        "Head Level": round(
            clamp(head_level),
            1
        ),
        "Mouth Control": round(
            clamp(mouth_control),
            1
        ),
        "Face Centering": round(
            clamp(face_centering),
            1
        )
    }

    persona_scores = (
        calculate_persona_from_features(
            features
        )
    )

    return {
        "success": True,
        "features": features,

        # 기존 result.py 호환용
        "detected_persona": persona_scores,

        # Photo Comparison 페이지 호환용
        "persona_scores": persona_scores,
        "scores": persona_scores
    }


def analyze_multiple_face_personas(
    images
):
    """
    여러 사진을 각각 분석하고 종합 Persona 결과를 생성합니다.

    분석에 실패한 사진은 종합 평균에서 제외합니다.
    """

    individual_results = []
    valid_results = []
    failed_results = []

    for index, image in enumerate(
        images
    ):
        result = analyze_face_persona(
            image
        )

        result_with_index = {
            "image_index": index,
            **result
        }

        individual_results.append(
            result_with_index
        )

        if result.get(
            "success",
            False
        ):
            valid_results.append(
                result_with_index
            )

        else:
            failed_results.append(
                result_with_index
            )

    if not valid_results:
        return {
            "success": False,
            "message": (
                "분석 가능한 사진이 없습니다. "
                "얼굴이 선명하게 보이는 다른 사진을 "
                "업로드해주세요."
            ),
            "individual_results": (
                individual_results
            ),
            "valid_count": 0,
            "failed_count": len(
                failed_results
            ),
            "total_count": len(images)
        }

    feature_names = list(
        valid_results[0][
            "features"
        ].keys()
    )

    averaged_features = {}

    for feature_name in feature_names:
        feature_values = [
            result["features"][
                feature_name
            ]
            for result in valid_results
        ]

        averaged_features[
            feature_name
        ] = round(
            float(
                np.mean(
                    feature_values
                )
            ),
            1
        )

    overall_persona_scores = (
        calculate_persona_from_features(
            averaged_features
        )
    )

    return {
        "success": True,
        "features": averaged_features,

        # 기존 결과 페이지 호환용
        "detected_persona": (
            overall_persona_scores
        ),

        # 새 비교 페이지 호환용
        "persona_scores": (
            overall_persona_scores
        ),
        "scores": (
            overall_persona_scores
        ),

        # 사진별 점수 포함
        "individual_results": (
            individual_results
        ),

        "valid_count": len(
            valid_results
        ),
        "failed_count": len(
            failed_results
        ),
        "total_count": len(images)
    }