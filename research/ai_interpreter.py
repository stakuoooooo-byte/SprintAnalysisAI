from pathlib import Path
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "research_pipeline.csv"
OUTPUT_FILE = DATA_DIR / "ai_evaluation.csv"


def load_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"{INPUT_FILE} がありません"
        )

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError(
            "research_pipeline.csv が空です"
        )

    return df


def get_value(df, metric):

    rows = df[
        df["metric"] == metric
    ]

    if rows.empty:
        return None

    value = rows.iloc[0]["value"]

    if pd.isna(value):
        return None

    return float(value)


def create_evaluation(df):

    results = []


    # ==================================================
    # ピッチ
    # ==================================================

    pitch = get_value(
        df,
        "step_rate"
    )

    if pitch is not None:

        results.append({
            "priority": 1,
            "metric": "step_rate",
            "value": pitch,
            "finding":
                f"今回の分析ではピッチは {pitch:.2f} steps/s でした。",
            "research_interpretation":
                "ステップレートはスプリントパフォーマンスを構成する主要な指標の一つとして研究されています。",
            "improvement_point":
                "ピッチだけを単独で上げるのではなく、1歩時間やストライドとの関係を確認しながら改善を検討します。",
            "recommended_drill":
                "短距離のリズム走・接地リズムドリル"
        })


    # ==================================================
    # 1歩時間
    # ==================================================

    stride = get_value(
        df,
        "stride_time"
    )

    if stride is not None:

        results.append({
            "priority": 2,
            "metric": "stride_time",
            "value": stride,
            "finding":
                f"研究比較候補ステップの平均1歩時間は {stride:.3f} 秒でした。",
            "research_interpretation":
                "ストライド時間はステップレートやスプリント速度と関係する重要な時間指標です。",
            "improvement_point":
                "1歩時間だけで良否を決めず、ピッチ・接地・空中局面などと合わせて評価します。",
            "recommended_drill":
                "高速リズム走・短距離スプリント"
        })


    # ==================================================
    # 膝角度
    # ==================================================

    knee = get_value(
        df,
        "knee_angle"
    )

    if knee is not None:

        results.append({
            "priority": 3,
            "metric": "knee_angle",
            "value": knee,
            "finding":
                f"接地関連データから算出した膝角度の平均値は {knee:.1f}° でした。",
            "research_interpretation":
                "膝角度はスプリント動作を評価する際に研究対象となるキネマティック指標です。",
            "improvement_point":
                "単一の角度を理想値と比較するのではなく、速度局面・接地タイミング・左右差と組み合わせて確認します。",
            "recommended_drill":
                "Aスキップ・ドリブル走・短距離フォーム走"
        })


    # ==================================================
    # 左右差
    # ==================================================

    asymmetry = get_value(
        df,
        "knee_asymmetry"
    )

    if asymmetry is not None:

        results.append({
            "priority": 4,
            "metric": "knee_asymmetry",
            "value": asymmetry,
            "finding":
                f"左右膝角度の平均差は {asymmetry:.1f}° でした。",
            "research_interpretation":
                "左右差は観察すべき情報ですが、左右差だけからフォームの良否を断定することはできません。",
            "improvement_point":
                "左右差が一貫して現れるかを確認し、動画上の接地・離地・脚の振り出しと合わせて評価します。",
            "recommended_drill":
                "左右交互のドリル・片脚リズムドリル"
        })


    return pd.DataFrame(
        results
    )


def add_overall_summary(df):

    if df.empty:
        return df

    messages = []

    for _, row in df.iterrows():

        messages.append(
            f"{row['priority']}. "
            f"{row['improvement_point']}"
        )

    overall = (
        "今回の分析では、測定できた指標を研究上の知見と照合し、"
        "改善候補を抽出しました。"
        "ただし、動画から取得できない指標や研究条件が一致しない指標については、"
        "断定的な評価を行っていません。"
    )

    df["overall_summary"] = overall

    return df


def run():

    print(
        "=============================================="
    )

    print(
        "SprintAnalysisAI AI Interpreter"
    )

    print(
        "=============================================="
    )

    df = load_data()

    result = create_evaluation(
        df
    )

    result = add_overall_summary(
        result
    )

    if result.empty:

        print(
            "AI評価を作成できるデータがありません。"
        )

        return

    result.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        "【AI評価】"
    )

    for _, row in result.iterrows():

        print(
            f"\n[{int(row['priority'])}] "
            f"{row['metric']}"
        )

        print(
            f"観測: {row['finding']}"
        )

        print(
            f"研究: {row['research_interpretation']}"
        )

        print(
            f"改善: {row['improvement_point']}"
        )

        print(
            f"ドリル: {row['recommended_drill']}"
        )

    print()
    print(
        f"保存完了: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    run()