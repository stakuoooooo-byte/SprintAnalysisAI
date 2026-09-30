from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def run_step_metrics(
    events_path=None
):
    """
    contact_events.csv から
    ピッチ・ステップ間隔・左右差を計算する。
    """

    if events_path is None:
        events_path = (
            DATA_DIR / "contact_events.csv"
        )

    events_path = Path(events_path)

    if not events_path.exists():
        raise FileNotFoundError(
            f"接地イベントファイルがありません: "
            f"{events_path}"
        )

    df = pd.read_csv(
        events_path
    )

    if df.empty:
        raise ValueError(
            "接地イベントデータが空です。"
        )

    required_columns = [
        "event",
        "frame",
        "time_sec",
        "side"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "contact_events.csv に必要な列がありません: "
            + str(missing)
        )

    # ==========================================
    # データ整理
    # ==========================================

    df["event"] = pd.to_numeric(
        df["event"],
        errors="coerce"
    )

    df["frame"] = pd.to_numeric(
        df["frame"],
        errors="coerce"
    )

    df["time_sec"] = pd.to_numeric(
        df["time_sec"],
        errors="coerce"
    )

    df["side"] = (
        df["side"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df = df.dropna(
        subset=[
            "event",
            "frame",
            "time_sec"
        ]
    ).copy()

    df = (
        df
        .sort_values("time_sec")
        .reset_index(drop=True)
    )

    # ==========================================
    # 基本値
    # ==========================================

    total_events = len(df)

    left_events = int(
        (
            df["side"] == "left"
        ).sum()
    )

    right_events = int(
        (
            df["side"] == "right"
        ).sum()
    )

    # ==========================================
    # ステップ間隔
    # ==========================================

    intervals = (
        df["time_sec"]
        .diff()
        .dropna()
    )

    if len(intervals) > 0:

        average_step_interval = (
            intervals.mean()
        )

        minimum_step_interval = (
            intervals.min()
        )

        maximum_step_interval = (
            intervals.max()
        )

    else:

        average_step_interval = None
        minimum_step_interval = None
        maximum_step_interval = None

    # ==========================================
    # ピッチ
    # ==========================================

    if (
        average_step_interval is not None
        and
        average_step_interval > 0
    ):

        pitch_steps_per_sec = (
            1.0 /
            average_step_interval
        )

        pitch_steps_per_min = (
            pitch_steps_per_sec *
            60.0
        )

    else:

        pitch_steps_per_sec = None
        pitch_steps_per_min = None

    # ==========================================
    # イベント全体の時間
    # ==========================================

    if total_events >= 2:

        event_duration_sec = (
            df["time_sec"].iloc[-1]
            -
            df["time_sec"].iloc[0]
        )

    else:

        event_duration_sec = None

    # ==========================================
    # 左脚の同側接地間隔
    # ==========================================

    left_times = (
        df.loc[
            df["side"] == "left",
            "time_sec"
        ]
        .sort_values()
    )

    left_intervals = (
        left_times.diff()
        .dropna()
    )

    if len(left_intervals) > 0:

        left_average_interval = (
            left_intervals.mean()
        )

    else:

        left_average_interval = None

    # ==========================================
    # 右脚の同側接地間隔
    # ==========================================

    right_times = (
        df.loc[
            df["side"] == "right",
            "time_sec"
        ]
        .sort_values()
    )

    right_intervals = (
        right_times.diff()
        .dropna()
    )

    if len(right_intervals) > 0:

        right_average_interval = (
            right_intervals.mean()
        )

    else:

        right_average_interval = None

    # ==========================================
    # 左右差
    # ==========================================

    if (
        left_average_interval is not None
        and
        right_average_interval is not None
    ):

        left_right_difference = abs(
            left_average_interval
            -
            right_average_interval
        )

        if right_average_interval != 0:

            left_right_ratio = (
                left_average_interval
                /
                right_average_interval
            )

        else:

            left_right_ratio = None

    else:

        left_right_difference = None
        left_right_ratio = None

    # ==========================================
    # イベント頻度
    # ==========================================

    if (
        event_duration_sec is not None
        and
        event_duration_sec > 0
    ):

        event_frequency = (
            (total_events - 1)
            /
            event_duration_sec
        )

    else:

        event_frequency = None

    # ==========================================
    # 結果
    # ==========================================

    summary = pd.DataFrame(
        [
            {
                "total_contact_events":
                    total_events,

                "left_contact_events":
                    left_events,

                "right_contact_events":
                    right_events,

                "event_duration_sec":
                    event_duration_sec,

                "average_step_interval_sec":
                    average_step_interval,

                "minimum_step_interval_sec":
                    minimum_step_interval,

                "maximum_step_interval_sec":
                    maximum_step_interval,

                "pitch_steps_per_sec":
                    pitch_steps_per_sec,

                "pitch_steps_per_min":
                    pitch_steps_per_min,

                "left_average_contact_interval_sec":
                    left_average_interval,

                "right_average_contact_interval_sec":
                    right_average_interval,

                "left_right_difference_sec":
                    left_right_difference,

                "left_right_ratio":
                    left_right_ratio,

                "event_frequency_steps_per_sec":
                    event_frequency
            }
        ]
    )

    # ==========================================
    # 詳細データ
    # ==========================================

    detail = df.copy()

    detail[
        "interval_sec"
    ] = detail[
        "time_sec"
    ].diff()

    # ==========================================
    # 保存
    # ==========================================

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    summary_path = (
        DATA_DIR /
        "step_metrics.csv"
    )

    detail_path = (
        DATA_DIR /
        "step_metrics_detail.csv"
    )

    summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig"
    )

    detail.to_csv(
        detail_path,
        index=False,
        encoding="utf-8-sig"
    )

    return {
        "summary": summary,
        "detail": detail,
        "summary_path": summary_path,
        "detail_path": detail_path
    }


if __name__ == "__main__":

    result = run_step_metrics()

    print(
        "ステップ分析完了"
    )

    print(
        result["summary"].to_string(
            index=False
        )
    )