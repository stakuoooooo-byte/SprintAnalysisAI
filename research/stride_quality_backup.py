import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 1歩ごとの品質・変化量分析
# ============================================================

DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
)

INPUT_FILE = (
    DATA_DIR /
    "stride_phase_metrics.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "stride_quality.csv"
)


# ============================================================
# 設定
# ============================================================

# 1歩時間
# これを超えるものは極端な外れ値候補として扱う
MIN_STRIDE_TIME = 0.15
MAX_STRIDE_TIME = 0.35


# ============================================================
# データ読み込み
# ============================================================

def load_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"{INPUT_FILE} がありません。"
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    if df.empty:

        raise ValueError(
            "stride_phase_metrics.csv が空です。"
        )

    return df


# ============================================================
# 数値化
# ============================================================

def convert_numeric(
    df
):

    numeric_columns = [

        "stride_time_sec",

        "previous_left_knee",
        "current_left_knee",

        "previous_right_knee",
        "current_right_knee",

        "previous_left_hip",
        "current_left_hip",

        "previous_right_hip",
        "current_right_hip",

        "previous_left_ankle",
        "current_left_ankle",

        "previous_right_ankle",
        "current_right_ankle",

        "previous_left_thigh_angle",
        "current_left_thigh_angle",

        "previous_right_thigh_angle",
        "current_right_thigh_angle",

        "previous_trunk_angle",
        "current_trunk_angle",

        "previous_pelvis_angle",
        "current_pelvis_angle",

        "ankle_image_displacement",

    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# 角度変化量
# ============================================================

def calculate_angle_changes(
    df
):

    angle_pairs = [

        (
            "left_knee",
            "previous_left_knee",
            "current_left_knee"
        ),

        (
            "right_knee",
            "previous_right_knee",
            "current_right_knee"
        ),

        (
            "left_hip",
            "previous_left_hip",
            "current_left_hip"
        ),

        (
            "right_hip",
            "previous_right_hip",
            "current_right_hip"
        ),

        (
            "left_ankle",
            "previous_left_ankle",
            "current_left_ankle"
        ),

        (
            "right_ankle",
            "previous_right_ankle",
            "current_right_ankle"
        ),

        (
            "left_thigh",
            "previous_left_thigh_angle",
            "current_left_thigh_angle"
        ),

        (
            "right_thigh",
            "previous_right_thigh_angle",
            "current_right_thigh_angle"
        ),

        (
            "trunk",
            "previous_trunk_angle",
            "current_trunk_angle"
        ),

        (
            "pelvis",
            "previous_pelvis_angle",
            "current_pelvis_angle"
        ),

    ]

    for name, previous, current in angle_pairs:

        if (
            previous in df.columns
            and current in df.columns
        ):

            df[
                f"{name}_change_deg"
            ] = (

                df[current]
                - df[previous]

            )

            df[
                f"{name}_absolute_change_deg"
            ] = (

                df[
                    f"{name}_change_deg"
                ]
                .abs()

            )

    return df


# ============================================================
# 左右差
# ============================================================

def calculate_left_right_difference(
    df
):

    pairs = [

        (
            "previous",
            "knee",
            "previous_left_knee",
            "previous_right_knee"
        ),

        (
            "current",
            "knee",
            "current_left_knee",
            "current_right_knee"
        ),

        (
            "previous",
            "hip",
            "previous_left_hip",
            "previous_right_hip"
        ),

        (
            "current",
            "hip",
            "current_left_hip",
            "current_right_hip"
        ),

        (
            "previous",
            "ankle",
            "previous_left_ankle",
            "previous_right_ankle"
        ),

        (
            "current",
            "ankle",
            "current_left_ankle",
            "current_right_ankle"
        ),

        (
            "previous",
            "thigh",
            "previous_left_thigh_angle",
            "previous_right_thigh_angle"
        ),

        (
            "current",
            "thigh",
            "current_left_thigh_angle",
            "current_right_thigh_angle"
        ),

    ]

    for stage, name, left, right in pairs:

        if (
            left in df.columns
            and right in df.columns
        ):

            df[
                f"{stage}_{name}_difference_deg"
            ] = (

                df[left]
                - df[right]

            )

            df[
                f"{stage}_{name}_absolute_difference_deg"
            ] = (

                df[
                    f"{stage}_{name}_difference_deg"
                ]
                .abs()

            )

    return df


# ============================================================
# ステップ品質
# ============================================================

def evaluate_stride_quality(
    df
):

    quality = []

    for _, row in df.iterrows():

        stride_time = row[
            "stride_time_sec"
        ]

        # ----------------------------------------------
        # 欠損
        # ----------------------------------------------

        if pd.isna(stride_time):

            quality.append(
                "測定不能"
            )

            continue

        # ----------------------------------------------
        # 短すぎる
        # ----------------------------------------------

        if stride_time < MIN_STRIDE_TIME:

            quality.append(
                "短すぎる"
            )

            continue

        # ----------------------------------------------
        # 長すぎる
        # ----------------------------------------------

        if stride_time > MAX_STRIDE_TIME:

            quality.append(
                "長すぎる"
            )

            continue

        # ----------------------------------------------
        # 通常
        # ----------------------------------------------

        quality.append(
            "使用候補"
        )

    df[
        "stride_quality"
    ] = quality

    return df


# ============================================================
# 全体統計
# ============================================================

def print_summary(
    df
):

    print()
    print(
        "=============================="
    )
    print(
        "ステップ品質分析"
    )
    print(
        "=============================="
    )

    print(
        f"全ステップ数: {len(df)}"
    )

    print()

    counts = (
        df[
            "stride_quality"
        ]
        .value_counts()
    )

    for label, count in counts.items():

        print(
            f"{label}: {count}"
        )

    print()

    valid = df[
        df[
            "stride_quality"
        ]
        == "使用候補"
    ]

    if not valid.empty:

        print(
            f"使用候補の平均1歩時間: "
            f"{valid['stride_time_sec'].mean():.3f} 秒"
        )

        print(
            f"使用候補の平均ピッチ: "
            f"{(1.0 / valid['stride_time_sec']).mean():.2f} steps/s"
        )

        print(
            f"使用候補の平均ピッチ: "
            f"{(60.0 / valid['stride_time_sec']).mean():.1f} steps/min"
        )


# ============================================================
# 実行
# ============================================================

def run():

    print(
        "============================================================"
    )

    print(
        "SprintAnalysisAI"
    )

    print(
        "1歩ごとの品質・変化量分析"
    )

    print(
        "============================================================"
    )

    # --------------------------------------------------------
    # 読み込み
    # --------------------------------------------------------

    df = load_data()

    print(
        f"読み込みステップ数: {len(df)}"
    )

    # --------------------------------------------------------
    # 数値化
    # --------------------------------------------------------

    df = convert_numeric(
        df
    )

    # --------------------------------------------------------
    # 角度変化
    # --------------------------------------------------------

    df = calculate_angle_changes(
        df
    )

    # --------------------------------------------------------
    # 左右差
    # --------------------------------------------------------

    df = calculate_left_right_difference(
        df
    )

    # --------------------------------------------------------
    # 品質判定
    # --------------------------------------------------------

    df = evaluate_stride_quality(
        df
    )

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # 統計
    # --------------------------------------------------------

    print_summary(
        df
    )

    print()

    print(
        f"保存先: {OUTPUT_FILE}"
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    run()