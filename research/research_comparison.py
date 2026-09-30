from pathlib import Path
import pandas as pd
import numpy as np

from research.research_database import load_references


DATA_DIR = Path("data")


# ============================================================
# データ読み込み
# ============================================================

def load_csv(name):

    path = DATA_DIR / name

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


def load_form_evaluation():

    return load_csv(
        "form_evaluation.csv"
    ).iloc[0]


def load_performance_summary():

    return load_csv(
        "performance_summary.csv"
    ).iloc[0]


# ============================================================
# 実測値と研究指標の対応表
# ============================================================

METRIC_MAPPING = {

    # ----------------------------------------
    # ステップ・ストライド
    # ----------------------------------------

    "step_rate": {
        "source": "performance",
        "column": "pitch_steps_per_sec",
        "unit": "steps/s",
    },

    "stride_time": {
        "source": "performance",
        "column": "average_stride_time_sec",
        "unit": "s",
    },

    # ----------------------------------------
    # 膝
    # ----------------------------------------

    "knee_angle": {
        "source": "form",
        "columns": [
            "left_knee_avg",
            "right_knee_avg",
        ],
        "unit": "deg",
    },

    "knee_flexion": {
        "source": "form",
        "columns": [
            "left_knee_avg",
            "right_knee_avg",
        ],
        "unit": "deg",
    },

    # ----------------------------------------
    # 股関節
    # ----------------------------------------

    "hip_angle": {
        "source": "form",
        "columns": [
            "left_hip_avg",
            "right_hip_avg",
        ],
        "unit": "deg",
    },

    # ----------------------------------------
    # 足関節
    # ----------------------------------------

    "ankle_angle": {
        "source": "form",
        "columns": [
            "left_ankle_avg",
            "right_ankle_avg",
        ],
        "unit": "deg",
    },

    # ----------------------------------------
    # 大腿
    # ----------------------------------------

    "thigh_angle": {
        "source": "form",
        "columns": [
            "left_thigh_avg",
            "right_thigh_avg",
        ],
        "unit": "deg",
    },

    # ----------------------------------------
    # 体幹
    # ----------------------------------------

    "trunk_angle": {
        "source": "form",
        "column": "trunk_angle_avg",
        "unit": "deg",
    },

    # ----------------------------------------
    # 骨盤
    # ----------------------------------------

    "pelvis_angle": {
        "source": "form",
        "column": "pelvis_angle_avg",
        "unit": "deg",
    },

    # ----------------------------------------
    # 左右差
    # ----------------------------------------

    "left_right_asymmetry": {
        "source": "form",
        "columns": [
            "knee_difference_deg",
            "hip_difference_deg",
            "ankle_difference_deg",
            "thigh_difference_deg",
        ],
        "unit": "deg",
    },

    # ----------------------------------------
    # 現在未実装
    # ----------------------------------------

    "stride_length": {
        "source": None,
        "column": None,
        "unit": "m",
    },

    "step_length": {
        "source": None,
        "column": None,
        "unit": "m",
    },

    "ground_contact_time": {
        "source": None,
        "column": None,
        "unit": "s",
    },

    "flight_time": {
        "source": None,
        "column": None,
        "unit": "s",
    },

    "hip_extension_angular_velocity": {
        "source": None,
        "column": None,
        "unit": "deg/s",
    },

    "vertical_foot_velocity": {
        "source": None,
        "column": None,
        "unit": "m/s",
    },

    "lower_limb_deformation": {
        "source": None,
        "column": None,
        "unit": None,
    },

}


# ============================================================
# 数値処理
# ============================================================

def mean_columns(row, columns):

    values = []

    for column in columns:

        if column not in row.index:
            continue

        value = pd.to_numeric(
            row[column],
            errors="coerce"
        )

        if pd.notna(value):
            values.append(float(value))

    if not values:
        return np.nan

    return float(
        np.mean(values)
    )


def get_measured_value(
    metric,
    form,
    performance
):

    if metric not in METRIC_MAPPING:
        return np.nan

    mapping = METRIC_MAPPING[metric]

    source = mapping["source"]

    # ----------------------------------------
    # 未実装
    # ----------------------------------------

    if source is None:
        return np.nan

    # ----------------------------------------
    # 単一列
    # ----------------------------------------

    if "column" in mapping:

        column = mapping["column"]

        source_df = (
            form
            if source == "form"
            else performance
        )

        if column not in source_df.index:
            return np.nan

        value = pd.to_numeric(
            source_df[column],
            errors="coerce"
        )

        if pd.isna(value):
            return np.nan

        return float(value)

    # ----------------------------------------
    # 複数列の平均
    # ----------------------------------------

    if "columns" in mapping:

        source_df = (
            form
            if source == "form"
            else performance
        )

        return mean_columns(
            source_df,
            mapping["columns"]
        )

    return np.nan


# ============================================================
# 研究比較
# ============================================================

def build_comparison():

    form = load_form_evaluation()

    performance = load_performance_summary()

    references = load_references()

    results = []

    for metric in references[
        "metric"
    ].unique():

        metric_refs = references[
            references["metric"] == metric
        ]

        measurement = get_measured_value(
            metric,
            form,
            performance
        )

        measured = pd.notna(
            measurement
        )

        # ------------------------------------
        # 研究との関係
        # ------------------------------------

        relationships = "; ".join(
            metric_refs[
                "relationship"
            ]
            .astype(str)
            .unique()
        )

        phases = "; ".join(
            metric_refs[
                "phase"
            ]
            .astype(str)
            .unique()
        )

        conditions = "; ".join(
            metric_refs[
                "condition"
            ]
            .astype(str)
            .unique()
        )

        athletes = "; ".join(
            metric_refs[
                "athletes"
            ]
            .astype(str)
            .unique()
        )

        # ------------------------------------
        # 比較可能性
        # ------------------------------------

        if measured:

            status = (
                "測定値あり・研究指標と対応可能"
            )

        else:

            status = (
                "現在のシステムでは測定値なし"
            )

        results.append({

            "metric": metric,

            "measured": measured,

            "measurement_value": (
                measurement
                if measured
                else np.nan
            ),

            "unit": (
                METRIC_MAPPING
                .get(metric, {})
                .get("unit")
            ),

            "research_records":
                len(metric_refs),

            "research_relationship":
                relationships,

            "research_phase":
                phases,

            "research_condition":
                conditions,

            "research_population":
                athletes,

            "comparison_status":
                status,

        })

    return pd.DataFrame(
        results
    )


# ============================================================
# 保存
# ============================================================

def save_comparison(df):

    path = (
        DATA_DIR /
        "research_comparison.csv"
    )

    df.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )

    return path


# ============================================================
# コンソール表示
# ============================================================

def print_report(df):

    print(
        "\n【研究指標と実測値の対応】"
    )

    for _, row in df.iterrows():

        metric = row["metric"]

        if row["measured"]:

            value = row[
                "measurement_value"
            ]

            unit = row["unit"]

            print(
                f"✓ {metric}: "
                f"{value:.3f} {unit}"
            )

        else:

            print(
                f"－ {metric}: "
                f"測定値なし"
            )

    print(
        "\n【研究との関連】"
    )

    available = df[
        df["measured"] == True
    ]

    for _, row in available.iterrows():

        print(
            f"- {row['metric']}: "
            f"{row['research_relationship']}"
        )

    print(
        "\n【重要】"
    )

    print(
        "研究で関連が報告された指標と、"
        "「理想的なフォーム」は同じ意味ではありません。"
    )

    print(
        "そのため現段階では、"
        "研究との一致率を勝手に算出していません。"
    )


# ============================================================
# 実行
# ============================================================

def run():

    print("=" * 60)
    print("SprintAnalysisAI")
    print("研究比較エンジン")
    print("=" * 60)

    comparison = build_comparison()

    path = save_comparison(
        comparison
    )

    print_report(
        comparison
    )

    print(
        f"\n保存先: {path}"
    )

    return comparison


if __name__ == "__main__":

    run()