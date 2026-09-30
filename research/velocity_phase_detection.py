import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 相対速度による局面候補検出
#
# 目的:
#   velocity_profile.csv を使って、
#   動画内の速度変化を局面候補として分類する。
#
# 重要:
#   ここでの分類は「動画内相対速度」に基づく。
#   加速局面・最大速度局面を直接証明するものではない。
# ============================================================


BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

DATA_DIR = BASE_DIR / "data"


INPUT_FILE = (
    DATA_DIR /
    "velocity_profile.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "velocity_phase_detection.csv"
)


# ============================================================
# 設定
# ============================================================

# 速度変化が小さいときの許容範囲
CHANGE_EPSILON = 0.02


# ============================================================
# 読み込み
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
            "velocity_profile.csv が空です。"
        )

    return df


# ============================================================
# 数値化
# ============================================================

def convert_numeric(df):

    columns = [

        "relative_speed",

        "relative_speed_rolling_mean",

        "relative_speed_change",

        "normalized_relative_speed",

        "relative_position",

        "stride_time_sec",

    ]

    for column in columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# ============================================================
# 速度変化の分類
# ============================================================

def classify_change(df):

    states = []

    for value in df[
        "relative_speed_change"
    ]:

        if pd.isna(value):

            states.append(
                "判定不能"
            )

        elif value > CHANGE_EPSILON:

            states.append(
                "速度上昇"
            )

        elif value < -CHANGE_EPSILON:

            states.append(
                "速度低下"
            )

        else:

            states.append(
                "速度維持"
            )

    df[
        "velocity_change_state"
    ] = states

    return df


# ============================================================
# 速度レベル
# ============================================================

def classify_level(df):

    levels = []

    for value in df[
        "normalized_relative_speed"
    ]:

        if pd.isna(value):

            levels.append(
                "判定不能"
            )

        elif value < 0.25:

            levels.append(
                "低速度域"
            )

        elif value < 0.50:

            levels.append(
                "中速度域"
            )

        elif value < 0.75:

            levels.append(
                "高速度域"
            )

        else:

            levels.append(
                "相対速度上位域"
            )

    df[
        "velocity_level"
    ] = levels

    return df


# ============================================================
# 局面候補
# ============================================================

def classify_phase(df):

    phases = []

    for _, row in df.iterrows():

        level = row[
            "velocity_level"
        ]

        change = row[
            "velocity_change_state"
        ]


        # ----------------------------------------------------
        # データ不足
        # ----------------------------------------------------

        if (
            level == "判定不能"
            or change == "判定不能"
        ):

            phases.append(
                "判定不能"
            )

            continue


        # ----------------------------------------------------
        # 速度上昇
        # ----------------------------------------------------

        if change == "速度上昇":

            phases.append(
                "速度上昇局面候補"
            )

            continue


        # ----------------------------------------------------
        # 高速度域で維持
        # ----------------------------------------------------

        if (
            level == "高速度域"
            and change == "速度維持"
        ):

            phases.append(
                "高速度維持候補"
            )

            continue


        # ----------------------------------------------------
        # 相対速度上位域
        # ----------------------------------------------------

        if (
            level == "相対速度上位域"
            and change != "速度低下"
        ):

            phases.append(
                "相対速度ピーク候補"
            )

            continue


        # ----------------------------------------------------
        # 速度低下
        # ----------------------------------------------------

        if change == "速度低下":

            phases.append(
                "速度低下局面候補"
            )

            continue


        # ----------------------------------------------------
        # その他
        # ----------------------------------------------------

        phases.append(
            "速度維持"
        )


    df[
        "phase_candidate"
    ] = phases

    return df


# ============================================================
# 連続区間ID
# ============================================================

def create_phase_groups(df):

    phase = df[
        "phase_candidate"
    ]

    change = (
        phase
        != phase.shift(1)
    )

    df[
        "phase_group"
    ] = change.cumsum()

    return df


# ============================================================
# 局面ごとの統計
# ============================================================

def create_phase_summary(df):

    results = []


    for group_id, group in df.groupby(
        "phase_group"
    ):

        if group.empty:

            continue


        result = {

            "phase_group":
                group_id,

            "phase_candidate":
                group[
                    "phase_candidate"
                ].iloc[0],

            "step_count":
                len(group),

            "start_relative_position":
                group[
                    "relative_position"
                ].min(),

            "end_relative_position":
                group[
                    "relative_position"
                ].max(),

        }


        # ----------------------------------------------------
        # 相対速度
        # ----------------------------------------------------

        if (
            "relative_speed"
            in group.columns
        ):

            result[
                "average_relative_speed"
            ] = group[
                "relative_speed"
            ].mean()

            result[
                "maximum_relative_speed"
            ] = group[
                "relative_speed"
            ].max()


        # ----------------------------------------------------
        # 正規化速度
        # ----------------------------------------------------

        if (
            "normalized_relative_speed"
            in group.columns
        ):

            result[
                "average_normalized_speed"
            ] = group[
                "normalized_relative_speed"
            ].mean()


        results.append(
            result
        )


    return pd.DataFrame(
        results
    )


# ============================================================
# 保存
# ============================================================

def save_data(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


# ============================================================
# 表示
# ============================================================

def print_summary(df):

    print()

    print(
        "============================================================"
    )

    print(
        "速度局面候補"
    )

    print(
        "============================================================"
    )

    print()

    summary = create_phase_summary(
        df
    )


    for _, row in summary.iterrows():

        print(
            f"[グループ {int(row['phase_group'])}]"
        )

        print(
            f"  局面: "
            f"{row['phase_candidate']}"
        )

        print(
            f"  ステップ数: "
            f"{int(row['step_count'])}"
        )

        print(
            f"  動画内位置: "
            f"{row['start_relative_position']:.2f}"
            f" → "
            f"{row['end_relative_position']:.2f}"
        )


        if (
            "average_normalized_speed"
            in row
            and pd.notna(
                row[
                    "average_normalized_speed"
                ]
            )
        ):

            print(
                f"  平均正規化速度: "
                f"{row['average_normalized_speed']:.3f}"
            )


        print()


    print(
        "注意:"
    )

    print(
        "「相対速度ピーク候補」は最大速度局面の確定ではありません。"
    )

    print(
        "カメラ追従・撮影条件などの影響を受けます。"
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
        "速度局面候補検出"
    )

    print(
        "============================================================"
    )


    df = load_data()


    print(
        f"分析対象: {len(df)}ステップ"
    )


    df = convert_numeric(
        df
    )


    df = classify_change(
        df
    )


    df = classify_level(
        df
    )


    df = classify_phase(
        df
    )


    df = create_phase_groups(
        df
    )


    save_data(
        df
    )


    print_summary(
        df
    )


    print()

    print(
        f"保存先: {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    run()