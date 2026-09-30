import pandas as pd
import numpy as np
from pathlib import Path


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
)

INPUT_FILE = (
    DATA_DIR /
    "contact_form_metrics.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "contact_form_quality.csv"
)


# ============================================================
# 対象となるフォーム指標
# ============================================================

METRICS = [
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
            "contact_form_metrics.csv が空です。"
        )

    return df


# ============================================================
# 角度の正規化
# ============================================================

def normalize_angle(angle):

    if pd.isna(angle):

        return np.nan

    return (
        (float(angle) + 180.0)
        % 360.0
    ) - 180.0


# ============================================================
# 循環平均
# ============================================================

def circular_mean(values):

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

    return float(
        np.rad2deg(
            np.arctan2(
                sin_mean,
                cos_mean
            )
        )
    )


# ============================================================
# 通常角度の外れ値判定
#
# IQR方式
# ============================================================

def remove_outliers_iqr(series):

    values = pd.to_numeric(
        series,
        errors="coerce"
    )

    q1 = values.quantile(
        0.25
    )

    q3 = values.quantile(
        0.75
    )

    iqr = q3 - q1

    if pd.isna(iqr) or iqr == 0:

        return values

    lower = (
        q1
        - 1.5 * iqr
    )

    upper = (
        q3
        + 1.5 * iqr
    )

    return values.where(
        (values >= lower)
        & (values <= upper)
    )


# ============================================================
# 左右脚別の接地イベント解析
# ============================================================

def analyze_side(
    df,
    side
):

    if side == "left":

        knee = "left_knee"
        hip = "left_hip"
        ankle = "left_ankle"
        thigh = "left_thigh_angle"

    else:

        knee = "right_knee"
        hip = "right_hip"
        ankle = "right_ankle"
        thigh = "right_thigh_angle"

    rows = []

    for metric in [
        knee,
        hip,
        ankle,
        thigh,
    ]:

        if metric not in df.columns:

            continue

        original = pd.to_numeric(
            df[metric],
            errors="coerce"
        )

        filtered = remove_outliers_iqr(
            original
        )

        original_count = int(
            original.notna().sum()
        )

        valid_count = int(
            filtered.notna().sum()
        )

        removed_count = (
            original_count
            - valid_count
        )

        if valid_count > 0:

            mean_value = float(
                filtered.mean()
            )

            std_value = float(
                filtered.std()
            )

        else:

            mean_value = np.nan
            std_value = np.nan

        rows.append({

            "side": side,

            "metric": metric,

            "original_count":
                original_count,

            "valid_count":
                valid_count,

            "removed_outliers":
                removed_count,

            "outlier_rate_pct":
                (
                    removed_count
                    / original_count
                    * 100
                )
                if original_count > 0
                else 0,

            "mean_deg":
                mean_value,

            "std_deg":
                std_value,

        })

    return rows


# ============================================================
# 体幹・骨盤
# ============================================================

def analyze_global_angles(df):

    rows = []

    for metric in [
        "trunk_angle",
        "pelvis_angle",
    ]:

        if metric not in df.columns:

            continue

        values = pd.to_numeric(
            df[metric],
            errors="coerce"
        ).apply(
            normalize_angle
        )

        valid = values.dropna()

        if valid.empty:

            continue

        rows.append({

            "side": "global",

            "metric": metric,

            "original_count":
                len(values),

            "valid_count":
                len(valid),

            "removed_outliers":
                0,

            "outlier_rate_pct":
                0,

            "mean_deg":
                circular_mean(valid),

            "std_deg":
                np.nan,

        })

    return rows


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
        "接地フォーム品質解析"
    )

    print(
        "============================================================"
    )

    df = load_data()

    print(
        f"接地イベント数: {len(df)}"
    )

    rows = []

    # 左脚
    rows.extend(
        analyze_side(
            df,
            "left"
        )
    )

    # 右脚
    rows.extend(
        analyze_side(
            df,
            "right"
        )
    )

    # 体幹・骨盤
    rows.extend(
        analyze_global_angles(
            df
        )
    )

    result = pd.DataFrame(
        rows
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()

    print(
        result.to_string(
            index=False
        )
    )

    print()

    print(
        f"保存先: {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    run()