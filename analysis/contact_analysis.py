import streamlit as st
import pandas as pd
import os

from contact_detector import ContactDetector


st.set_page_config(
    page_title="Sprint Contact Analysis",
    page_icon="🦶",
    layout="wide"
)

st.title("🦶 Sprint Contact Analysis")

st.write(
    "足首の動きから接地候補を検出します。"
)


# =====================================
# CSV読み込み
# =====================================

uploaded_file = st.file_uploader(
    "angle_history.csvを選択してください",
    type=["csv"]
)


if uploaded_file is None:

    st.info(
        "angle_history.csvをアップロードしてください。"
    )

    st.stop()


df = pd.read_csv(
    uploaded_file
)


st.success(
    "骨格データを読み込みました。"
)


# =====================================
# 必要な列
# =====================================

required_columns = [

    "frame",

    "left_ankle_x",
    "left_ankle_y",

    "right_ankle_x",
    "right_ankle_y"
]


missing_columns = [

    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "必要な列がありません。"
    )

    st.write(
        missing_columns
    )

    st.stop()


# =====================================
# FPS
# =====================================

fps = st.number_input(
    "動画FPS",
    min_value=1.0,
    max_value=240.0,
    value=30.0,
    step=1.0
)


# =====================================
# 接地検出
# =====================================

detector = ContactDetector(
    fps=fps
)


result = detector.analyze(
    df
)


left_contacts = result[
    "left"
].copy()


right_contacts = result[
    "right"
].copy()


# =====================================
# 左右結合
# =====================================

contact_candidates = pd.concat(
    [
        left_contacts,
        right_contacts
    ],
    ignore_index=True
)


# =====================================
# 時系列順
# =====================================

if not contact_candidates.empty:

    contact_candidates = (
        contact_candidates
        .sort_values(
            "time_sec"
        )
        .reset_index(
            drop=True
        )
    )


    contact_candidates.insert(
        0,
        "candidate",
        range(
            1,
            len(contact_candidates) + 1
        )
    )


# =====================================
# 保存
# =====================================

os.makedirs(
    "data",
    exist_ok=True
)


candidate_path = (
    "data/contact_candidates.csv"
)


contact_candidates.to_csv(
    candidate_path,
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 結果
# =====================================

st.subheader(
    "🦶 接地候補"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "左足候補",
        len(left_contacts)
    )


with col2:

    st.metric(
        "右足候補",
        len(right_contacts)
    )


with col3:

    st.metric(
        "合計候補",
        len(contact_candidates)
    )


# =====================================
# データ表示
# =====================================

if contact_candidates.empty:

    st.warning(
        "接地候補が検出されませんでした。"
    )

else:

    st.dataframe(
        contact_candidates,
        use_container_width=True
    )


# =====================================
# 足首グラフ
# =====================================

st.subheader(
    "📈 足首の上下動"
)


ankle_graph = df[
    [
        "frame",
        "left_ankle_y",
        "right_ankle_y"
    ]
].set_index(
    "frame"
)


st.line_chart(
    ankle_graph,
    use_container_width=True
)


# =====================================
# ダウンロード
# =====================================

if not contact_candidates.empty:

    csv_data = contact_candidates.to_csv(
        index=False
    ).encode(
        "utf-8-sig"
    )


    st.download_button(
        label="接地候補CSVをダウンロード",
        data=csv_data,
        file_name="contact_candidates.csv",
        mime="text/csv"
    )


st.success(
    f"接地候補を {candidate_path} に保存しました。"
)