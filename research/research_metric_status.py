import pandas as pd
from pathlib import Path


# ============================================================
# SprintAnalysisAI
# 研究比較指標ステータス
#
# 目的:
#   現在のSprintAnalysisAIで
#   「何を測定できるのか」
#   「何がまだ測定できないのか」
#   「研究比較に使えるのか」
#   を明確にする。
# ============================================================


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
)

INPUT_FILE = (
    DATA_DIR /
    "research_candidate_steps.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "research_metric_status.csv"
)


# ============================================================
# 研究指標
# ============================================================

METRICS = [

    {
        "metric": "step_rate",
        "display_name": "ステップ率",
        "column": "step_rate_steps_per_sec",
        "status": "測定可能",
        "research_relevance": "高",
        "description":
            "1秒あたりのステップ数"
    },

    {
        "metric": "stride_time",
        "display_name": "1歩時間",
        "column": "stride_time_sec",
        "status": "測定可能",
        "research_relevance": "高",
        "description":
            "接地イベント間の時間"
    },

    {
        "metric": "knee_angle",
        "display_name": "膝関節角度",
        "column": "current_left_knee",
        "status": "測定可能",
        "research_relevance": "中",
        "description":
            "接地イベント時の膝関節角度"
    },

    {
        "metric": "hip_angle",
        "display_name": "股関節角度",
        "column": "current_left_hip",
        "status": "測定可能",
        "research_relevance": "中",
        "description":
            "接地イベント時の股関節角度"
    },

    {
        "metric": "ankle_angle",
        "display_name": "足関節角度",
        "column": "current_left_ankle",
        "status": "測定可能",
        "research_relevance": "中",
        "description":
            "接地イベント時の足関節角度"
    },

    {
        "metric": "thigh_angle",
        "display_name": "大腿角度",
        "column": "current_left_thigh_angle",
        "status": "測定可能",
        "research_relevance": "中",
        "description":
            "大腿部の角度"
    },

    {
        "metric": "trunk_angle",
        "display_name": "体幹角度",
        "column": "current_trunk_angle",
        "status": "測定可能",
        "research_relevance": "中",
        "description":
            "骨盤中心と肩中心を結んだ体幹角度"
    },

    {
        "metric": "pelvis_angle",
        "display_name": "骨盤角度",
        "column": "current_pelvis_angle",
        "status": "測定可能",
        "research_relevance": "中",
        "description":
            "左右股関節を結んだ骨盤角度"
    },

    {
        "metric": "stride_length",
        "display_name": "ストライド長",
        "column": None,
        "status": "未測定",
        "research_relevance": "高",
        "description":
            "現在のカメラ条件では絶対距離として測定していない"
    },

    {
        "metric": "step_length",
        "display_name": "ステップ長",
        "column": None,
        "status": "未測定",
        "research_relevance": "高",
        "description":
            "現在は画像座標上の移動量のみで絶対距離を取得していない"
    },

    {
        "metric": "ground_contact_time",
        "display_name": "接地時間",
        "column": None,
        "status": "未測定",
        "research_relevance": "高",
        "description":
            "現在の接地イベント検出だけでは正確な接地時間を算出していない"
    },

    {
        "metric": "flight_time",
        "display_name": "滞空時間",
        "column": None,
        "status": "未測定",
        "research_relevance": "高",
        "description":
            "現在は接地時間との明確な境界を設定していない"
    },

    {
        "metric": "vertical_foot_velocity",
        "display_name": "足部鉛直速度",
        "column": None,
        "status": "未測定",
        "research_relevance": "高",
        "description":
            "足部位置の時間微分としての研究用指標は未実装"
    },

    {
        "metric": "hip_extension_angular_velocity",
        "display_name": "股関節伸展角速度",
        "column": None,
        "status": "未測定",
        "research_relevance": "高",
        "description":
            "股関節角度の時間変化率として未実装"
    },

    {
        "metric": "maximum_thigh_extension",
        "display_name": "最大大腿伸展",
        "column": None,
        "status": "未測定",
        "research_relevance": "中",
        "description":
            "最大値を局面内から抽出する処理が未実装"
    },

    {
        "metric": "maximum_thigh_flexion",
        "display_name": "最大大腿屈曲",
        "column": None,
        "status": "未測定",
        "research_relevance": "中",
        "description":
            "最大値を局面内から抽出する処理が未実装"
    },

    {
        "metric": "lower_limb_deformation",
        "display_name": "下肢変形",
        "column": None,
        "status": "未測定",
        "research_relevance": "低",
        "description":
            "現在の2D動画骨格解析だけでは研究レベルの評価は困難"
    },

    {
        "metric": "stiffness",
        "display_name": "脚部スティフネス",
        "column": None,
        "status": "未測定",
        "research_relevance": "高",
        "description":
            "力データ等を必要とするため現在の構成では未測定"
    },

]


# ============================================================
# 入力確認
# ============================================================

def load_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"{INPUT_FILE} がありません。"
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    return df


# ============================================================
# 実際に列が存在するか確認
# ============================================================

def check_measurement_status():

    candidate_df = load_data()

    columns = set(
        candidate_df.columns
    )

    results = []

    for metric in METRICS:

        item = metric.copy()

        column = item["column"]

        if column is not None:

            if column in columns:

                item[
                    "actual_column_exists"
                ] = True

            else:

                item[
                    "actual_column_exists"
                ] = False

        else:

            item[
                "actual_column_exists"
            ] = False

        results.append(
            item
        )

    return pd.DataFrame(
        results
    )


# ============================================================
# 保存
# ============================================================

def save_results(df):

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
# 表示
# ============================================================

def print_summary(df):

    print()
    print(
        "=============================="
    )

    print(
        "研究比較指標ステータス"
    )

    print(
        "=============================="
    )

    measurable = df[
        df["status"]
        == "測定可能"
    ]

    unavailable = df[
        df["status"]
        == "未測定"
    ]

    print(
        f"測定可能: {len(measurable)}"
    )

    print(
        f"未測定: {len(unavailable)}"
    )

    print()

    print(
        "【現在測定可能】"
    )

    for _, row in measurable.iterrows():

        print(
            f"  ○ {row['display_name']}"
            f" | 研究重要度: "
            f"{row['research_relevance']}"
        )

    print()

    print(
        "【現在未測定】"
    )

    for _, row in unavailable.iterrows():

        print(
            f"  - {row['display_name']}"
            f" | 研究重要度: "
            f"{row['research_relevance']}"
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
        "研究比較指標ステータス分析"
    )

    print(
        "============================================================"
    )

    df = check_measurement_status()

    save_results(
        df
    )

    print_summary(
        df
    )


if __name__ == "__main__":

    run()