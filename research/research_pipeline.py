from pathlib import Path
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CANDIDATE_FILE = DATA_DIR / "research_candidate_steps.csv"
METRIC_FILE = DATA_DIR / "research_metric_comparison.csv"
PHASE_FILE = DATA_DIR / "research_phase_comparison.csv"
OUTPUT_FILE = DATA_DIR / "research_pipeline.csv"


def safe_mean(df, column):
    if column not in df.columns:
        return np.nan

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    if len(values) == 0:
        return np.nan

    return values.mean()


def load_candidates():
    if not CANDIDATE_FILE.exists():
        raise FileNotFoundError(
            f"{CANDIDATE_FILE} がありません"
        )

    return pd.read_csv(CANDIDATE_FILE)


def build_summary(df):

    result = {}

    result["candidate_step_count"] = len(df)

    result["step_rate_mean"] = safe_mean(
        df,
        "step_rate"
    )

    result["stride_time_mean"] = safe_mean(
        df,
        "stride_time_sec"
    )

    # 左右の膝角度
    knee_values = []

    for column in [
        "previous_left_knee",
        "previous_right_knee",
        "current_left_knee",
        "current_right_knee",
    ]:
        if column in df.columns:
            values = pd.to_numeric(
                df[column],
                errors="coerce"
            ).dropna()

            knee_values.extend(
                values.tolist()
            )

    result["knee_angle_mean"] = (
        np.mean(knee_values)
        if knee_values
        else np.nan
    )

    # 左右差
    if (
        "previous_left_knee" in df.columns
        and
        "previous_right_knee" in df.columns
    ):

        left = pd.to_numeric(
            df["previous_left_knee"],
            errors="coerce"
        )

        right = pd.to_numeric(
            df["previous_right_knee"],
            errors="coerce"
        )

        diff = (
            left - right
        ).abs()

        result["knee_asymmetry_mean"] = (
            diff.mean()
        )

    else:

        result["knee_asymmetry_mean"] = np.nan

    return result


def research_status():

    if not METRIC_FILE.exists():
        return "研究比較データなし"

    df = pd.read_csv(
        METRIC_FILE
    )

    if "interpretation_status" not in df.columns:
        return "研究比較情報あり"

    statuses = (
        df["interpretation_status"]
        .dropna()
        .astype(str)
        .tolist()
    )

    if "実測値あり・研究情報あり" in statuses:
        return "研究情報と実測値を照合"

    if "実測値あり・研究情報なし" in statuses:
        return "実測値あり・研究情報限定"

    return "比較条件確認中"


def phase_status():

    if not PHASE_FILE.exists():
        return "局面比較データなし"

    df = pd.read_csv(
        PHASE_FILE
    )

    if "comparison_status" not in df.columns:
        return "局面情報あり"

    statuses = (
        df["comparison_status"]
        .dropna()
        .astype(str)
        .tolist()
    )

    if "比較条件不足" in statuses:
        return "局面条件不足"

    return "局面比較情報あり"


def build_evaluation(summary):

    evaluations = []

    # --------------------------------------------------
    # ピッチ
    # --------------------------------------------------

    pitch = summary[
        "step_rate_mean"
    ]

    if pd.notna(pitch):

        evaluations.append({
            "metric": "step_rate",
            "value": pitch,
            "status": "実測値あり",
            "interpretation":
                "スプリントに関係する主要なステップ指標として研究比較対象にする"
        })


    # --------------------------------------------------
    # ストライド時間
    # --------------------------------------------------

    stride = summary[
        "stride_time_mean"
    ]

    if pd.notna(stride):

        evaluations.append({
            "metric": "stride_time",
            "value": stride,
            "status": "実測値あり",
            "interpretation":
                "1歩時間を研究比較用の基礎指標として扱う"
        })


    # --------------------------------------------------
    # 膝角度
    # --------------------------------------------------

    knee = summary[
        "knee_angle_mean"
    ]

    if pd.notna(knee):

        evaluations.append({
            "metric": "knee_angle",
            "value": knee,
            "status": "実測値あり",
            "interpretation":
                "膝角度はスプリント動作の研究比較対象として扱う"
        })


    # --------------------------------------------------
    # 左右差
    # --------------------------------------------------

    asymmetry = summary[
        "knee_asymmetry_mean"
    ]

    if pd.notna(asymmetry):

        evaluations.append({
            "metric": "knee_asymmetry",
            "value": asymmetry,
            "status": "観察値",
            "interpretation":
                "左右差の存在を確認する。ただし左右差だけでフォームの良否を断定しない"
        })


    return pd.DataFrame(
        evaluations
    )


def run():

    print(
        "=============================================="
    )

    print(
        "SprintAnalysisAI Research Pipeline"
    )

    print(
        "=============================================="
    )


    df = load_candidates()

    print(
        f"研究比較候補ステップ: {len(df)}"
    )


    summary = build_summary(
        df
    )


    print()
    print("【実測値】")

    for key, value in summary.items():

        if isinstance(value, float):

            if pd.isna(value):
                print(
                    f"{key}: データなし"
                )

            else:
                print(
                    f"{key}: {value:.3f}"
                )

        else:

            print(
                f"{key}: {value}"
            )


    print()
    print(
        "【研究比較】"
    )

    print(
        research_status()
    )


    print()
    print(
        "【局面比較】"
    )

    print(
        phase_status()
    )


    evaluation = build_evaluation(
        summary
    )


    if evaluation.empty:

        print()
        print(
            "評価可能な指標がありません"
        )

        return


    # 全結果に共通情報を追加
    evaluation[
        "research_status"
    ] = research_status()

    evaluation[
        "phase_status"
    ] = phase_status()


    evaluation.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    print()
    print(
        "【評価結果】"
    )

    print(
        evaluation[
            [
                "metric",
                "value",
                "status",
                "interpretation"
            ]
        ].to_string(
            index=False
        )
    )


    print()
    print(
        f"保存完了: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    run()