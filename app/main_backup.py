import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# パス設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = BASE_DIR / "videos"
ANALYSIS_DIR = BASE_DIR / "analysis"

sys.path.insert(0, str(BASE_DIR))


# ============================================================
# 分析モジュール
# ============================================================

from analysis.sprint_timer import calculate_time, calculate_speed
from analysis.pose_analyzer import PoseAnalyzer
from analysis.video_converter import convert_to_browser_mp4


# ============================================================
# Streamlit設定
# ============================================================

st.set_page_config(
    page_title="SprintAnalysisAI",
    page_icon="🏃",
    layout="wide"
)


# ============================================================
# タイトル
# ============================================================

st.title("🏃 SprintAnalysisAI")

st.write(
    "スプリント映像から、タイム・ピッチ・接地・角度・"
    "フォーム情報を分析します。"
)


# ============================================================
# 動画選択
# ============================================================

st.header("🎥 動画")

video_files = sorted(
    [
        f for f in os.listdir(VIDEOS_DIR)
        if f.lower().endswith(
            (".mp4", ".mov", ".avi", ".mkv")
        )
        and "analysis" not in f.lower()
    ]
)


if not video_files:

    st.warning(
        "videosフォルダに分析対象の動画がありません。"
    )

    st.stop()


selected_video = st.selectbox(
    "分析する動画を選択",
    video_files
)


input_path = str(
    VIDEOS_DIR / selected_video
)


st.write(
    f"選択中: `{selected_video}`"
)


if os.path.exists(input_path):

    st.video(input_path)


# ============================================================
# 50mスプリントタイム
# ============================================================

st.divider()

st.header("⏱ 50mスプリントタイム")


st.write(
    "動画上のスタートフレームとゴールフレームを指定して、"
    "スプリントタイムを計測します。"
)


if "start_frame" not in st.session_state:
    st.session_state.start_frame = None


if "end_frame" not in st.session_state:
    st.session_state.end_frame = None


frame_number = st.number_input(
    "フレーム番号",
    min_value=0,
    value=0,
    step=1
)


col1, col2 = st.columns(2)


with col1:

    if st.button(
        "▶ 現在のフレームをスタートに設定"
    ):

        st.session_state.start_frame = int(
            frame_number
        )

        st.success(
            f"スタート: Frame {frame_number}"
        )


with col2:

    if st.button(
        "🏁 現在のフレームをゴールに設定"
    ):

        st.session_state.end_frame = int(
            frame_number
        )

        st.success(
            f"ゴール: Frame {frame_number}"
        )


start_frame = st.session_state.start_frame
end_frame = st.session_state.end_frame


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "スタートフレーム",
        "-" if start_frame is None else start_frame
    )


with col2:

    st.metric(
        "ゴールフレーム",
        "-" if end_frame is None else end_frame
    )


distance_m = st.number_input(
    "走行距離（m）",
    min_value=1.0,
    value=50.0,
    step=1.0
)


if (
    start_frame is not None
    and end_frame is not None
):

    if end_frame <= start_frame:

        st.error(
            "ゴールフレームはスタートフレームより後にしてください。"
        )

    else:

        if st.button(
            "⏱ タイムを計測"
        ):

            try:

                result = calculate_time(
                    input_path,
                    int(start_frame),
                    int(end_frame)
                )

                sprint_time = result["time_sec"]

                average_speed = calculate_speed(
                    distance_m,
                    sprint_time
                )


                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "タイム",
                        f"{sprint_time:.3f} 秒"
                    )


                with col2:

                    st.metric(
                        "平均速度",
                        f"{average_speed:.2f} m/s"
                    )


                with col3:

                    st.metric(
                        "距離",
                        f"{distance_m:.1f} m"
                    )


                # セッションに保存
                st.session_state.sprint_time = sprint_time
                st.session_state.average_speed = average_speed


            except Exception as e:

                st.error(
                    "タイム計測中にエラーが発生しました。"
                )

                st.exception(e)


else:

    st.info(
        "スタートとゴールのフレームを設定してください。"
    )


# ============================================================
# 骨格解析
# ============================================================

st.divider()

st.header("🦴 骨格解析")


pose_output_path = str(
    VIDEOS_DIR / "pose_analysis.mp4"
)

pose_browser_path = str(
    VIDEOS_DIR / "pose_analysis_browser.mp4"
)


if st.button(
    "🦴 骨格解析を実行"
):

    try:

        with st.spinner(
            "骨格解析を実行しています..."
        ):

            analyzer = PoseAnalyzer()

            result = analyzer.analyze_video(
                input_path,
                pose_output_path
            )


        with st.spinner(
            "ブラウザ用動画を作成しています..."
        ):

            convert_to_browser_mp4(
                pose_output_path,
                pose_browser_path
            )


        st.success(
            "骨格解析が完了しました。"
        )


        if result is not None:

            col1, col2, col3 = st.columns(3)


            with col1:

                if "fps" in result:

                    st.metric(
                        "FPS",
                        f"{result['fps']:.2f}"
                    )


            with col2:

                if "frames" in result:

                    st.metric(
                        "フレーム数",
                        result["frames"]
                    )


            with col3:

                if (
                    "width" in result
                    and
                    "height" in result
                ):

                    st.metric(
                        "解像度",
                        f"{result['width']} × "
                        f"{result['height']}"
                    )


    except Exception as e:

        st.error(
            "骨格解析中にエラーが発生しました。"
        )

        st.exception(e)


if os.path.exists(pose_browser_path):

    st.subheader(
        "🎥 骨格解析動画"
    )

    with open(
        pose_browser_path,
        "rb"
    ) as f:

        st.video(
            f.read(),
            format="video/mp4"
        )


# ============================================================
# 総合分析
# ============================================================

st.divider()

st.header("📊 スプリント総合分析")


summary_path = (
    DATA_DIR / "performance_summary.csv"
)


if summary_path.exists():

    try:

        summary_df = pd.read_csv(
            summary_path
        )


        if len(summary_df) > 0:

            summary = summary_df.iloc[0]


            # ==================================================
            # タイム・速度
            # ==================================================

            st.subheader(
                "🏃 パフォーマンス"
            )


            performance_col1, performance_col2 = (
                st.columns(2)
            )


            with performance_col1:

                if (
                    "sprint_time"
                    in st.session_state
                ):

                    st.metric(
                        "50mタイム",
                        f"{st.session_state.sprint_time:.3f} 秒"
                    )

                else:

                    st.info(
                        "タイム計測を行うと表示されます。"
                    )


            with performance_col2:

                if (
                    "average_speed"
                    in st.session_state
                ):

                    st.metric(
                        "平均速度",
                        f"{st.session_state.average_speed:.2f} m/s"
                    )

                else:

                    st.info(
                        "タイム計測を行うと表示されます。"
                    )


            # ==================================================
            # ピッチ
            # ==================================================

            st.subheader(
                "👣 ピッチ・ステップ"
            )


            col1, col2, col3, col4 = (
                st.columns(4)
            )


            with col1:

                st.metric(
                    "接地イベント",
                    int(
                        summary[
                            "total_contact_events"
                        ]
                    )
                )


            with col2:

                st.metric(
                    "ピッチ",
                    f"{summary['pitch_steps_per_sec']:.2f}"
                    " steps/s"
                )


            with col3:

                st.metric(
                    "ピッチ",
                    f"{summary['pitch_steps_per_min']:.1f}"
                    " steps/min"
                )


            with col4:

                st.metric(
                    "平均ステップ間隔",
                    f"{summary['average_step_interval_sec']:.3f}"
                    " 秒"
                )


            # ==================================================
            # ステップ時間
            # ==================================================

            st.subheader(
                "🔄 ステップ時間"
            )


            col1, col2, col3 = (
                st.columns(3)
            )


            with col1:

                st.metric(
                    "最短ステップ間隔",
                    f"{summary['minimum_step_interval_sec']:.3f}"
                    " 秒"
                )


            with col2:

                st.metric(
                    "最長ステップ間隔",
                    f"{summary['maximum_step_interval_sec']:.3f}"
                    " 秒"
                )


            with col3:

                st.metric(
                    "平均ストライド時間",
                    f"{summary['average_stride_time_sec']:.3f}"
                    " 秒"
                )


            # ==================================================
            # 左右バランス
            # ==================================================

            st.subheader(
                "⚖️ 左右バランス"
            )


            col1, col2, col3, col4 = (
                st.columns(4)
            )


            with col1:

                st.metric(
                    "左脚接地",
                    int(
                        summary[
                            "left_contact_events"
                        ]
                    )
                )


            with col2:

                st.metric(
                    "右脚接地",
                    int(
                        summary[
                            "right_contact_events"
                        ]
                    )
                )


            with col3:

                st.metric(
                    "左→左",
                    f"{summary['left_average_contact_interval_sec']:.3f}"
                    " 秒"
                )


            with col4:

                st.metric(
                    "右→右",
                    f"{summary['right_average_contact_interval_sec']:.3f}"
                    " 秒"
                )


            st.metric(
                "左右接地間隔差",
                f"{summary['left_right_difference_sec']:.3f} 秒"
            )


            # ==================================================
            # 接地時角度
            # ==================================================

            st.subheader(
                "📐 接地時角度"
            )


            col1, col2, col3 = (
                st.columns(3)
            )


            with col1:

                st.metric(
                    "膝関節",
                    f"{summary['contact_knee_angle_avg']:.1f}°"
                )


            with col2:

                st.metric(
                    "股関節",
                    f"{summary['contact_hip_angle_avg']:.1f}°"
                )


            with col3:

                st.metric(
                    "足関節",
                    f"{summary['contact_ankle_angle_avg']:.1f}°"
                )


            # ==================================================
            # 左右角度比較
            # ==================================================

            st.subheader(
                "↔️ 左右の接地時角度"
            )


            comparison_df = pd.DataFrame(
                {
                    "関節": [
                        "膝関節",
                        "股関節",
                        "足関節"
                    ],

                    "左脚": [
                        summary[
                            "left_knee_angle_avg"
                        ],

                        summary[
                            "left_hip_angle_avg"
                        ],

                        summary[
                            "left_ankle_angle_avg"
                        ]
                    ],

                    "右脚": [
                        summary[
                            "right_knee_angle_avg"
                        ],

                        summary[
                            "right_hip_angle_avg"
                        ],

                        summary[
                            "right_ankle_angle_avg"
                        ]
                    ]
                }
            )


            st.dataframe(
                comparison_df.round(2),
                use_container_width=True,
                hide_index=True
            )


            # ==================================================
            # 詳細データ
            # ==================================================

            with st.expander(
                "📋 総合分析データを表示"
            ):

                display_summary = (
                    summary_df.T
                )

                display_summary.columns = [
                    "値"
                ]

                st.dataframe(
                    display_summary,
                    use_container_width=True
                )


            # ==================================================
            # CSVダウンロード
            # ==================================================

            st.download_button(
                "⬇️ 総合分析CSVをダウンロード",

                data=summary_df.to_csv(
                    index=False,
                    encoding="utf-8-sig"
                ),

                file_name=(
                    "performance_summary.csv"
                ),

                mime="text/csv"
            )


    except Exception as e:

        st.error(
            "総合分析データを読み込めませんでした。"
        )

        st.exception(e)


else:

    st.info(
        "performance_summary.csv がありません。"
        "先に performance_summary.py を実行してください。"
    )


# ============================================================
# 接地イベント
# ============================================================

st.divider()

st.header("🦶 接地イベント")


contact_path = (
    DATA_DIR / "contact_events.csv"
)


if contact_path.exists():

    contact_df = pd.read_csv(
        contact_path
    )


    st.dataframe(
        contact_df,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "contact_events.csv がありません。"
    )


# ============================================================
# 接地イベント動画
# ============================================================

st.subheader(
    "🎥 接地イベント分析動画"
)


event_video_path = (
    VIDEOS_DIR /
    "contact_events_analysis_browser.mp4"
)


if event_video_path.exists():

    st.video(
        str(event_video_path)
    )

else:

    st.info(
        "接地イベント分析動画がありません。"
    )


# ============================================================
# 接地時角度詳細
# ============================================================

st.divider()

st.header(
    "📐 接地時角度の詳細"
)


contact_angle_path = (
    DATA_DIR /
    "contact_angle_analysis.csv"
)


if contact_angle_path.exists():

    angle_df = pd.read_csv(
        contact_angle_path
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        st.metric(
            "膝角度",
            f"{angle_df['contact_knee_angle'].mean():.2f}°"
        )


    with col2:

        st.metric(
            "股関節角度",
            f"{angle_df['contact_hip_angle'].mean():.2f}°"
        )


    with col3:

        st.metric(
            "足関節角度",
            f"{angle_df['contact_ankle_angle'].mean():.2f}°"
        )


    st.subheader(
        "膝関節角度の推移"
    )


    knee_chart = (
        angle_df[
            [
                "event",
                "contact_knee_angle"
            ]
        ]
        .set_index("event")
    )


    st.line_chart(
        knee_chart,
        use_container_width=True
    )


    st.subheader(
        "股関節角度の推移"
    )


    hip_chart = (
        angle_df[
            [
                "event",
                "contact_hip_angle"
            ]
        ]
        .set_index("event")
    )


    st.line_chart(
        hip_chart,
        use_container_width=True
    )


    st.subheader(
        "足関節角度の推移"
    )


    ankle_chart = (
        angle_df[
            [
                "event",
                "contact_ankle_angle"
            ]
        ]
        .set_index("event")
    )


    st.line_chart(
        ankle_chart,
        use_container_width=True
    )


    st.subheader(
        "接地イベント詳細"
    )


    display_df = angle_df[
        [
            "event",
            "frame",
            "time_sec",
            "side",
            "contact_knee_angle",
            "contact_hip_angle",
            "contact_ankle_angle"
        ]
    ].copy()


    display_df.columns = [
        "イベント",
        "フレーム",
        "時間",
        "脚",
        "膝角度",
        "股関節角度",
        "足関節角度"
    ]


    st.dataframe(
        display_df.round(2),
        use_container_width=True,
        hide_index=True
    )


    st.download_button(
        "⬇️ 接地角度CSVをダウンロード",

        data=angle_df.to_csv(
            index=False,
            encoding="utf-8-sig"
        ),

        file_name=(
            "contact_angle_analysis.csv"
        ),

        mime="text/csv"
    )


else:

    st.info(
        "contact_angle_analysis.csv がありません。"
    )


# ============================================================
# 骨格解析履歴
# ============================================================

st.divider()

st.header(
    "🦴 フレームごとの角度データ"
)


angle_history_path = (
    DATA_DIR /
    "angle_history.csv"
)


if angle_history_path.exists():

    angle_history_df = pd.read_csv(
        angle_history_path
    )


    st.dataframe(
        angle_history_df.head(100),
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "angle_history.csv がありません。"
    )


# ============================================================
# フッター
# ============================================================

st.divider()

st.caption(
    "SprintAnalysisAI"
)