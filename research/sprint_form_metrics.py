from pathlib import Path
import pandas as pd


DATA_DIR = Path("data")


def load_data():
    """SprintAnalysisAIの既存分析データを読み込む"""

    angle_path = DATA_DIR / "angle_history.csv"
    contact_angle_path = DATA_DIR / "contact_angle_analysis.csv"
    stride_path = DATA_DIR / "stride_analysis.csv"
    step_path = DATA_DIR / "step_metrics.csv"

    data = {}

    if angle_path.exists():
        data["angle_history"] = pd.read_csv(angle_path)

    if contact_angle_path.exists():
        data["contact_angle"] = pd.read_csv(contact_angle_path)

    if stride_path.exists():
        data["stride"] = pd.read_csv(stride_path)

    if step_path.exists():
        data["step_metrics"] = pd.read_csv(step_path)

    return data


def extract_basic_metrics(data):
    """
    現在取得できているデータから、
    スプリントフォーム評価に利用できる基本指標を抽出する。
    """

    metrics = {}

    # -------------------------
    # ステップ関連
    # -------------------------
    if "step_metrics" in data:
        df = data["step_metrics"]

        if len(df) > 0:
            row = df.iloc[0]

            columns = {
                "total_contact_events": "total_contact_events",
                "left_contact_events": "left_contact_events",
                "right_contact_events": "right_contact_events",
                "average_step_interval_sec": "average_step_interval_sec",
                "minimum_step_interval_sec": "minimum_step_interval_sec",
                "maximum_step_interval_sec": "maximum_step_interval_sec",
                "pitch_steps_per_sec": "pitch_steps_per_sec",
                "pitch_steps_per_min": "pitch_steps_per_min",
                "left_average_contact_interval_sec":
                    "left_average_contact_interval_sec",
                "right_average_contact_interval_sec":
                    "right_average_contact_interval_sec",
                "left_right_difference_sec":
                    "left_right_difference_sec",
                "left_right_ratio":
                    "left_right_ratio",
            }

            for output_name, column_name in columns.items():
                if column_name in df.columns:
                    metrics[output_name] = float(row[column_name])

    # -------------------------
    # 接地時の関節角度
    # -------------------------
    if "contact_angle" in data:
        df = data["contact_angle"]

        if len(df) > 0:
            for column in [
                "contact_knee_angle_avg",
                "contact_hip_angle_avg",
                "contact_ankle_angle_avg",
                "left_knee_angle_avg",
                "left_hip_angle_avg",
                "left_ankle_angle_avg",
                "right_knee_angle_avg",
                "right_hip_angle_avg",
                "right_ankle_angle_avg",
            ]:
                if column in df.columns:
                    metrics[column] = float(df[column].iloc[0])

    # -------------------------
    # ストライド
    # -------------------------
    if "stride" in data:
        df = data["stride"]

        if len(df) > 0:
            for column in [
                "average_stride_time_sec",
                "left_stride_image_displacement",
                "right_stride_image_displacement",
            ]:
                if column in df.columns:
                    metrics[column] = float(df[column].iloc[0])

    return metrics


def build_evaluation_input(metrics):
    """
    AI評価に渡すための整理されたデータを作る。
    """

    evaluation = {
        "step_metrics": {},
        "contact_angles": {},
        "stride_metrics": {},
        "data_quality": {},
    }

    # ステップ
    for key in [
        "average_step_interval_sec",
        "minimum_step_interval_sec",
        "maximum_step_interval_sec",
        "pitch_steps_per_sec",
        "pitch_steps_per_min",
        "left_average_contact_interval_sec",
        "right_average_contact_interval_sec",
        "left_right_difference_sec",
        "left_right_ratio",
    ]:
        if key in metrics:
            evaluation["step_metrics"][key] = metrics[key]

    # 接地角度
    for key in [
        "contact_knee_angle_avg",
        "contact_hip_angle_avg",
        "contact_ankle_angle_avg",
        "left_knee_angle_avg",
        "left_hip_angle_avg",
        "left_ankle_angle_avg",
        "right_knee_angle_avg",
        "right_hip_angle_avg",
        "right_ankle_angle_avg",
    ]:
        if key in metrics:
            evaluation["contact_angles"][key] = metrics[key]

    # ストライド
    for key in [
        "average_stride_time_sec",
        "left_stride_image_displacement",
        "right_stride_image_displacement",
    ]:
        if key in metrics:
            evaluation["stride_metrics"][key] = metrics[key]

    # データ品質
    evaluation["data_quality"] = {
        "measurement_type": "2D video pose analysis",
        "camera_plane": "sagittal-plane oriented analysis",
        "research_comparison_status":
            "Research comparison requires phase-specific reference data",
        "absolute_distance_status":
            "Current image displacement is not absolute meter distance",
    }

    return evaluation


def run_form_metrics():
    """フォーム評価用データを作成"""

    data = load_data()

    if not data:
        raise FileNotFoundError(
            "分析データが見つかりません。"
        )

    metrics = extract_basic_metrics(data)
    evaluation = build_evaluation_input(metrics)

    return evaluation


if __name__ == "__main__":
    result = run_form_metrics()

    print("=" * 50)
    print("SprintAnalysisAI")
    print("研究ベースフォーム評価データ")
    print("=" * 50)

    for category, values in result.items():
        print(f"\n[{category}]")

        if isinstance(values, dict):
            for key, value in values.items():
                print(f"{key}: {value}")
        else:
            print(values)