from pathlib import Path
import pandas as pd
import numpy as np


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
)


# ============================================================
# 対象角度
# ============================================================

ANGLE_COLUMNS = [
    "left_knee",
    "right_knee",
    "left_hip",
    "right_hip",
    "left_ankle",
    "right_ankle",
    "left_thigh_angle",
    "right_thigh_angle",
    "trunk_angle",
    "pelvis_angle",
]


# ============================================================
# 読み込み
# ============================================================

def load_angle_history():

    path = (
        DATA_DIR /
        "angle_history.csv"
    )

    if not path.exists():

        raise FileNotFoundError(
            f"{path} がありません。"
        )

    df = pd.read_csv(path)

    if df.empty:

        raise ValueError(
            "angle_history.csv が空です。"
        )

    return df


# ============================================================
# 角度を -180〜180 に統一
# ============================================================

def normalize_angle(angle):

    if pd.isna(angle):
        return np.nan

    angle = float(angle)

    return (
        (angle + 180.0) % 360.0
    ) - 180.0


# ============================================================
# 角度の循環平均
#
# 例:
# 179° と -179°
# 単純平均 → 0°
# 循環平均 → 約180°
# ============================================================

def circular_mean_deg(values):

    values = pd.Series(
        values,
        dtype="float64"
    ).dropna()

    if values.empty:
        return np.nan

    radians = np.deg2rad(
        values.to_numpy()
    )

    sin_mean = np.mean(
        np.sin(radians)
    )

    cos_mean = np.mean(
        np.cos(radians)
    )

    angle = np.rad2deg(
        np.arctan2(
            sin_mean,
            cos_mean
        )
    )

    return float(angle)


# ============================================================
# 循環標準偏差
# ============================================================

def circular_std_deg(values):

    values = pd.Series(
        values,
        dtype="float64"
    ).dropna()

    if len(values) < 2:
        return np.nan

    radians = np.deg2rad(
        values.to_numpy()
    )

    sin_mean = np.mean(
        np.sin(radians)
    )

    cos_mean = np.mean(
        np.cos(radians)
    )

    resultant_length = np.sqrt(
        sin_mean ** 2
        + cos_mean ** 2
    )

    resultant_length = np.clip(
        resultant_length,
        1e-12,
        1.0
    )

    circular_std = np.sqrt(
        -2.0
        * np.log(resultant_length)
    )

    return float(
        np.rad2deg(
            circular_std
        )
    )


# ============================================================
# 通常角度の妥当性
# ============================================================

def calculate_quality_flags(df):

    result = df.copy()

    # ----------------------------------------
    # 数値化
    # ----------------------------------------

    for column in ANGLE_COLUMNS:

        if column in result.columns:

            result[column] = pd.to_numeric(
                result[column],
                errors="coerce"
            )

    # ----------------------------------------
    # 関節角度
    #
    # 3点角度は基本的に0〜180°
    # ----------------------------------------

    joint_angles = [
        "left_knee",
        "right_knee",
        "left_hip",
        "right_hip",
        "left_ankle",
        "right_ankle",
    ]

    for column in joint_angles:

        if column not in result.columns:
            continue

        result[
            f"{column}_valid"
        ] = (
            result[column].between(
                1.0,
                179.0,
                inclusive="both"
            )
        )

    # ----------------------------------------
    # 大腿角度
    #
    # line angleなので -180〜180
    # ----------------------------------------

    thigh_angles = [
        "left_thigh_angle",
        "right_thigh_angle",
    ]

    for column in thigh_angles:

        if column not in result.columns:
            continue

        result[
            f"{column}_normalized"
        ] = result[column].apply(
            normalize_angle
        )

        result[
            f"{column}_valid"
        ] = result[
            f"{column}_normalized"
        ].notna()

    # ----------------------------------------
    # 体幹
    # ----------------------------------------

    if "trunk_angle" in result.columns:

        result[
            "trunk_angle_normalized"
        ] = result[
            "trunk_angle"
        ].apply(
            normalize_angle
        )

        result[
            "trunk_angle_valid"
        ] = result[
            "trunk_angle_normalized"
        ].notna()

    # ----------------------------------------
    # 骨盤
    # ----------------------------------------

    if "pelvis_angle" in result.columns:

        result[
            "pelvis_angle_normalized"
        ] = result[
            "pelvis_angle"
        ].apply(
            normalize_angle
        )

        result[
            "pelvis_angle_valid"
        ] = result[
            "pelvis_angle_normalized"
        ].notna()

    return result


# ============================================================
# 全体品質サマリー
# ============================================================

def build_quality_summary(df):

    rows = []

    for column in ANGLE_COLUMNS:

        if column not in df.columns:
            continue

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        valid = values.notna()

        valid_count = int(
            valid.sum()
        )

        total_count = len(
            values
        )

        if total_count > 0:

            valid_rate = (
                valid_count
                / total_count
                * 100.0
            )

        else:

            valid_rate = 0.0

        # ------------------------------------
        # 体幹・骨盤・大腿は
        # 循環角度として評価
        # ------------------------------------

        if column in [
            "left_thigh_angle",
            "right_thigh_angle",
            "trunk_angle",
            "pelvis_angle",
        ]:

            normalized = values.apply(
                normalize_angle
            )

            mean_value = circular_mean_deg(
                normalized
            )

            std_value = circular_std_deg(
                normalized
            )

        else:

            mean_value = (
                float(values.mean())
                if valid_count > 0
                else np.nan
            )

            std_value = (
                float(values.std())
                if valid_count > 1
                else np.nan
            )

        # ------------------------------------
        # 判定
        # ------------------------------------

        if valid_rate >= 95:

            status = "使用可能"

        elif valid_rate >= 80:

            status = "要注意"

        else:

            status = "使用不可"

        rows.append({

            "metric": column,

            "sample_count":
                total_count,

            "valid_count":
                valid_count,

            "valid_rate_pct":
                valid_rate,

            "mean_deg":
                mean_value,

            "std_deg":
                std_value,

            "quality_status":
                status,

        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# 実行
# ============================================================

def run_angle_quality():

    print(
        "========================================"
    )

    print(
        "SprintAnalysisAI"
    )

    print(
        "角度データ品質チェック"
    )

    print(
        "========================================"
    )

    df = load_angle_history()

    checked = calculate_quality_flags(
        df
    )

    summary = build_quality_summary(
        checked
    )

    output_path = (
        DATA_DIR /
        "angle_quality.csv"
    )

    summary.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print()

    print(
        summary.to_string(
            index=False
        )
    )

    print()

    print(
        f"保存先: {output_path}"
    )

    return summary


if __name__ == "__main__":

    run_angle_quality()