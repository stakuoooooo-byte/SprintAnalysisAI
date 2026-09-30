import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 1歩ごとの測定品質・変化量分析
#
# 目的:
#   1. 1歩時間の異常を検出
#   2. 関節角度の急激な変化を検出
#   3. 左右差を記録
#   4. 研究比較に使用できる候補データを分離
#
# 注意:
#   このプログラムは「良いフォーム / 悪いフォーム」を
#   判定するものではありません。
#
#   あくまで動画・骨格推定データの
#   「測定品質」を評価します。
# ============================================================


# ============================================================
# パス
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
# 1歩時間の品質基準
# ============================================================

MIN_STRIDE_TIME = 0.15
MAX_STRIDE_TIME = 0.35


# ============================================================
# 1歩間で許容する角度変化
#
# これは「理想フォーム」の基準ではなく、
# 動画上で1イベント間に突然変化した場合の
# 骨格推定異常候補を検出するための基準。
# ============================================================

MAX_KNEE_CHANGE = 70.0
MAX_HIP_CHANGE = 50.0
MAX_ANKLE_CHANGE = 50.0
MAX_THIGH_CHANGE = 50.0
MAX_TRUNK_CHANGE = 40.0
MAX_PELVIS_CHANGE = 50.0


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

def convert_numeric(df):

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

    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# 角度変化量を計算
# ============================================================

def calculate_angle_changes(df):

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

def calculate_left_right_difference(df):

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

    for (
        stage,
        name,
        left,
        right
    ) in pairs:

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
# 急変フラグ
# ============================================================

def calculate_anomaly_flags(df):

    # --------------------------------------------------------
    # 膝
    # --------------------------------------------------------

    knee_columns = [
        "left_knee_absolute_change_deg",
        "right_knee_absolute_change_deg",
    ]

    existing = [
        c for c in knee_columns
        if c in df.columns
    ]

    if existing:

        df["knee_change_anomaly"] = (
            df[existing]
            .max(axis=1)
            > MAX_KNEE_CHANGE
        )

    else:

        df["knee_change_anomaly"] = False


    # --------------------------------------------------------
    # 股関節
    # --------------------------------------------------------

    hip_columns = [
        "left_hip_absolute_change_deg",
        "right_hip_absolute_change_deg",
    ]

    existing = [
        c for c in hip_columns
        if c in df.columns
    ]

    if existing:

        df["hip_change_anomaly"] = (
            df[existing]
            .max(axis=1)
            > MAX_HIP_CHANGE
        )

    else:

        df["hip_change_anomaly"] = False


    # --------------------------------------------------------
    # 足関節
    # --------------------------------------------------------

    ankle_columns = [
        "left_ankle_absolute_change_deg",
        "right_ankle_absolute_change_deg",
    ]

    existing = [
        c for c in ankle_columns
        if c in df.columns
    ]

    if existing:

        df["ankle_change_anomaly"] = (
            df[existing]
            .max(axis=1)
            > MAX_ANKLE_CHANGE
        )

    else:

        df["ankle_change_anomaly"] = False


    # --------------------------------------------------------
    # 大腿
    # --------------------------------------------------------

    thigh_columns = [
        "left_thigh_absolute_change_deg",
        "right_thigh_absolute_change_deg",
    ]

    existing = [
        c for c in thigh_columns
        if c in df.columns
    ]

    if existing:

        df["thigh_change_anomaly"] = (
            df[existing]
            .max(axis=1)
            > MAX_THIGH_CHANGE
        )

    else:

        df["thigh_change_anomaly"] = False


    # --------------------------------------------------------
    # 体幹
    # --------------------------------------------------------

    if (
        "trunk_absolute_change_deg"
        in df.columns
    ):

        df["trunk_change_anomaly"] = (
            df[
                "trunk_absolute_change_deg"
            ]
            > MAX_TRUNK_CHANGE
        )

    else:

        df["trunk_change_anomaly"] = False


    # --------------------------------------------------------
    # 骨盤
    # --------------------------------------------------------

    if (
        "pelvis_absolute_change_deg"
        in df.columns
    ):

        df["pelvis_change_anomaly"] = (
            df[
                "pelvis_absolute_change_deg"
            ]
            > MAX_PELVIS_CHANGE
        )

    else:

        df["pelvis_change_anomaly"] = False


    return df


# ============================================================
# 1歩時間の品質
# ============================================================

def calculate_time_quality(df):

    conditions = []

    for value in df[
        "stride_time_sec"
    ]:

        if pd.isna(value):

            conditions.append(
                "測定不能"
            )

        elif value < MIN_STRIDE_TIME:

            conditions.append(
                "時間異常"
            )

        elif value > MAX_STRIDE_TIME:

            conditions.append(
                "時間異常"
            )

        else:

            conditions.append(
                "正常範囲"
            )

    df[
        "stride_time_quality"
    ] = conditions

    return df


# ============================================================
# 総合的な測定品質
# ============================================================

def calculate_overall_quality(df):

    quality_list = []

    anomaly_columns = [

        "knee_change_anomaly",
        "hip_change_anomaly",
        "ankle_change_anomaly",
        "thigh_change_anomaly",
        "trunk_change_anomaly",
        "pelvis_change_anomaly",

    ]

    for _, row in df.iterrows():

        reasons = []

        # ----------------------------------------------------
        # 時間
        # ----------------------------------------------------

        if (
            row[
                "stride_time_quality"
            ]
            != "正常範囲"
        ):

            reasons.append(
                "step_time"
            )

        # ----------------------------------------------------
        # 急変
        # ----------------------------------------------------

        for column in anomaly_columns:

            if (
                column in row
                and bool(row[column])
            ):

                reasons.append(
                    column.replace(
                        "_anomaly",
                        ""
                    )
                )

        # ----------------------------------------------------
        # 判定
        # ----------------------------------------------------

        if len(reasons) == 0:

            quality_list.append(
                "研究比較候補"
            )

        elif len(reasons) == 1:

            quality_list.append(
                "要確認"
            )

        else:

            quality_list.append(
                "除外候補"
            )

    df[
        "measurement_quality"
    ] = quality_list

    return df


# ============================================================
# 品質理由
# ============================================================

def create_quality_reason(df):

    reasons_list = []

    for _, row in df.iterrows():

        reasons = []

        if (
            row[
                "stride_time_quality"
            ]
            != "正常範囲"
        ):

            reasons.append(
                "1歩時間"
            )

        mapping = {

            "knee_change_anomaly":
                "膝角度急変",

            "hip_change_anomaly":
                "股関節角度急変",

            "ankle_change_anomaly":
                "足関節角度急変",

            "thigh_change_anomaly":
                "大腿角度急変",

            "trunk_change_anomaly":
                "体幹角度急変",

            "pelvis_change_anomaly":
                "骨盤角度急変",

        }

        for column, label in mapping.items():

            if (
                column in row
                and bool(row[column])
            ):

                reasons.append(
                    label
                )

        if not reasons:

            reasons.append(
                "異常検出なし"
            )

        reasons_list.append(
            " / ".join(reasons)
        )

    df[
        "measurement_quality_reason"
    ] = reasons_list

    return df


# ============================================================
# 統計
# ============================================================

def print_summary(df):

    print()
    print(
        "=============================="
    )

    print(
        "測定品質分析結果"
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
            "measurement_quality"
        ]
        .value_counts()
    )

    for label, count in counts.items():

        print(
            f"{label}: {count}"
        )

    print()

    # --------------------------------------------------------
    # 急変件数
    # --------------------------------------------------------

    anomaly_columns = [

        "knee_change_anomaly",
        "hip_change_anomaly",
        "ankle_change_anomaly",
        "thigh_change_anomaly",
        "trunk_change_anomaly",
        "pelvis_change_anomaly",

    ]

    print(
        "角度急変検出:"
    )

    for column in anomaly_columns:

        if column in df.columns:

            count = int(
                df[column].sum()
            )

            print(
                f"  {column}: {count}"
            )

    print()

    # --------------------------------------------------------
    # 研究比較候補
    # --------------------------------------------------------

    research_candidate = df[
        df[
            "measurement_quality"
        ]
        == "研究比較候補"
    ]

    print(
        f"研究比較候補: "
        f"{len(research_candidate)}"
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
        "測定品質・異常値分析"
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
    # 異常フラグ
    # --------------------------------------------------------

    df = calculate_anomaly_flags(
        df
    )

    # --------------------------------------------------------
    # 時間品質
    # --------------------------------------------------------

    df = calculate_time_quality(
        df
    )

    # --------------------------------------------------------
    # 総合品質
    # --------------------------------------------------------

    df = calculate_overall_quality(
        df
    )

    # --------------------------------------------------------
    # 理由
    # --------------------------------------------------------

    df = create_quality_reason(
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