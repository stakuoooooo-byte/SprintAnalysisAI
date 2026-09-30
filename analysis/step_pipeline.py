from pathlib import Path
import pandas as pd


def run_step_metrics(events_path=None):
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    if events_path is None:
        events_path = data_dir / "contact_events.csv"

    events_path = Path(events_path)

    output_path = data_dir / "step_metrics.csv"
    detail_output_path = data_dir / "step_metrics_detail.csv"

    df = pd.read_csv(events_path)

    required = ["event", "time_sec", "side"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"contact_events.csv に必要な列がありません: {missing}")

    df["time_sec"] = pd.to_numeric(df["time_sec"], errors="coerce")
    df = df.dropna(subset=["time_sec"])
    df = df.sort_values("time_sec").reset_index(drop=True)

    total_events = len(df)
    left_events = int((df["side"] == "left").sum())
    right_events = int((df["side"] == "right").sum())

    if total_events >= 2:
        intervals = df["time_sec"].diff().dropna()

        average_step_interval = float(intervals.mean())
        minimum_step_interval = float(intervals.min())
        maximum_step_interval = float(intervals.max())

        event_duration = float(
            df["time_sec"].iloc[-1] - df["time_sec"].iloc[0]
        )

        if event_duration > 0:
            pitch_steps_per_sec = float(
                (total_events - 1) / event_duration
            )
        else:
            pitch_steps_per_sec = 0.0
    else:
        average_step_interval = 0.0
        minimum_step_interval = 0.0
        maximum_step_interval = 0.0
        event_duration = 0.0
        pitch_steps_per_sec = 0.0

    pitch_steps_per_min = pitch_steps_per_sec * 60.0

    left_times = df.loc[df["side"] == "left", "time_sec"]
    right_times = df.loc[df["side"] == "right", "time_sec"]

    if len(left_times) >= 2:
        left_average_interval = float(left_times.diff().dropna().mean())
    else:
        left_average_interval = 0.0

    if len(right_times) >= 2:
        right_average_interval = float(right_times.diff().dropna().mean())
    else:
        right_average_interval = 0.0

    left_right_difference = abs(
        left_average_interval - right_average_interval
    )

    if right_average_interval > 0:
        left_right_ratio = (
            left_average_interval / right_average_interval
        )
    else:
        left_right_ratio = 0.0

    if event_duration > 0:
        event_frequency = (total_events - 1) / event_duration
    else:
        event_frequency = 0.0

    summary = pd.DataFrame([{
        "total_contact_events": total_events,
        "left_contact_events": left_events,
        "right_contact_events": right_events,
        "event_duration_sec": event_duration,
        "average_step_interval_sec": average_step_interval,
        "minimum_step_interval_sec": minimum_step_interval,
        "maximum_step_interval_sec": maximum_step_interval,
        "pitch_steps_per_sec": pitch_steps_per_sec,
        "pitch_steps_per_min": pitch_steps_per_min,
        "left_average_contact_interval_sec": left_average_interval,
        "right_average_contact_interval_sec": right_average_interval,
        "left_right_difference_sec": left_right_difference,
        "left_right_ratio": left_right_ratio,
        "event_frequency_steps_per_sec": event_frequency,
    }])

    summary.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    detail = df.copy()

    if "interval_sec" not in detail.columns:
        detail["interval_sec"] = detail["time_sec"].diff()

    detail.to_csv(
        detail_output_path,
        index=False,
        encoding="utf-8-sig"
    )

    return {
        "summary": summary,
        "detail": detail,
        "output_path": str(output_path),
        "detail_output_path": str(detail_output_path),
    }


if __name__ == "__main__":
    result = run_step_metrics()

    print("=== Step Metrics ===")
    print(result["summary"].to_string(index=False))
    print(f"\nOutput: {result['output_path']}")
