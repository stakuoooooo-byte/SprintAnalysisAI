from pathlib import Path
import pandas as pd


DATA_DIR = Path("data")


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


def build_athlete_profile():

    # ==========================================
    # パフォーマンスデータ
    # ==========================================

    performance = load_csv(
        "performance_summary.csv"
    ).iloc[0]

    # ==========================================
    # フォームデータ
    # ==========================================

    form = load_csv(
        "form_evaluation.csv"
    ).iloc[0]

    profile = {}

    # ==========================================
    # パフォーマンス
    # ==========================================

    performance_columns = [
        "total_contact_events",
        "left_contact_events",
        "right_contact_events",
        "event_duration_sec",
        "average_step_interval_sec",
        "minimum_step_interval_sec",
        "maximum_step_interval_sec",
        "pitch_steps_per_sec",
        "pitch_steps_per_min",
        "event_frequency_steps_per_sec",
        "left_average_contact_interval_sec",
        "right_average_contact_interval_sec",
        "left_right_difference_sec",
        "left_right_ratio",
        "average_stride_time_sec",
        "left_stride_image_displacement",
        "right_stride_image_displacement",
    ]

    for column in performance_columns:

        if column in performance.index:

            profile[column] = performance[column]

    # ==========================================
    # 接地フォーム
    # ==========================================

    form_columns = [
        "left_knee_avg",
        "right_knee_avg",

        "left_hip_avg",
        "right_hip_avg",

        "left_ankle_avg",
        "right_ankle_avg",

        "left_thigh_avg",
        "right_thigh_avg",

        "trunk_angle_avg",
        "pelvis_angle_avg",

        "knee_asymmetry_avg",
        "hip_asymmetry_avg",
        "ankle_asymmetry_avg",
        "thigh_asymmetry_avg",

        "contact_event_count",
        "valid_knee_samples",
        "valid_hip_samples",
        "valid_ankle_samples",
        "valid_thigh_samples",
    ]

    for column in form_columns:

        if column in form.index:

            profile[column] = form[column]

    # ==========================================
    # メタ情報
    # ==========================================

    profile["data_type"] = (
        "2D video pose analysis"
    )

    profile["camera_analysis"] = (
        "sagittal-plane oriented"
    )

    profile["research_match_rate"] = (
        "not_calculated"
    )

    profile["research_match_note"] = (
        "研究対象集団・速度・局面を揃えた"
        "基準値比較は未実装"
    )

    return pd.DataFrame([profile])


def save_profile(profile):

    path = (
        DATA_DIR /
        "athlete_profile.csv"
    )

    profile.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )

    return path


def run():

    print("=" * 60)
    print("SprintAnalysisAI")
    print("選手総合分析データ作成")
    print("=" * 60)

    profile = build_athlete_profile()

    path = save_profile(profile)

    print("\n統合完了")

    print(
        f"項目数: {len(profile.columns)}"
    )

    print(
        f"保存先: {path}"
    )

    print("\n【主要パフォーマンス】")

    for column in [
        "pitch_steps_per_min",
        "average_step_interval_sec",
        "average_stride_time_sec",
        "left_right_difference_sec",
    ]:

        if column in profile.columns:

            print(
                f"{column}: "
                f"{profile.iloc[0][column]}"
            )

    print("\n【主要フォーム】")

    for column in [
        "left_knee_avg",
        "right_knee_avg",
        "left_hip_avg",
        "right_hip_avg",
        "left_thigh_avg",
        "right_thigh_avg",
        "trunk_angle_avg",
        "pelvis_angle_avg",
    ]:

        if column in profile.columns:

            print(
                f"{column}: "
                f"{profile.iloc[0][column]}"
            )

    return profile


if __name__ == "__main__":
    run()