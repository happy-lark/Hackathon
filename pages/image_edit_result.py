from io import BytesIO

import streamlit as st

from utils.navigation import (
    go_to_page
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


def show_image_edit_result_page():
    edit_result = st.session_state.get(
        "image_edit_result"
    )

    if not edit_result:
        st.error(
            "이미지 편집 결과를 찾을 수 없습니다."
        )

        if st.button(
            "Return to Upload",
            use_container_width=True
        ):
            go_to_page(
                "upload"
            )

        return

    st.markdown(
        """
        <div class="page-title">
            Your Edited Photos ✨
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="page-description">
            원본 사진과 편집된 사진을 비교하고
            결과 이미지를 저장할 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    success_count = edit_result.get(
        "success_count",
        0
    )

    failed_count = edit_result.get(
        "failed_count",
        0
    )

    if failed_count:
        st.warning(
            f"{success_count}장의 편집을 완료했고, "
            f"{failed_count}장은 처리하지 못했습니다."
        )

    else:
        st.success(
            f"{success_count}장의 이미지 편집을 완료했습니다."
        )

    results = edit_result.get(
        "results",
        []
    )

    for item in results:
        photo_number = (
            item["image_index"] + 1
        )

        st.divider()

        st.subheader(
            f"Photo {photo_number}"
        )

        if not item["success"]:
            st.error(
                item.get(
                    "message",
                    "이미지를 편집하지 못했습니다."
                )
            )

            continue

        original_column, edited_column = (
            st.columns(2)
        )

        with original_column:
            st.markdown(
                "#### Original"
            )

            st.image(
                item["original_image"],
                use_container_width=True
            )

        with edited_column:
            st.markdown(
                "#### Edited"
            )

            st.image(
                item["edited_image"],
                use_container_width=True
            )

        st.markdown(
            "#### Applied Changes"
        )

        descriptions = item.get(
            "descriptions",
            []
        )

        for description in descriptions:
            st.info(
                description
            )

        edited_image_bytes = (
            image_to_bytes(
                item["edited_image"]
            )
        )

        st.download_button(
            label=(
                f"Download Edited Photo "
                f"{photo_number}"
            ),
            data=edited_image_bytes,
            file_name=(
                f"edited_photo_{photo_number}.png"
            ),
            mime="image/png",
            use_container_width=True,
            key=(
                f"download_edited_photo_"
                f"{photo_number}"
            )
        )

    st.write("")

    back_column, result_column = (
        st.columns(2)
    )

    with back_column:
        if st.button(
            "← Back to Upload",
            use_container_width=True
        ):
            go_to_page(
                "upload"
            )

    with result_column:
        if (
            "analysis_result"
            in st.session_state
        ):
            if st.button(
                "View Persona Result",
                type="primary",
                use_container_width=True
            ):
                go_to_page(
                    "result"
                )