from pathlib import Path

from analysis.pose_analyzer import PoseAnalyzer
from analysis.video_converter import convert_to_browser_mp4
from analysis.contact_pipeline import run_contact_analysis
from analysis.events_pipeline import run_contact_events
from analysis.step_pipeline import run_step_metrics


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = BASE_DIR / "videos"


def run_pipeline(
    input_path,
    fps=None
):
    """
    スプリント動画を一括分析する。

    動画
      ↓
    骨格解析
      ↓
    接地候補
      ↓
    接地イベント
      ↓
    ステップ分析
    """

    input_path = Path(
        input_path
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"動画がありません: {input_path}"
        )

    print("=" * 60)
    print("SprintAnalysisAI")
    print("一括分析開始")
    print("=" * 60)

    # ======================================================
    # 1. 骨格解析
    # ======================================================

    print()
    print("[1/4] 骨格解析")

    pose_output = (
        VIDEOS_DIR /
        "pose_analysis.mp4"
    )

    analyzer = PoseAnalyzer()

    pose_result = analyzer.analyze_video(
        str(input_path),
        str(pose_output)
    )

    print("骨格解析完了")

    # ======================================================
    # FPS取得
    # ======================================================

    if fps is None:

        if (
            isinstance(
                pose_result,
                dict
            )
            and
            "fps" in pose_result
        ):

            fps = float(
                pose_result["fps"]
            )

        else:

            fps = 30.0

    print(
        f"FPS: {fps:.2f}"
    )

    # ======================================================
    # ブラウザ用動画
    # ======================================================

    pose_browser = (
        VIDEOS_DIR /
        "pose_analysis_browser.mp4"
    )

    convert_to_browser_mp4(
        str(pose_output),
        str(pose_browser)
    )

    # ======================================================
    # 2. 接地候補
    # ======================================================

    print()
    print("[2/4] 接地候補検出")

    angle_history = (
        DATA_DIR /
        "angle_history.csv"
    )

    contact_result = (
        run_contact_analysis(
            angle_history,
            fps=fps
        )
    )

    print(
        "接地候補検出完了"
    )

    print(
        f"左: {contact_result['left_count']}"
    )

    print(
        f"右: {contact_result['right_count']}"
    )

    print(
        f"合計: {contact_result['total_count']}"
    )

    # ======================================================
    # 3. 接地イベント
    # ======================================================

    print()
    print("[3/4] 接地イベント確定")

    event_result = (
        run_contact_events()
    )

    print(
        "接地イベント確定完了"
    )

    print(
        f"イベント数: "
        f"{event_result['total_events']}"
    )

    print(
        f"左: "
        f"{event_result['left_events']}"
    )

    print(
        f"右: "
        f"{event_result['right_events']}"
    )

    # ======================================================
    # 4. ステップ分析
    # ======================================================

    print()
    print("[4/4] ステップ分析")

    step_result = (
        run_step_metrics()
    )

    print(
        "ステップ分析完了"
    )

    summary = (
        step_result["summary"]
        .iloc[0]
    )

    print()
    print(
        f"平均ステップ間隔: "
        f"{summary['average_step_interval_sec']:.3f} 秒"
    )

    print(
        f"ピッチ: "
        f"{summary['pitch_steps_per_sec']:.2f} steps/s"
    )

    print(
        f"ピッチ: "
        f"{summary['pitch_steps_per_min']:.1f} steps/min"
    )

    # ======================================================
    # 完了
    # ======================================================

    print()
    print("=" * 60)
    print("一括分析完了")
    print("=" * 60)

    return {
        "pose": pose_result,
        "contact": contact_result,
        "events": event_result,
        "steps": step_result
    }


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:

        print(
            "使用方法:"
        )

        print(
            "python analysis\\run_pipeline.py "
            "videos\\動画.mp4"
        )

        sys.exit(1)

    video_path = sys.argv[1]

    run_pipeline(
        video_path
    )