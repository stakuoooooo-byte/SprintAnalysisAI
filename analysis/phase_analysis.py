from pathlib import Path
import pandas as pd
import numpy as np


def run_phase_analysis(events_path=None):

    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    if events_path is None:
        events_path = data_dir / "contact_events.csv"

    events_path = Path(events_path)

    if not events_path.exists():
        raise FileNotFoundError(
            f"{events_path} が見つかりません。"
        )

    df = pd.read_csv(events_path)

    required = [
        "event",
        "frame",
        "time_sec",
        "side",
        "interval_sec"
    ]

    missing = [
        c for c in required
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"contact_events.csv に必要な列がありません: {missing}"
        )

    # ----------------------------------------
    # 数値化
    # ----------------------------------------

    for column in [
        "event",
        "frame",
        "time_sec",
        "interval_sec"
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "frame",
            "time_sec"
        ]
    )

    df = df.sort_values(
        "time_sec"
    ).reset_index(drop=True)

    if len(df) < 2:
        raise ValueError(
            "接地イベントが2件未満です。"
        )

    # ----------------------------------------
    # ステップ間隔
    # ----------------------------------------

    df["step_interval_sec"] = (
        df["time_sec"].diff()
    )

    # ----------------------------------------
    # 累積時間
    # ----------------------------------------

    start_time = float(
        df["time_sec"].iloc[0]
    )

    df["elapsed_time_sec"] = (
        df["time_sec"] - start_time
    )

    # ----------------------------------------
    # 区間番号
    #
    # 現段階では「局面」と断定しない。
    # 映像を5区間に分割する。
    # ----------------------------------------

    n = len(df)

    df["segment"] = pd.qcut(
        np.arange(n),
        q=min(5, n),
        labels=False,
        duplicates="drop"
    )

    df["segment"] = (
        df["segment"].astype(int) + 1
    )

    # ----------------------------------------
    # 区間ごとの統計
    # ----------------------------------------

    rows = []

    for segment_id, group in df.groupby(
        "segment"
    ):

        intervals = group[
            "step_interval_sec"
        ].dropna()

        if len(intervals) > 0:

            avg_interval = float(
                intervals.mean()
            )

            pitch = (
                1.0 / avg_interval
                if avg_interval > 0
                else np.nan
            )

        else:

            avg_interval = np.nan
            pitch = np.nan

        rows.append({

            "segment": int(
                segment_id
            ),

            "start_time_sec": float(
                group["time_sec"].min()
            ),

            "end_time_sec": float(
                group["time_sec"].max()
            ),

            "event_count": int(
                len(group)
            ),

            "average_step_interval_sec":
                avg_interval,

            "pitch_steps_per_sec":
                pitch,

            "pitch_steps_per_min":
                (
                    pitch * 60.0
                    if pd.notna(pitch)
                    else np.nan
                ),

            "left_events": int(
                (
                    group["side"] == "left"
                ).sum()
            ),

            "right_events": int(
                (
                    group["side"] == "right"
                ).sum()
            ),

        })

    summary = pd.DataFrame(
        rows
    )

    # ----------------------------------------
    # 出力
    # ----------------------------------------

    detail_path = (
        data_dir /
        "phase_analysis_detail.csv"
    )

    summary_path = (
        data_dir /
        "phase_analysis.csv"
    )

    df.to_csv(
        detail_path,
        index=False,
        encoding="utf-8-sig"
    )

    summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig"
    )

    return {
        "detail": df,
        "summary": summary,
        "detail_path": str(
            detail_path
        ),
        "summary_path": str(
            summary_path
        ),
    }


def print_report(result):

    print()
    print(
        "========================================"
    )
    print(
        "SprintAnalysisAI"
    )
    print(
        "時間区間別ステップ分析"
    )
    print(
        "========================================"
    )

    print()

    print(
        result["summary"].to_string(
            index=False
        )
    )

    print()

    print(
        f"詳細データ: "
        f"{result['detail_path']}"
    )

    print(
        f"区間データ: "
        f"{result['summary_path']}"
    )

    print()

    print(
        "注意:"
    )

    print(
        "segment 1〜5 は時間区間による分割であり、"
    )

    print(
        "加速局面・最大速度局面を意味しません。"
    )


if __name__ == "__main__":

    result = run_phase_analysis()

    print_report(
        result
    )