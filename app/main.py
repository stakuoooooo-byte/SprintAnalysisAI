import streamlit as st
from pathlib import Path
import sys
import subprocess
import pandas as pd
import imageio_ffmpeg


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
VIDEO_DIR = BASE_DIR / "videos"

DATA_DIR.mkdir(exist_ok=True)
VIDEO_DIR.mkdir(exist_ok=True)


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

st.caption(
    "スプリント映像 × 骨格解析 × 研究比較 × AI評価"
)


# ============================================================
# サイドバー
# ============================================================

st.sidebar.header("分析")

uploaded_file = st.sidebar.file_uploader(
    "スプリント動画をアップロード",
    type=["mp4", "mov", "avi", "m4v"]
)


# ============================================================
# 動画解析
# ============================================================

if uploaded_file is not None:

    st.subheader("🎥 アップロード動画")

    st.video(
        uploaded_file
    )

    if st.button(
        "🔬 分析開始",
        type="primary",
        use_container_width=True
    ):

        # ----------------------------------------------------
        # 動画保存
        # ----------------------------------------------------

        video_path = (
            VIDEO_DIR /
            uploaded_file.name
        )

        with open(
            video_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )


        # ----------------------------------------------------
        # プログレス
        # ----------------------------------------------------

        progress = st.progress(
            0
        )

        status = st.empty()


        # ====================================================
        # ① 骨格・接地・ステップ解析
        # ====================================================

        status.write(
            "① 骨格・接地・ステップ解析中..."
        )

        progress.progress(
            20
        )

        command = [
            sys.executable,
            "-m",
            "analysis.run_pipeline",
            str(video_path)
        ]

        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )


        if result.returncode != 0:

            st.error(
                "動画解析中にエラーが発生しました。"
            )

            st.code(
                result.stderr
            )

            st.stop()


        # ====================================================
        # ② 速度プロファイル
        # ====================================================

        status.write(
            "② 速度プロファイルを解析中..."
        )

        progress.progress(
            40
        )

        velocity_command = [
            sys.executable,
            "-m",
            "research.velocity_profile"
        ]

        velocity_result = subprocess.run(
            velocity_command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if velocity_result.returncode != 0:

            st.warning(
                "速度プロファイルの解析を完了できませんでした。"
            )


        # ====================================================
        # ③ 速度局面
        # ====================================================

        status.write(
            "③ 速度局面を分析中..."
        )

        progress.progress(
            50
        )

        phase_command = [
            sys.executable,
            "-m",
            "research.velocity_phase_detection"
        ]

        phase_result = subprocess.run(
            phase_command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if phase_result.returncode != 0:

            st.warning(
                "速度局面分析を完了できませんでした。"
            )


        # ====================================================
        # ④ 研究比較
        # ====================================================

        status.write(
            "④ 研究データと比較中..."
        )

        progress.progress(
            65
        )

        research_command = [
            sys.executable,
            "-m",
            "research.research_pipeline"
        ]

        research_result = subprocess.run(
            research_command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if research_result.returncode != 0:

            st.warning(
                "研究比較の一部を実行できませんでした。"
            )


        # ====================================================
        # ⑤ AI評価
        # ====================================================

        status.write(
            "⑤ AI評価を生成中..."
        )

        progress.progress(
            80
        )

        ai_command = [
            sys.executable,
            "-m",
            "research.ai_interpreter"
        ]

        ai_result = subprocess.run(
            ai_command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if ai_result.returncode != 0:

            st.warning(
                "AI評価の生成に失敗しました。"
            )


        # ====================================================
        # 完了
        # ====================================================

        progress.progress(
            100
        )

        status.success(
            "✅ 分析完了"
        )

        st.session_state[
            "analysis_completed"
        ] = True

        st.rerun()


# ============================================================
# 分析結果
# ============================================================

if st.session_state.get(
    "analysis_completed",
    False
):

    st.divider()

    st.header(
        "📊 分析結果"
    )


    # ========================================================
    # 基本パフォーマンス
    # ========================================================

    st.subheader(
        "⚡ パフォーマンス"
    )

    summary_file = (
        DATA_DIR /
        "performance_summary.csv"
    )

    if summary_file.exists():

        summary = pd.read_csv(
            summary_file
        )

        if not summary.empty:

            row = summary.iloc[0]

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "接地イベント",
                    f"{int(row['total_contact_events'])}"
                )

            with col2:

                st.metric(
                    "ピッチ",
                    f"{row['pitch_steps_per_sec']:.2f} steps/s"
                )

            with col3:

                st.metric(
                    "平均1歩時間",
                    f"{row['average_step_interval_sec']:.3f} 秒"
                )

            with col4:

                st.metric(
                    "左右時間差",
                    f"{abs(row['left_right_difference_sec']):.3f} 秒"
                )

    else:

        st.warning(
            "performance_summary.csv がありません。"
        )


    # ========================================================
    # フォーム
    # ========================================================

    st.subheader(
        "🦵 フォーム分析"
    )

    form_file = (
        DATA_DIR /
        "form_evaluation.csv"
    )

    if form_file.exists():

        form = pd.read_csv(
            form_file
        )

        if not form.empty:

            row = form.iloc[0]

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "左膝角度",
                    f"{row['left_knee_avg']:.1f}°"
                )

            with col2:

                st.metric(
                    "右膝角度",
                    f"{row['right_knee_avg']:.1f}°"
                )

            with col3:

                st.metric(
                    "左股関節角度",
                    f"{row['left_hip_avg']:.1f}°"
                )

            with col4:

                st.metric(
                    "右股関節角度",
                    f"{row['right_hip_avg']:.1f}°"
                )

            st.info(
                "角度は2D動画骨格から取得した測定値です。"
                "単一の角度だけでフォームの良否を断定しません。"
            )

    else:

        st.warning(
            "form_evaluation.csv がありません。"
        )


    # ========================================================
    # 研究比較
    # ========================================================

    st.subheader(
        "📚 研究比較"
    )

    research_file = (
        DATA_DIR /
        "research_metric_comparison.csv"
    )

    if research_file.exists():

        research = pd.read_csv(
            research_file
        )

        if not research.empty:

            display_columns = []

            possible_columns = [
                "metric",
                "measured_mean",
                "measured_sd",
                "research_reference_count",
                "interpretation_status"
            ]

            for column in possible_columns:

                if column in research.columns:

                    display_columns.append(
                        column
                    )

            if display_columns:

                st.dataframe(
                    research[
                        display_columns
                    ],
                    use_container_width=True,
                    hide_index=True
                )

    else:

        st.warning(
            "research_metric_comparison.csv がありません。"
        )


    # ========================================================
    # 速度局面
    # ========================================================

    st.subheader(
        "📈 速度局面"
    )

    velocity_phase_file = (
        DATA_DIR /
        "velocity_phase_detection.csv"
    )

    if velocity_phase_file.exists():

        velocity_phase = pd.read_csv(
            velocity_phase_file
        )

        if not velocity_phase.empty:

            display_columns = []

            for column in [
                "phase_group",
                "phase_candidate",
                "relative_position",
                "normalized_relative_speed",
                "velocity_change_state"
            ]:

                if column in velocity_phase.columns:

                    display_columns.append(
                        column
                    )

            if display_columns:

                st.dataframe(
                    velocity_phase[
                        display_columns
                    ],
                    use_container_width=True,
                    hide_index=True
                )

            st.caption(
                "※速度局面は動画内の相対的な速度変化による候補分類です。"
                "最大速度局面を直接証明するものではありません。"
            )

    else:

        st.info(
            "速度局面データはまだありません。"
        )


    # ========================================================
    # AI評価
    # ========================================================

    st.subheader(
        "🤖 AIフォーム評価"
    )

    ai_file = (
        DATA_DIR /
        "ai_evaluation.csv"
    )

    if ai_file.exists():

        ai = pd.read_csv(
            ai_file
        )

        if not ai.empty:

            for _, row in ai.iterrows():

                with st.container(
                    border=True
                ):

                    metric_name = str(
                        row.get(
                            "metric",
                            "評価項目"
                        )
                    )

                    st.markdown(
                        f"### {metric_name}"
                    )

                    if "finding" in row:

                        st.markdown(
                            "**観測結果**"
                        )

                        st.write(
                            row["finding"]
                        )

                    if "research_interpretation" in row:

                        st.markdown(
                            "**研究上の解釈**"
                        )

                        st.write(
                            row[
                                "research_interpretation"
                            ]
                        )

                    if "improvement_point" in row:

                        st.markdown(
                            "**改善ポイント**"
                        )

                        st.write(
                            row[
                                "improvement_point"
                            ]
                        )

                    if "recommended_drill" in row:

                        st.markdown(
                            "**推奨ドリル**"
                        )

                        st.write(
                            row[
                                "recommended_drill"
                            ]
                        )

        else:

            st.info(
                "AI評価データがありません。"
            )

    else:

        st.info(
            "AI評価データがまだありません。"
        )


    # ========================================================
    # 骨格解析動画
    # ========================================================

    st.subheader(
        "🎥 骨格解析動画"
    )

    analysis_video = (
        VIDEO_DIR /
        "pose_analysis.mp4"
    )

    if analysis_video.exists():

        browser_video = (
            VIDEO_DIR /
            "pose_analysis_h264.mp4"
        )

        # ----------------------------------------------------
        # FMP4 → H.264変換
        # ----------------------------------------------------

        if not browser_video.exists():

            with st.spinner(
                "ブラウザ再生用動画を作成しています..."
            ):

                ffmpeg = (
                    imageio_ffmpeg
                    .get_ffmpeg_exe()
                )

                command = [
                    ffmpeg,
                    "-y",
                    "-i",
                    str(analysis_video),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "fast",
                    "-crf",
                    "23",
                    "-pix_fmt",
                    "yuv420p",
                    "-an",
                    "-movflags",
                    "+faststart",
                    str(browser_video)
                ]

                conversion = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )

                if conversion.returncode != 0:

                    st.error(
                        "ブラウザ用動画への変換に失敗しました。"
                    )

                    st.code(
                        conversion.stderr
                    )

                    st.stop()

        # ----------------------------------------------------
        # H.264動画をStreamlitへ渡す
        # ----------------------------------------------------

        with open(
            browser_video,
            "rb"
        ) as video_file:

            video_bytes = video_file.read()

        st.video(
            video_bytes
        )

    else:

        st.warning(
            "pose_analysis.mp4 がありません。"
        )


# ============================================================
# 初期画面
# ============================================================

else:

    st.info(
        "左側からスプリント動画をアップロードしてください。"
    )

    st.markdown(
        """
        ### SprintAnalysisAIでできること

        **動画解析**
        - 🦴 骨格解析
        - 👣 接地イベント解析
        - 📈 ピッチ・1歩時間分析
        - 📐 膝・股関節・足首・体幹分析

        **研究分析**
        - 📚 研究データベースとの比較
        - 📊 研究比較候補の抽出
        - 📈 速度局面分析

        **AI評価**
        - 🤖 フォームの解釈
        - 💡 改善ポイント
        - 🏃 推奨ドリル
        """
    )