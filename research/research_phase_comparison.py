import pandas as pd
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 研究局面比較
#
# 目的:
#   研究論文の対象局面と、
#   現在の動画データの局面情報を比較する。
#
# 重要:
#   動画を5分割しただけでは
#   「最大速度局面」とは判定しない。
#
#   研究と動画の条件が十分に揃っていない場合は
#   「比較条件不足」とする。
# ============================================================


BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

DATA_DIR = BASE_DIR / "data"
RESEARCH_DIR = BASE_DIR / "research"


PHASE_FILE = (
    DATA_DIR /
    "research_phase_matching.csv"
)

REFERENCES_FILE = (
    RESEARCH_DIR /
    "references.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "research_phase_comparison.csv"
)


# ============================================================
# 研究局面の定義
# ============================================================

RESEARCH_PHASES = {

    "max_velocity": {
        "display_name": "最大速度局面",
        "requires":
            "最大速度局面であることを確認できる情報が必要"
    },

    "acceleration": {
        "display_name": "加速局面",
        "requires":
            "加速局面であることを確認できる情報が必要"
    },

    "general_sprinting": {
        "display_name": "一般的なスプリント",
        "requires":
            "研究条件に応じた比較"
    },

    "block_start": {
        "display_name": "ブロックスタート",
        "requires":
            "ブロックスタート条件が必要"
    },

}


# ============================================================
# ファイル読み込み
# ============================================================

def load_files():

    if not PHASE_FILE.exists():

        raise FileNotFoundError(
            f"{PHASE_FILE} がありません。"
        )

    if not REFERENCES_FILE.exists():

        raise FileNotFoundError(
            f"{REFERENCES_FILE} がありません。"
        )

    phase_df = pd.read_csv(
        PHASE_FILE
    )

    references_df = pd.read_csv(
        REFERENCES_FILE
    )

    return (
        phase_df,
        references_df
    )


# ============================================================
# 動画側の局面情報
# ============================================================

def summarize_video_phase(
    phase_df
):

    results = []

    for phase in phase_df[
        "temporal_phase"
    ].dropna().unique():

        phase_data = phase_df[
            phase_df[
                "temporal_phase"
            ] == phase
        ]

        result = {

            "video_phase":
                str(phase),

            "step_count":
                len(phase_data),

            "phase_verified":
                False,

            "phase_verification_status":
                "時間位置による分類のみ",

        }

        results.append(
            result
        )

    return pd.DataFrame(
        results
    )


# ============================================================
# 研究側の局面を整理
# ============================================================

def summarize_research_phase(
    references_df
):

    results = []

    for _, row in references_df.iterrows():

        phase = row.get(
            "phase",
            ""
        )

        results.append({

            "reference_id":
                row.get(
                    "reference_id",
                    ""
                ),

            "author_year":
                row.get(
                    "author_year",
                    ""
                ),

            "research_phase":
                phase,

            "athletes":
                row.get(
                    "athletes",
                    ""
                ),

            "condition":
                row.get(
                    "condition",
                    ""
                ),

            "metric":
                row.get(
                    "metric",
                    ""
                ),

            "relationship":
                row.get(
                    "relationship",
                    ""
                ),

        })

    return pd.DataFrame(
        results
    )


# ============================================================
# 比較可能性判定
# ============================================================

def determine_comparability(
    research_phase
):

    # --------------------------------------------------------
    # 最大速度局面
    # --------------------------------------------------------

    if research_phase == "max_velocity":

        return (
            "比較条件不足",
            "研究は最大速度局面を対象としているが、"
            "現在の動画では最大速度局面を独立して確認していない"
        )


    # --------------------------------------------------------
    # 加速局面
    # --------------------------------------------------------

    if research_phase == "acceleration":

        return (
            "比較条件不足",
            "研究は加速局面を対象としているが、"
            "現在の動画では加速局面を独立して確認していない"
        )


    # --------------------------------------------------------
    # ブロックスタート
    # --------------------------------------------------------

    if research_phase == "block_start":

        return (
            "比較不可",
            "現在の分析対象は通常走であり、"
            "ブロックスタート条件を確認していない"
        )


    # --------------------------------------------------------
    # 一般的なスプリント
    # --------------------------------------------------------

    if research_phase == "general_sprinting":

        return (
            "条件確認が必要",
            "研究対象条件と動画条件を確認してから比較する"
        )


    return (
        "比較条件不足",
        "研究局面を特定できない"
    )


# ============================================================
# 比較表作成
# ============================================================

def build_comparison(
    references_df
):

    results = []

    for _, row in references_df.iterrows():

        (
            status,
            reason
        ) = determine_comparability(
            row["research_phase"]
        )

        results.append({

            "reference_id":
                row["reference_id"],

            "author_year":
                row["author_year"],

            "research_phase":
                row["research_phase"],

            "athletes":
                row["athletes"],

            "condition":
                row["condition"],

            "metric":
                row["metric"],

            "relationship":
                row["relationship"],

            "comparison_status":
                status,

            "comparison_reason":
                reason,

        })

    return pd.DataFrame(
        results
    )


# ============================================================
# 保存
# ============================================================

def save_results(
    df
):

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        f"保存完了: {OUTPUT_FILE}"
    )


# ============================================================
# 結果表示
# ============================================================

def print_results(
    df
):

    print()
    print(
        "============================================================"
    )

    print(
        "研究局面比較結果"
    )

    print(
        "============================================================"
    )

    print()

    counts = (
        df[
            "comparison_status"
        ]
        .value_counts()
    )

    for status, count in counts.items():

        print(
            f"{status}: {count}"
        )

    print()

    for _, row in df.iterrows():

        print(
            f"[{row['reference_id']}] "
            f"{row['author_year']}"
        )

        print(
            f"  研究局面: "
            f"{row['research_phase']}"
        )

        print(
            f"  指標: "
            f"{row['metric']}"
        )

        print(
            f"  比較状態: "
            f"{row['comparison_status']}"
        )

        print(
            f"  理由: "
            f"{row['comparison_reason']}"
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
        "研究局面比較システム"
    )

    print(
        "============================================================"
    )

    (
        phase_df,
        references_df
    ) = load_files()


    print(
        f"動画データ: "
        f"{len(phase_df)}ステップ"
    )

    print(
        f"研究データ: "
        f"{len(references_df)}件"
    )


    # --------------------------------------------------------
    # 動画側
    # --------------------------------------------------------

    video_phase = summarize_video_phase(
        phase_df
    )


    print()

    print(
        "動画側フェーズ:"
    )

    for _, row in video_phase.iterrows():

        print(
            f"  {row['video_phase']}: "
            f"{row['step_count']}ステップ"
        )


    # --------------------------------------------------------
    # 研究側
    # --------------------------------------------------------

    research_phase = summarize_research_phase(
        references_df
    )


    # --------------------------------------------------------
    # 比較可能性
    # --------------------------------------------------------

    comparison = build_comparison(
        research_phase
    )


    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    save_results(
        comparison
    )


    # --------------------------------------------------------
    # 表示
    # --------------------------------------------------------

    print_results(
        comparison
    )


if __name__ == "__main__":

    run()