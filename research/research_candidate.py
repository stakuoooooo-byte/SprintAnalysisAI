import pandas as pd
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 研究比較用データ抽出
#
# 目的:
#   stride_quality.csv の中から
#   測定品質が「研究比較候補」のデータだけを抽出する。
#
# 注意:
#   ここではフォームの良し悪しを評価しない。
#   あくまで「研究比較に使用する測定データ」の選別。
# ============================================================


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
)

INPUT_FILE = (
    DATA_DIR /
    "stride_quality.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "research_candidate_steps.csv"
)


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
            "stride_quality.csv が空です。"
        )

    return df


def extract_candidates(df):

    # --------------------------------------------------------
    # 「研究比較候補」のみ抽出
    # --------------------------------------------------------

    candidates = df[
        df[
            "measurement_quality"
        ] == "研究比較候補"
    ].copy()

    return candidates


def add_candidate_id(df):

    # 元データのstep番号を保持
    if "step_index" in df.columns:

        df[
            "research_candidate_id"
        ] = (
            "candidate_"
            + df["step_index"].astype(str)
        )

    else:

        df[
            "research_candidate_id"
        ] = [
            f"candidate_{i + 1}"
            for i in range(len(df))
        ]

    return df


def calculate_summary(df):

    print()
    print(
        "=============================="
    )

    print(
        "研究比較用データ"
    )

    print(
        "=============================="
    )

    print(
        f"候補データ数: {len(df)}"
    )

    if df.empty:

        print(
            "研究比較候補がありません。"
        )

        return


    # --------------------------------------------------------
    # 1歩時間
    # --------------------------------------------------------

    if "stride_time_sec" in df.columns:

        print(
            f"平均1歩時間: "
            f"{df['stride_time_sec'].mean():.3f} 秒"
        )

        print(
            f"最短1歩時間: "
            f"{df['stride_time_sec'].min():.3f} 秒"
        )

        print(
            f"最長1歩時間: "
            f"{df['stride_time_sec'].max():.3f} 秒"
        )


    # --------------------------------------------------------
    # ピッチ
    # --------------------------------------------------------

    if "step_rate_steps_per_sec" in df.columns:

        print(
            f"平均ピッチ: "
            f"{df['step_rate_steps_per_sec'].mean():.2f} steps/s"
        )

        print(
            f"平均ピッチ: "
            f"{df['step_rate_steps_per_sec'].mean() * 60:.1f} steps/min"
        )


    # --------------------------------------------------------
    # 左右
    # --------------------------------------------------------

    if "previous_knee_absolute_difference_deg" in df.columns:

        print(
            f"平均膝左右差: "
            f"{df['previous_knee_absolute_difference_deg'].mean():.2f}°"
        )


def save_data(df):

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        f"保存完了: {OUTPUT_FILE}"
    )


def run():

    print(
        "============================================================"
    )

    print(
        "SprintAnalysisAI"
    )

    print(
        "研究比較用データ抽出"
    )

    print(
        "============================================================"
    )

    # --------------------------------------------------------
    # 読み込み
    # --------------------------------------------------------

    df = load_data()

    print(
        f"元データ: {len(df)}ステップ"
    )

    # --------------------------------------------------------
    # 候補抽出
    # --------------------------------------------------------

    candidates = extract_candidates(
        df
    )

    # --------------------------------------------------------
    # ID追加
    # --------------------------------------------------------

    candidates = add_candidate_id(
        candidates
    )

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    save_data(
        candidates
    )

    # --------------------------------------------------------
    # 統計
    # --------------------------------------------------------

    calculate_summary(
        candidates
    )


if __name__ == "__main__":

    run()