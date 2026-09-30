import pandas as pd
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 研究指標比較
#
# 目的:
#   実測できている指標と研究データベースを接続する。
#
# 重要:
#   「研究で関連が報告されている」
#   と
#   「この選手が良い / 悪い」
#   は別物として扱う。
# ============================================================


BASE_DIR = (
    Path(__file__).resolve().parent.parent
)

DATA_DIR = BASE_DIR / "data"
RESEARCH_DIR = BASE_DIR / "research"


CANDIDATE_FILE = (
    DATA_DIR /
    "research_candidate_steps.csv"
)

METRIC_STATUS_FILE = (
    DATA_DIR /
    "research_metric_status.csv"
)

REFERENCES_FILE = (
    RESEARCH_DIR /
    "references.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "research_metric_comparison.csv"
)


# ============================================================
# 現在のデータで取得する代表値
# ============================================================

METRIC_COLUMNS = {

    "step_rate":
        "step_rate_steps_per_sec",

    "stride_time":
        "stride_time_sec",

    "knee_angle":
        "current_left_knee",

    "hip_angle":
        "current_left_hip",

    "ankle_angle":
        "current_left_ankle",

    "thigh_angle":
        "current_left_thigh_angle",

    "trunk_angle":
        "current_trunk_angle",

    "pelvis_angle":
        "current_pelvis_angle",

}


# ============================================================
# ファイル読み込み
# ============================================================

def load_files():

    if not CANDIDATE_FILE.exists():

        raise FileNotFoundError(
            f"{CANDIDATE_FILE} がありません。"
        )

    if not METRIC_STATUS_FILE.exists():

        raise FileNotFoundError(
            f"{METRIC_STATUS_FILE} がありません。"
        )

    if not REFERENCES_FILE.exists():

        raise FileNotFoundError(
            f"{REFERENCES_FILE} がありません。"
        )

    candidate_df = pd.read_csv(
        CANDIDATE_FILE
    )

    status_df = pd.read_csv(
        METRIC_STATUS_FILE
    )

    references_df = pd.read_csv(
        REFERENCES_FILE
    )

    return (
        candidate_df,
        status_df,
        references_df
    )


# ============================================================
# 実測値を集計
# ============================================================

def calculate_measured_values(
    candidate_df
):

    results = []

    for metric, column in METRIC_COLUMNS.items():

        if column not in candidate_df.columns:

            continue

        values = pd.to_numeric(
            candidate_df[column],
            errors="coerce"
        ).dropna()

        if values.empty:

            continue

        results.append({

            "metric":
                metric,

            "measured":
                True,

            "sample_count":
                len(values),

            "mean":
                values.mean(),

            "std":
                values.std(),

            "minimum":
                values.min(),

            "maximum":
                values.max(),

        })

    return pd.DataFrame(
        results
    )


# ============================================================
# 研究データベースを整理
# ============================================================

def summarize_references(
    references_df
):

    results = []

    for metric in references_df[
        "metric"
    ].dropna().unique():

        rows = references_df[
            references_df["metric"]
            == metric
        ]

        references = []

        for _, row in rows.iterrows():

            references.append(
                (
                    f"{row['reference_id']}: "
                    f"{row['author_year']} / "
                    f"{row['phase']} / "
                    f"{row['athletes']} / "
                    f"{row['condition']} / "
                    f"{row['relationship']}"
                )
            )

        results.append({

            "metric":
                metric,

            "research_reference_count":
                len(rows),

            "research_summary":
                " || ".join(
                    references
                ),

        })

    return pd.DataFrame(
        results
    )


# ============================================================
# 実測値と研究情報を結合
# ============================================================

def build_comparison(
    measured_df,
    reference_summary_df,
    status_df
):

    comparison = status_df[
        [
            "metric",
            "display_name",
            "status",
            "research_relevance",
            "description",
        ]
    ].copy()


    # --------------------------------------------------------
    # 実測値
    # --------------------------------------------------------

    comparison = comparison.merge(

        measured_df,

        on="metric",

        how="left"

    )


    # --------------------------------------------------------
    # 研究情報
    # --------------------------------------------------------

    comparison = comparison.merge(

        reference_summary_df,

        on="metric",

        how="left"

    )


    # --------------------------------------------------------
    # 欠損処理
    # --------------------------------------------------------

    comparison[
        "measured"
    ] = comparison[
        "measured"
    ].fillna(False)


    comparison[
        "research_reference_count"
    ] = comparison[
        "research_reference_count"
    ].fillna(0).astype(int)


    comparison[
        "research_summary"
    ] = comparison[
        "research_summary"
    ].fillna(
        "登録された研究情報なし"
    )


    return comparison


# ============================================================
# AI解釈用ステータス
# ============================================================

def add_interpretation_status(
    df
):

    statuses = []

    for _, row in df.iterrows():

        measured = bool(
            row["measured"]
        )

        references = int(
            row[
                "research_reference_count"
            ]
        )

        if (
            measured
            and references > 0
        ):

            status = (
                "実測値あり・研究情報あり"
            )

        elif (
            measured
            and references == 0
        ):

            status = (
                "実測値あり・研究情報なし"
            )

        elif (
            not measured
            and references > 0
        ):

            status = (
                "研究情報あり・現在未測定"
            )

        else:

            status = (
                "比較材料不足"
            )

        statuses.append(
            status
        )

    df[
        "interpretation_status"
    ] = statuses

    return df


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
        "研究比較データ"
    )

    print(
        "============================================================"
    )

    for _, row in df.iterrows():

        print()

        print(
            f"【{row['display_name']}】"
        )

        print(
            f"指標: {row['metric']}"
        )

        print(
            f"状態: "
            f"{row['interpretation_status']}"
        )

        if bool(row["measured"]):

            print(
                f"平均: "
                f"{row['mean']:.3f}"
            )

            print(
                f"SD: "
                f"{row['std']:.3f}"
            )

            print(
                f"n: "
                f"{int(row['sample_count'])}"
            )

        print(
            f"研究登録数: "
            f"{int(row['research_reference_count'])}"
        )

        print(
            f"研究情報: "
            f"{row['research_summary']}"
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
        "研究指標比較システム"
    )

    print(
        "============================================================"
    )


    (
        candidate_df,
        status_df,
        references_df
    ) = load_files()


    print(
        f"分析対象ステップ: "
        f"{len(candidate_df)}"
    )


    # --------------------------------------------------------
    # 実測値
    # --------------------------------------------------------

    measured_df = calculate_measured_values(
        candidate_df
    )


    # --------------------------------------------------------
    # 研究情報
    # --------------------------------------------------------

    reference_summary_df = summarize_references(
        references_df
    )


    # --------------------------------------------------------
    # 結合
    # --------------------------------------------------------

    comparison = build_comparison(

        measured_df,

        reference_summary_df,

        status_df

    )


    # --------------------------------------------------------
    # AI解釈用状態
    # --------------------------------------------------------

    comparison = add_interpretation_status(
        comparison
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