from pathlib import Path
import pandas as pd

MIN_SAME_SIDE_INTERVAL_SEC = 0.20
MIN_GLOBAL_INTERVAL_SEC = 0.12
MAX_STEP_INTERVAL_SEC = 0.60


def run_contact_events(candidates_path=None):
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    if candidates_path is None:
        candidates_path = data_dir / "contact_candidates.csv"

    candidates_path = Path(candidates_path)
    output_path = data_dir / "contact_events.csv"

    df = pd.read_csv(candidates_path)

    required = ["candidate", "frame", "time_sec", "side"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"contact_candidates.csv に必要な列がありません: {missing}")

    df["time_sec"] = pd.to_numeric(df["time_sec"], errors="coerce")
    df["frame"] = pd.to_numeric(df["frame"], errors="coerce")
    df["side"] = df["side"].astype(str).str.lower().str.strip()

    df = df.dropna(subset=["time_sec", "frame"])
    df = df.sort_values("time_sec").reset_index(drop=True)

    selected = []

    last_global_time = None
    last_side_time = {
        "left": None,
        "right": None,
    }

    for _, row in df.iterrows():
        side = row["side"]
        time_sec = float(row["time_sec"])

        if side not in ("left", "right"):
            continue

        if last_global_time is not None:
            global_interval = time_sec - last_global_time

            if global_interval < MIN_GLOBAL_INTERVAL_SEC:
                continue

        if last_side_time[side] is not None:
            same_side_interval = time_sec - last_side_time[side]

            if same_side_interval < MIN_SAME_SIDE_INTERVAL_SEC:
                continue
        else:
            same_side_interval = None

        selected.append(row)

        last_global_time = time_sec
        last_side_time[side] = time_sec

    events = pd.DataFrame(selected).reset_index(drop=True)

    if events.empty:
        raise ValueError("接地イベントを検出できませんでした。")

    events.insert(0, "event", range(1, len(events) + 1))

    events["interval_sec"] = events["time_sec"].diff()

    same_side_intervals = []
    last_times = {
        "left": None,
        "right": None,
    }

    for _, row in events.iterrows():
        side = row["side"]
        current_time = float(row["time_sec"])

        if last_times[side] is None:
            same_side_intervals.append(None)
        else:
            same_side_intervals.append(
                current_time - last_times[side]
            )

        last_times[side] = current_time

    events["same_side_interval_sec"] = same_side_intervals

    events["alternating"] = (
        events["side"] != events["side"].shift(1)
    )

    events["step_interval_valid"] = (
        events["interval_sec"].isna()
        | (
            (events["interval_sec"] >= MIN_GLOBAL_INTERVAL_SEC)
            & (events["interval_sec"] <= MAX_STEP_INTERVAL_SEC)
        )
    )

    events.to_csv(output_path, index=False, encoding="utf-8-sig")

    return {
        "data": events,
        "total_events": len(events),
        "left_events": int((events["side"] == "left").sum()),
        "right_events": int((events["side"] == "right").sum()),
        "output_path": str(output_path),
    }


if __name__ == "__main__":
    result = run_contact_events()

    print("=== Contact Events ===")
    print(f"Total: {result['total_events']}")
    print(f"Left : {result['left_events']}")
    print(f"Right: {result['right_events']}")
    print(f"Output: {result['output_path']}")
