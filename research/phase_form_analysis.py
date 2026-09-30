from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# 設定
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
# CSV読み込み
# ============================================================

def load_csv(path):

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"{path} が見つかりません。"
        )

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(
            f"{path} にデータがありません。"
        )

    return df


# ============================================================
# 区間情報を取得
# ============================================================

def load_phase_information():

    path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "phase_analysis_detail.csv"
    )

    return load_csv(path)


# ============================================================
# 角度データ
# ============================================================

def load_angle_history():

    path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "angle_history.csv"
    )

    return load_csv(path)


# ============================================================
# フレーム→時間区間対応
# ============================================================

def assign_phase_to_angles(
    angle_df,
    phase_df
):

    angle_df = angle_df.copy()
    phase_df = phase_df.copy()

    if "frame" not in angle_df.columns:
        raise ValueError(
            "angle_history.csv に frame がありません。"
        )

    if "frame" not in phase_df.columns:
        raise ValueError(
            "phase_analysis_detail.csv に frame がありません。"
        )

    angle_df["frame"] = pd.to_numeric(
        angle_df["frame"],
        errors="coerce"
    )

    phase_df["frame"] = pd.to_numeric(
        phase_df["frame"],
        errors="coerce"
    )

    angle_df = angle_df.dropna(
        subset=["frame"]
    )

    phase_df = phase_df.dropna(
        subset=["frame"]
    )

    phase_map = phase_df[
        ["frame", "segment"]
    ].drop_duplicates(
        subset=["frame"]
    )

    merged = angle_df.merge(
        phase_map,
        on="frame",
        how="inner"
    )

    return merged


# ============================================================
# 区間別フォーム統計
# ============================================================

def calculate_phase_form_metrics(
    df
):

    rows = []

    for segment, group in df.groupby(
        "segment"
    ):

        result = {
            "segment": int(segment),

            "frame_count": int(
                len(group)
            ),
        }

        # ----------------------------------------
        # 各角度
        # ----------------------------------------

        for column in ANGLE_COLUMNS:

            if column not in group.columns:
                result[
                    f"{column}_avg"
                ] = np.nan

                result[
                    f"{column}_std"
                ] = np.nan

                continue

            values = pd.to_numeric(
                group[column],
                errors="coerce"
            ).dropna()

            if len(values) == 0:

                result[
                    f"{column}_avg"
                ] = np.nan

                result[
                    f"{column}_std"
                ] = np.nan

            else:

                result[
                    f"{column}_avg"
                ] = float(
                    values.mean()
                )

                result[
                    f"{column}_std"
                ] = float(
                    values.std()
                )

        # ----------------------------------------
        # 左右差
        # ----------------------------------------

        for left, right, name in [

            (
                "left_knee",
                "right_knee",
                "knee"
            ),

            (
                "left_hip",
                "right_hip",
                "hip"
            ),

            (
                "left_ankle",
                "right_ankle",
                "ankle"
            ),

            (
                "left_thigh_angle",
                "right_thigh_angle",
                "thigh"
            ),

        ]:

            if (
                left in group.columns
                and right in group.columns
            ):

                left_values = pd.to_numeric(
                    group[left],
                    errors="coerce"
                )

                right_values = pd.to_numeric(
                    group[right],
                    errors="coerce"
                )

                difference = (
                    left_values
                    - right_values
                ).abs()

                difference = (
                    difference
                    .dropna()
                )

                if len(difference) > 0:

                    result[
                        f"{name}_difference_deg"
                    ] = float(
                        difference.mean()
                    )

                else:

                    result[
                        f"{name}_difference_deg"
                    ] = np.nan

            else:

                result[
                    f"{name}_difference_deg"
                ] = np.nan

        rows.append(result)

    return pd.DataFrame(rows)


# ============================================================
# 保存
# ============================================================

def save_result(df):

    output_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "phase_form_analysis.csv"
    )

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    return output_path


# ============================================================
# 実行
# ============================================================

def run_phase_form_analysis():

    print(
        "=== 区間別フォーム分析 ==="
    )

    phase_df = (
        load_phase_information()
    )

    angle_df = (
        load_angle_history()
    )

    merged = assign_phase_to_angles(
        angle_df,
        phase_df
    )

    if merged.empty:

        raise ValueError(
            "接地イベントと角度データを"
            "対応付けられませんでした。"
        )

    result = (
        calculate_phase_form_metrics(
            merged
        )
    )

    output_path = save_result(
        result
    )

    print()
    print(
        result.to_string(
            index=False
        )
    )

    print()
    print(
        f"保存先: {output_path}"
    )

    return result


if __name__ == "__main__":

    run_phase_form_analysis()