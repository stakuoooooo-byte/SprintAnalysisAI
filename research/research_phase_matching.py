import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 研究比較用フェーズ分類
#
# 目的:
#   各1歩データに時間的なフェーズ情報を付与する。
#
# 注意:
#   ここでいうフェーズは「加速局面」「最大速度局面」を
#   直接意味するものではない。
#
#   現段階では動画内の時間位置による分類。
# ============================================================


BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

DATA_DIR = BASE_DIR / "data"


INPUT_FILE = (
    DATA_DIR /
    "research_candidate_steps.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "research_phase_matching.csv"
)


# ============================================================
# フェーズ数
# ============================================================

PHASE_COUNT = 5


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
            "研究比較候補データが空です。"
        )

    return df


# ============================================================
# 時間列を取得
# ============================================================

def detect_time_column(df):

    candidates = [

        "current_time_sec",
        "time_sec",
        "previous_time_sec",

    ]

    for column in candidates:

        if column in df.columns:

            return column

    # --------------------------------------------------------
    # stride_phase_metrics.py の形式に対応
    # --------------------------------------------------------

    if "current_event_time_sec" in df.columns:

        return "current_event_time_sec"

    if "previous_event_time_sec" in df.columns:

        return "previous_event_time_sec"

    return None


# ============================================================
# 時間情報を作成
# ============================================================

def create_time_information(df):

    time_column = detect_time_column(
        df
    )

    if time_column is None:

        # 時間列がない場合
        # 行番号による相対位置を使用

        df[
            "relative_position"
        ] = np.linspace(
            0,
            1,
            len(df)
        )

        df[
            "phase_data_source"
        ] = "step_order"

        return df


    df[
        time_column
    ] = pd.to_numeric(
        df[time_column],
        errors="coerce"
    )


    valid = df[
        time_column
    ].dropna()


    if valid.empty:

        df[
            "relative_position"
        ] = np.linspace(
            0,
            1,
            len(df)
        )

        df[
            "phase_data_source"
        ] = "step_order"

        return df


    minimum = valid.min()

    maximum = valid.max()


    if maximum == minimum:

        df[
            "relative_position"
        ] = 0.0

    else:

        df[
            "relative_position"
        ] = (
            df[time_column]
            - minimum
        ) / (
            maximum
            - minimum
        )


    df[
        "phase_data_source"
    ] = time_column


    return df


# ============================================================
# 5分割
# ============================================================

def assign_temporal_phase(df):

    labels = [

        "phase_1_early",

        "phase_2_early_middle",

        "phase_3_middle",

        "phase_4_late_middle",

        "phase_5_late",

    ]


    bins = np.linspace(
        0,
        1,
        PHASE_COUNT + 1
    )


    df[
        "temporal_phase"
    ] = pd.cut(

        df[
            "relative_position"
        ],

        bins=bins,

        labels=labels,

        include_lowest=True,

        duplicates="drop"

    )


    return df


# ============================================================
# フェーズ内統計
# ============================================================

def calculate_phase_statistics(
    df
):

    results = []


    for phase in df[
        "temporal_phase"
    ].dropna().unique():

        phase_df = df[
            df[
                "temporal_phase"
            ]
            == phase
        ]


        result = {

            "temporal_phase":
                phase,

            "step_count":
                len(phase_df),

        }


        if (
            "stride_time_sec"
            in phase_df.columns
        ):

            values = pd.to_numeric(

                phase_df[
                    "stride_time_sec"
                ],

                errors="coerce"

            ).dropna()


            if not values.empty:

                result[
                    "average_stride_time_sec"
                ] = values.mean()

                result[
                    "average_step_rate_steps_per_sec"
                ] = (
                    1 / values.mean()
                )


        if (
            "current_left_knee"
            in phase_df.columns
        ):

            values = pd.to_numeric(

                phase_df[
                    "current_left_knee"
                ],

                errors="coerce"

            ).dropna()


            if not values.empty:

                result[
                    "left_knee_mean_deg"
                ] = values.mean()


        if (
            "current_right_knee"
            in phase_df.columns
        ):

            values = pd.to_numeric(

                phase_df[
                    "current_right_knee"
                ],

                errors="coerce"

            ).dropna()


            if not values.empty:

                result[
                    "right_knee_mean_deg"
                ] = values.mean()


        results.append(
            result
        )


    return pd.DataFrame(
        results
    )


# ============================================================
# 保存
# ============================================================

def save_data(
    df
):

    df.to_csv(

        OUTPUT_FILE,

        index=False,

        encoding="utf-8-sig"

    )


# ============================================================
# 表示
# ============================================================

def print_results(
    df
):

    print()

    print(
        "============================================================"
    )

    print(
        "研究比較用フェーズ分類"
    )

    print(
        "============================================================"
    )

    print()

    print(
        "注意:"
    )

    print(
        "この分類は動画内の時間位置による分類です。"
    )

    print(
        "加速局面・最大速度局面を直接判定したものではありません。"
    )

    print()


    stats = calculate_phase_statistics(
        df
    )


    for _, row in stats.iterrows():

        print(
            f"【{row['temporal_phase']}】"
        )

        print(
            f"  ステップ数: "
            f"{int(row['step_count'])}"
        )


        if (
            "average_stride_time_sec"
            in row
            and pd.notna(
                row[
                    "average_stride_time_sec"
                ]
            )
        ):

            print(
                f"  平均1歩時間: "
                f"{row['average_stride_time_sec']:.3f} 秒"
            )


        if (
            "average_step_rate_steps_per_sec"
            in row
            and pd.notna(
                row[
                    "average_step_rate_steps_per_sec"
                ]
            )
        ):

            print(
                f"  平均ピッチ: "
                f"{row['average_step_rate_steps_per_sec']:.2f} steps/s"
            )


        if (
            "left_knee_mean_deg"
            in row
            and pd.notna(
                row[
                    "left_knee_mean_deg"
                ]
            )
        ):

            print(
                f"  左膝平均: "
                f"{row['left_knee_mean_deg']:.2f}°"
            )


        if (
            "right_knee_mean_deg"
            in row
            and pd.notna(
                row[
                    "right_knee_mean_deg"
                ]
            )
        ):

            print(
                f"  右膝平均: "
                f"{row['right_knee_mean_deg']:.2f}°"
            )


        print()


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
        "研究比較フェーズマッチング"
    )

    print(
        "============================================================"
    )


    df = load_data()


    print(
        f"分析対象: {len(df)}ステップ"
    )


    df = create_time_information(
        df
    )


    df = assign_temporal_phase(
        df
    )


    save_data(
        df
    )


    print_results(
        df
    )


    print(
        f"保存先: {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    run()