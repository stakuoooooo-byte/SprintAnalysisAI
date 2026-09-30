import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 動画内相対速度プロファイル
#
# 目的:
#   1歩ごとの画像上の移動量と時間から
#   動画内の相対的な速度変化を作る。
#
# 重要:
#   カメラ追従映像のため、これは絶対速度(m/s)ではない。
#   最大速度を直接証明するものでもない。
# ============================================================


BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

DATA_DIR = BASE_DIR / "data"


INPUT_FILE = (
    DATA_DIR /
    "research_phase_matching.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "velocity_profile.csv"
)


# ============================================================
# 入力列の候補
# ============================================================

DISPLACEMENT_COLUMNS = [

    "ankle_image_displacement",

    "current_ankle_image_displacement",

    "image_displacement",

]


TIME_COLUMNS = [

    "stride_time_sec",

]


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
            "入力データが空です。"
        )

    return df


# ============================================================
# 使用する移動量列を探す
# ============================================================

def find_displacement_column(df):

    for column in DISPLACEMENT_COLUMNS:

        if column in df.columns:

            return column

    return None


# ============================================================
# 相対速度計算
# ============================================================

def calculate_relative_speed(df):

    displacement_column = (
        find_displacement_column(df)
    )

    if displacement_column is None:

        raise ValueError(
            "画像上の移動量を表す列が見つかりません。"
        )

    if "stride_time_sec" not in df.columns:

        raise ValueError(
            "stride_time_sec がありません。"
        )


    displacement = pd.to_numeric(

        df[
            displacement_column
        ],

        errors="coerce"

    )

    stride_time = pd.to_numeric(

        df[
            "stride_time_sec"
        ],

        errors="coerce"

    )


    # --------------------------------------------------------
    # 相対速度
    #
    # 画像座標上の移動量 / 1歩時間
    # --------------------------------------------------------

    df[
        "relative_speed"
    ] = np.where(

        stride_time > 0,

        displacement / stride_time,

        np.nan

    )


    df[
        "velocity_data_source"
    ] = (
        "image_displacement_per_second"
    )


    return df


# ============================================================
# 正規化速度
# ============================================================

def calculate_normalized_speed(df):

    valid = df[
        "relative_speed"
    ].dropna()


    if valid.empty:

        df[
            "normalized_relative_speed"
        ] = np.nan

        return df


    minimum = valid.min()

    maximum = valid.max()


    if maximum == minimum:

        df[
            "normalized_relative_speed"
        ] = 0.0

    else:

        df[
            "normalized_relative_speed"
        ] = (

            df[
                "relative_speed"
            ]
            - minimum

        ) / (

            maximum
            - minimum

        )


    return df


# ============================================================
# 移動平均
# ============================================================

def calculate_smoothed_speed(df):

    # 3歩移動平均
    df[
        "relative_speed_rolling_mean"
    ] = (

        df[
            "relative_speed"
        ]
        .rolling(
            window=3,
            min_periods=1
        )
        .mean()

    )

    return df


# ============================================================
# 速度変化
# ============================================================

def calculate_velocity_change(df):

    df[
        "relative_speed_change"
    ] = (

        df[
            "relative_speed_rolling_mean"
        ]
        .diff()

    )

    return df


# ============================================================
# 仮の速度状態
#
# 「最大速度局面」とは呼ばない。
# ============================================================

def classify_velocity_state(df):

    states = []


    for value in df[
        "normalized_relative_speed"
    ]:

        if pd.isna(value):

            states.append(
                "判定不能"
            )

        elif value < 0.25:

            states.append(
                "低速度域"
            )

        elif value < 0.50:

            states.append(
                "速度上昇域"
            )

        elif value < 0.75:

            states.append(
                "高速度域"
            )

        else:

            states.append(
                "相対速度ピーク域"
            )


    df[
        "relative_velocity_state"
    ] = states


    return df


# ============================================================
# ピーク判定
# ============================================================

def detect_relative_peak(df):

    if (
        "relative_speed_rolling_mean"
        not in df.columns
    ):

        df[
            "relative_peak_candidate"
        ] = False

        return df


    maximum = df[
        "relative_speed_rolling_mean"
    ].max()


    # 上位10%程度を候補として扱う
    threshold = (
        maximum * 0.90
    )


    df[
        "relative_peak_candidate"
    ] = (

        df[
            "relative_speed_rolling_mean"
        ]
        >= threshold

    )


    return df


# ============================================================
# 時間位置
# ============================================================

def calculate_relative_position(df):

    if (
        "relative_position"
        in df.columns
    ):

        return df


    df[
        "relative_position"
    ] = np.linspace(
        0,
        1,
        len(df)
    )


    return df


# ============================================================
# 結果表示
# ============================================================

def print_summary(df):

    print()

    print(
        "============================================================"
    )

    print(
        "動画内相対速度プロファイル"
    )

    print(
        "============================================================"
    )

    print()

    print(
        "注意:"
    )

    print(
        "これは絶対速度(m/s)ではありません。"
    )

    print(
        "カメラ追従の影響を含む画像上の相対速度です。"
    )

    print()

    valid = df[
        "relative_speed"
    ].dropna()


    if valid.empty:

        print(
            "速度を計算できませんでした。"
        )

        return


    print(
        f"平均相対速度: "
        f"{valid.mean():.4f}"
    )

    print(
        f"最大相対速度: "
        f"{valid.max():.4f}"
    )

    print(
        f"最小相対速度: "
        f"{valid.min():.4f}"
    )

    print()


    peak_count = int(

        df[
            "relative_peak_candidate"
        ]
        .sum()

    )


    print(
        f"相対速度ピーク候補: "
        f"{peak_count}ステップ"
    )


    print()

    print(
        "速度状態:"
    )

    counts = (
        df[
            "relative_velocity_state"
        ]
        .value_counts()
    )


    for state, count in counts.items():

        print(
            f"  {state}: {count}"
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

    print()

    print(
        f"保存先: {OUTPUT_FILE}"
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
        "動画内相対速度分析"
    )

    print(
        "============================================================"
    )


    df = load_data()


    print(
        f"分析対象: {len(df)}ステップ"
    )


    # --------------------------------------------------------
    # 相対速度
    # --------------------------------------------------------

    df = calculate_relative_speed(
        df
    )


    # --------------------------------------------------------
    # 正規化
    # --------------------------------------------------------

    df = calculate_normalized_speed(
        df
    )


    # --------------------------------------------------------
    # 平滑化
    # --------------------------------------------------------

    df = calculate_smoothed_speed(
        df
    )


    # --------------------------------------------------------
    # 速度変化
    # --------------------------------------------------------

    df = calculate_velocity_change(
        df
    )


    # --------------------------------------------------------
    # 状態分類
    # --------------------------------------------------------

    df = classify_velocity_state(
        df
    )


    # --------------------------------------------------------
    # ピーク候補
    # --------------------------------------------------------

    df = detect_relative_peak(
        df
    )


    # --------------------------------------------------------
    # 相対位置
    # --------------------------------------------------------

    df = calculate_relative_position(
        df
    )


    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    save_data(
        df
    )


    # --------------------------------------------------------
    # 結果
    # --------------------------------------------------------

    print_summary(
        df
    )


if __name__ == "__main__":

    run()