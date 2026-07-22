# MediaPipe로 얼굴 분석
from pathlib import Path
import urllib.request

import mediapipe as mp
import numpy as np
import streamlit as st
from PIL import Image


MODEL_DIRECTORY = Path("models")
MODEL_PATH = MODEL_DIRECTORY / "face_landmarker.task"

MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/face_landmarker/"
    "face_landmarker/float16/latest/"
    "face_landmarker.task"
)


def clamp(value, minimum=0.0, maximum=100.0):
    """
    값을 지정된 범위 안으로 제한합니다.
    """
    return max(minimum, min(maximum, value))


def prepare_model():
    """
    MediaPipe 얼굴 분석 모델이 없을 경우 자동 다운로드합니다.
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

    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=model_path
        ),
        running_mode=mp.tasks.vision.RunningMode.IMAGE,

        # 여러 명의 얼굴이 있는지 확인하기 위해 최대 2명 감지
        num_faces=2,

        # 표정 관련 blendshape 값 출력
        output_face_blendshapes=True,

        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    return mp.tasks.vision.FaceLandmarker.create_from_options(
        options
    )


def get_blendshape_score(blendshapes, name):
    """
    MediaPipe blendshape 결과에서 원하는 항목의 점수를 찾습니다.
    """

    for item in blendshapes:
        if item.category_name == name:
            return float(item.score)

    return 0.0


def calculate_frontality(landmarks):
    """
    코가 양쪽 눈 사이 중앙에 얼마나 가까운지 측정합니다.

    33  : 왼쪽 눈 바깥쪽
    263 : 오른쪽 눈 바깥쪽
    1   : 코끝
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
        left_distance + right_distance
    )

    if total_distance == 0:
        return 0.0

    asymmetry = (
        abs(left_distance - right_distance)
        / total_distance
    )

    frontality = (
        1 - asymmetry
    ) * 100

    return clamp(frontality)


def calculate_head_level(landmarks):
    """
    양쪽 눈의 높이 차이를 이용해
    고개가 얼마나 수평인지 측정합니다.
    """

    left_eye = landmarks[33]
    right_eye = landmarks[263]

    horizontal_distance = abs(
        right_eye.x - left_eye.x
    )

    vertical_distance = abs(
        right_eye.y - left_eye.y
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
    얼굴 중심이 사진 중앙에 얼마나 가까운지 측정합니다.
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
        min(x_values) + max(x_values)
    ) / 2

    face_center_y = (
        min(y_values) + max(y_values)
    ) / 2

    distance_from_center = np.sqrt(
        (face_center_x - 0.5) ** 2
        + (face_center_y - 0.5) ** 2
    )

    centering = (
        1 - distance_from_center * 2
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
        max(x_values) - min(x_values)
    )

    face_height = (
        max(y_values) - min(y_values)
    )

    return (
        face_width >= 0.15
        and face_height >= 0.15
    )


def detect_single_face(image: Image.Image):
    """
    이미지에서 한 사람의 얼굴을 검출하고
    이미지 배열, 랜드마크, 표정 데이터를 반환합니다.

    Persona 분석과 Personal Color 분석에서
    공통으로 사용하는 함수입니다.
    """

    if image is None:
        return {
            "success": False,
            "message": (
                "분석할 이미지가 없습니다. "
                "사진을 먼저 업로드해주세요."
            )
        }

    try:
        image = image.convert("RGB")
        image_array = np.asarray(image)

        # 일부 이미지에서 배열이 읽기 전용이 되는 문제 방지
        image_array = np.ascontiguousarray(
            image_array
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_array
        )

        landmarker = create_face_landmarker()
        result = landmarker.detect(mp_image)

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

    # 얼굴이 감지되지 않은 경우
    if not result.face_landmarks:
        return {
            "success": False,
            "message": (
                "얼굴을 감지하지 못했습니다. "
                "사람의 얼굴이 선명하게 보이는 정면 사진을 "
                "업로드해주세요."
            )
        }

    # 여러 명의 얼굴이 감지된 경우
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

    # 얼굴이 사진에서 너무 작게 나온 경우
    if not check_face_size(landmarks):
        return {
            "success": False,
            "message": (
                "사진 속 얼굴이 너무 작습니다. "
                "얼굴이 화면에 더 크게 보이는 사진을 "
                "업로드해주세요."
            )
        }

    blendshapes = None

    if result.face_blendshapes:
        blendshapes = result.face_blendshapes[0]

    return {
        "success": True,
        "image_array": image_array,
        "landmarks": landmarks,
        "blendshapes": blendshapes
    }


def normalize_persona(persona_scores):
    """
    네 Persona 점수의 합을 100으로 정규화합니다.
    """

    total = sum(persona_scores.values())

    if total <= 0:
        return {
            "Warm": 25.0,
            "Confident": 25.0,
            "Professional": 25.0,
            "Approachable": 25.0
        }

    return {
        name: round(
            score / total * 100,
            1
        )
        for name, score in persona_scores.items()
    }


def analyze_face_persona(image: Image.Image):
    """
    얼굴 특징을 분석하고 Persona 점수를 반환합니다.

    분석 특징:
    - Smile
    - Eye Openness
    - Frontality
    - Head Level
    - Mouth Control
    - Face Centering
    """

    # 공통 얼굴 검출 함수 사용
    face_result = detect_single_face(
        image
    )

    if not face_result["success"]:
        return face_result

    landmarks = face_result[
        "landmarks"
    ]

    blendshapes = face_result[
        "blendshapes"
    ]

    # Persona 분석에는 표정 데이터가 필요함
    if blendshapes is None:
        return {
            "success": False,
            "message": (
                "얼굴 표정을 분석하지 못했습니다. "
                "조명이 밝고 얼굴이 가려지지 않은 사진을 "
                "사용해주세요."
            )
        }

    # ------------------------------------------------
    # 표정 관련 MediaPipe 원본 값
    # ------------------------------------------------

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

    # ------------------------------------------------
    # 얼굴 특징 점수
    # ------------------------------------------------

    smile = (
        (smile_left + smile_right)
        / 2
        * 100
    )

    eye_openness = (
        1
        - (
            blink_left + blink_right
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

    face_centering = calculate_face_centering(
        landmarks
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

    # ------------------------------------------------
    # Persona 계산 기준
    # ------------------------------------------------

    warm = (
        features["Smile"] * 0.70
        + features["Eye Openness"] * 0.30
    )

    confident = (
        features["Frontality"] * 0.35
        + features["Eye Openness"] * 0.25
        + features["Head Level"] * 0.25
        + features["Face Centering"] * 0.15
    )

    professional = (
        features["Frontality"] * 0.30
        + features["Head Level"] * 0.30
        + features["Mouth Control"] * 0.25
        + features["Face Centering"] * 0.15
    )

    approachable = (
        features["Smile"] * 0.55
        + features["Eye Openness"] * 0.25
        + features["Frontality"] * 0.20
    )

    raw_persona = {
        "Warm": warm,
        "Confident": confident,
        "Professional": professional,
        "Approachable": approachable
    }

    detected_persona = normalize_persona(
        raw_persona
    )

    return {
        "success": True,
        "features": features,
        "detected_persona": detected_persona
    }