from pathlib import Path
import pandas as pd
import numpy as np


DATA_DIR = Path("data")


def safe_mean(series):
    """
    NaNを除外して平均値を計算する。
    """

    values = pd.to_numeric(
        series,
        errors="coerce"
    ).dropna()

    if len(values) == 0:
        return np.nan

    return float(values.mean())


def safe_std(series):
    """
    NaNを除外して標準偏差を計算する。
    """

    values = pd.to_numeric(
        series,
        errors="coerce"
    ).dropna()

    if len(values) < 2:
        return np.nan

    return float(values.std())


def calculate_angle_difference(left, right):
    """
    左右の角度差を度数で計算する。

    例:
        左膝 130°
        右膝 120°
        → 左右差 10°
    """

    left = pd.to_numeric(
        left,
        errors="coerce"
    )

    right = pd.to_numeric(
        right,
        errors="coerce"
    )

    return (
        left - right
    ).abs()


def calculate_normalized_difference(left, right):
    """
    左右差を平均角度に対して正規化する。

    これは評価点ではなく、
    左右差を別の角度指標と比較しやすくする
    補助指標として使用する。
    """

    left = pd.to_numeric(
        left,
        errors="coerce"
    )

    right = pd.to_numeric(
        right,
        errors="coerce"
    )

    mean_value = (
        left.abs() + right.abs()
    ) / 2

    result = (
        (left - right).abs()
        / mean_value
        * 100
    )

    return result.replace(
        [np.inf, -np.inf],
        np.nan
    )


def load_contact_form_data():
    """
    接地時フォームデータを読み込む。
    """

    path = (
        DATA_DIR /
        "contact_form_metrics.csv"
    )

    if not path.exists():

        raise FileNotFoundError(
            "data/contact_form_metrics.csv がありません。\n"
            "先に以下を実行してください。\n"
            "python -m research.contact_form_metrics"
        )

    df = pd.read_csv(path)

    if df.empty:

        raise ValueError(
            "contact_form_metrics.csv にデータがありません。"
        )

    return df


def calculate_form_metrics(df):
    """
    接地時フォームから評価用指標を計算する。
    """

    result = {}

    # ==================================================
    # 接地時角度
    # ==================================================

    result["left_knee_avg"] = safe_mean(
        df["left_knee"]
    )

    result["right_knee_avg"] = safe_mean(
        df["right_knee"]
    )

    result["left_hip_avg"] = safe_mean(
        df["left_hip"]
    )

    result["right_hip_avg"] = safe_mean(
        df["right_hip"]
    )

    result["left_ankle_avg"] = safe_mean(
        df["left_ankle"]
    )

    result["right_ankle_avg"] = safe_mean(
        df["right_ankle"]
    )

    result["left_thigh_avg"] = safe_mean(
        df["left_thigh_angle"]
    )

    result["right_thigh_avg"] = safe_mean(
        df["right_thigh_angle"]
    )

    result["trunk_angle_avg"] = safe_mean(
        df["trunk_angle"]
    )

    result["pelvis_angle_avg"] = safe_mean(
        df["pelvis_angle"]
    )

    # ==================================================
    # 左右角度差
    # ==================================================

    knee_difference = calculate_angle_difference(
        df["left_knee"],
        df["right_knee"]
    )

    hip_difference = calculate_angle_difference(
        df["left_hip"],
        df["right_hip"]
    )

    ankle_difference = calculate_angle_difference(
        df["left_ankle"],
        df["right_ankle"]
    )

    thigh_difference = calculate_angle_difference(
        df["left_thigh_angle"],
        df["right_thigh_angle"]
    )

    result["knee_difference_deg"] = safe_mean(
        knee_difference
    )

    result["hip_difference_deg"] = safe_mean(
        hip_difference
    )

    result["ankle_difference_deg"] = safe_mean(
        ankle_difference
    )

    result["thigh_difference_deg"] = safe_mean(
        thigh_difference
    )

    # ==================================================
    # 正規化左右差
    # ==================================================

    knee_normalized = calculate_normalized_difference(
        df["left_knee"],
        df["right_knee"]
    )

    hip_normalized = calculate_normalized_difference(
        df["left_hip"],
        df["right_hip"]
    )

    ankle_normalized = calculate_normalized_difference(
        df["left_ankle"],
        df["right_ankle"]
    )

    thigh_normalized = calculate_normalized_difference(
        df["left_thigh_angle"],
        df["right_thigh_angle"]
    )

    result[
        "knee_normalized_difference_pct"
    ] = safe_mean(
        knee_normalized
    )

    result[
        "hip_normalized_difference_pct"
    ] = safe_mean(
        hip_normalized
    )

    result[
        "ankle_normalized_difference_pct"
    ] = safe_mean(
        ankle_normalized
    )

    result[
        "thigh_normalized_difference_pct"
    ] = safe_mean(
        thigh_normalized
    )

    # ==================================================
    # 接地イベント数
    # ==================================================

    result["contact_event_count"] = len(df)

    # ==================================================
    # 有効データ数
    # ==================================================

    result["valid_knee_samples"] = (
        df[
            [
                "left_knee",
                "right_knee"
            ]
        ]
        .notna()
        .all(axis=1)
        .sum()
    )

    result["valid_hip_samples"] = (
        df[
            [
                "left_hip",
                "right_hip"
            ]
        ]
        .notna()
        .all(axis=1)
        .sum()
    )

    result["valid_ankle_samples"] = (
        df[
            [
                "left_ankle",
                "right_ankle"
            ]
        ]
        .notna()
        .all(axis=1)
        .sum()
    )

    result["valid_thigh_samples"] = (
        df[
            [
                "left_thigh_angle",
                "right_thigh_angle"
            ]
        ]
        .notna()
        .all(axis=1)
        .sum()
    )

    # ==================================================
    # データ品質
    # ==================================================

    result["data_quality"] = (
        "2D video pose analysis"
    )

    result["camera_plane"] = (
        "sagittal-plane oriented analysis"
    )

    result["measurement_confidence"] = (
        "video-based"
    )

    # ==================================================
    # 研究比較
    # ==================================================

    # 現段階では研究対象集団・速度・局面を
    # 揃えた基準値がないため一致率を計算しない。
    result["research_match_rate"] = np.nan

    result["research_match_status"] = (
        "研究対象集団・速度・局面を揃えた"
        "比較基準が未登録のため未計算"
    )

    return result


def save_result(result):
    """
    評価結果をCSVとして保存する。
    """

    output = pd.DataFrame(
        [result]
    )

    path = (
        DATA_DIR /
        "form_evaluation.csv"
    )

    output.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )

    return path


def print_result(result):
    """
    コンソールに結果を表示する。
    """

    print(
        "\n【接地時フォーム】"
    )

    print(
        f"左膝平均: "
        f"{result['left_knee_avg']:.2f} deg"
    )

    print(
        f"右膝平均: "
        f"{result['right_knee_avg']:.2f} deg"
    )

    print(
        f"左股関節平均: "
        f"{result['left_hip_avg']:.2f} deg"
    )

    print(
        f"右股関節平均: "
        f"{result['right_hip_avg']:.2f} deg"
    )

    print(
        f"左足関節平均: "
        f"{result['left_ankle_avg']:.2f} deg"
    )

    print(
        f"右足関節平均: "
        f"{result['right_ankle_avg']:.2f} deg"
    )

    print(
        f"左大腿角度平均: "
        f"{result['left_thigh_avg']:.2f} deg"
    )

    print(
        f"右大腿角度平均: "
        f"{result['right_thigh_avg']:.2f} deg"
    )

    print(
        f"体幹角度平均: "
        f"{result['trunk_angle_avg']:.2f} deg"
    )

    print(
        f"骨盤角度平均: "
        f"{result['pelvis_angle_avg']:.2f} deg"
    )

    print(
        "\n【左右角度差】"
    )

    print(
        f"膝左右差: "
        f"{result['knee_difference_deg']:.2f} deg"
    )

    print(
        f"股関節左右差: "
        f"{result['hip_difference_deg']:.2f} deg"
    )

    print(
        f"足関節左右差: "
        f"{result['ankle_difference_deg']:.2f} deg"
    )

    print(
        f"大腿左右差: "
        f"{result['thigh_difference_deg']:.2f} deg"
    )

    print(
        "\n【正規化左右差】"
    )

    print(
        f"膝: "
        f"{result['knee_normalized_difference_pct']:.2f}%"
    )

    print(
        f"股関節: "
        f"{result['hip_normalized_difference_pct']:.2f}%"
    )

    print(
        f"足関節: "
        f"{result['ankle_normalized_difference_pct']:.2f}%"
    )

    print(
        f"大腿: "
        f"{result['thigh_normalized_difference_pct']:.2f}%"
    )

    print(
        "\n【データ品質】"
    )

    print(
        f"接地イベント数: "
        f"{result['contact_event_count']}"
    )

    print(
        f"膝有効データ: "
        f"{result['valid_knee_samples']}"
    )

    print(
        f"股関節有効データ: "
        f"{result['valid_hip_samples']}"
    )

    print(
        f"足関節有効データ: "
        f"{result['valid_ankle_samples']}"
    )

    print(
        f"大腿有効データ: "
        f"{result['valid_thigh_samples']}"
    )

    print(
        "\n【研究比較】"
    )

    print(
        "研究一致率: 未計算"
    )

    print(
        result["research_match_status"]
    )


def run_form_evaluation():

    print("=" * 60)
    print("SprintAnalysisAI")
    print("フォーム評価エンジン")
    print("=" * 60)

    # データ読み込み
    df = load_contact_form_data()

    print(
        f"\n接地イベント数: {len(df)}"
    )

    # 指標計算
    result = calculate_form_metrics(
        df
    )

    # 結果表示
    print_result(
        result
    )

    # 保存
    output_path = save_result(
        result
    )

    print(
        f"\n保存先: {output_path}"
    )

    return result


if __name__ == "__main__":

    run_form_evaluation()