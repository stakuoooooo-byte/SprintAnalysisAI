import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Sprint Step Analysis",
    page_icon="🏃",
    layout="wide"
)

st.title("🏃 Sprint Step Analysis")

st.write(
    "関節角度から走動作の周期を推定します。"
)


uploaded_file = st.file_uploader(
    "角度データCSVを選択してください",
    type=["csv"]
)


if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success("角度データを読み込みました。")

    # =====================================
    # 基本設定
    # =====================================

    fps = 30.0

    if "fps" in df.columns:
        fps = float(df["fps"].iloc[0])

    smooth_window = st.slider(
        "平滑化の強さ",
        min_value=3,
        max_value=15,
        value=5,
        step=2
    )

    # =====================================
    # 膝角度を平滑化
    # =====================================

    df["left_knee_smooth"] = (
        df["left_knee"]
        .rolling(
            window=smooth_window,
            center=True,
            min_periods=1
        )
        .mean()
    )

    df["right_knee_smooth"] = (
        df["right_knee"]
        .rolling(
            window=smooth_window,
            center=True,
            min_periods=1
        )
        .mean()
    )

    # =====================================
    # 膝角度グラフ
    # =====================================

    st.subheader("🦵 膝角度")

    knee_df = df[
        [
            "frame",
            "left_knee_smooth",
            "right_knee_smooth"
        ]
    ].set_index("frame")

    st.line_chart(
        knee_df,
        use_container_width=True
    )

    # =====================================
    # 左右の膝の谷を検出
    # =====================================

    left_points = []
    right_points = []

    for i in range(1, len(df) - 1):

        left_prev = df.loc[i - 1, "left_knee_smooth"]
        left_now = df.loc[i, "left_knee_smooth"]
        left_next = df.loc[i + 1, "left_knee_smooth"]

        right_prev = df.loc[i - 1, "right_knee_smooth"]
        right_now = df.loc[i, "right_knee_smooth"]
        right_next = df.loc[i + 1, "right_knee_smooth"]

        if (
            left_now < left_prev
            and left_now < left_next
        ):
            left_points.append(i)

        if (
            right_now < right_prev
            and right_now < right_next
        ):
            right_points.append(i)

    # =====================================
    # 近すぎる点を削除
    # =====================================

    def filter_points(points, minimum_distance=8):

        filtered = []

        for point in points:

            if not filtered:
                filtered.append(point)
                continue

            if point - filtered[-1] >= minimum_distance:

                filtered.append(point)

        return filtered


    left_points = filter_points(left_points)
    right_points = filter_points(right_points)

    # =====================================
    # 推定歩数
    # =====================================

    total_steps = (
        len(left_points)
        + len(right_points)
    )

    # =====================================
    # 推定ピッチ
    # =====================================

    duration_seconds = len(df) / fps

    if duration_seconds > 0:

        estimated_pitch = (
            total_steps / duration_seconds
        )

    else:

        estimated_pitch = 0

    # =====================================
    # 結果表示
    # =====================================

    st.subheader("📊 走動作の推定結果")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "左側の周期",
            len(left_points)
        )

    with col2:

        st.metric(
            "右側の周期",
            len(right_points)
        )

    with col3:

        st.metric(
            "推定ピッチ",
            f"{estimated_pitch:.2f} steps/s"
        )

    st.caption(
        "※膝角度の谷を利用した簡易推定です。"
        "接地・離地そのものを直接検出した値ではありません。"
    )

    # =====================================
    # 検出位置
    # =====================================

    st.subheader("🔎 周期検出位置")

    if left_points:

        left_result = pd.DataFrame({
            "frame": left_points,
            "time_sec": [
                frame / fps
                for frame in left_points
            ],
            "side": "left"
        })

        st.write("左側")
        st.dataframe(
            left_result,
            use_container_width=True
        )

    if right_points:

        right_result = pd.DataFrame({
            "frame": right_points,
            "time_sec": [
                frame / fps
                for frame in right_points
            ],
            "side": "right"
        })

        st.write("右側")
        st.dataframe(
            right_result,
            use_container_width=True
        )