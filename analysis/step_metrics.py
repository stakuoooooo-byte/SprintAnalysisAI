import pandas as pd
import os


# =====================================
# ファイル設定
# =====================================

INPUT_CSV = "data/contact_events.csv"
OUTPUT_CSV = "data/step_metrics.csv"


# =====================================
# CSV読み込み
# =====================================

if not os.path.exists(INPUT_CSV):

    print("入力ファイルがありません:")
    print(INPUT_CSV)

    raise SystemExit


df = pd.read_csv(
    INPUT_CSV
)


if df.empty:

    print("接地イベントデータがありません。")

    raise SystemExit


# =====================================
# 必要な列
# =====================================

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

    print("必要な列がありません:")
    print(missing)

    print()
    print("現在の列:")
    print(list(df.columns))

    raise SystemExit


# =====================================
# 数値化
# =====================================

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


# =====================================
# side整理
# =====================================

df["side"] = (
    df["side"]
    .astype(str)
    .str.lower()
    .str.strip()
)


# =====================================
# 欠損削除
# =====================================

df = df.dropna(
    subset=[
        "event",
        "frame",
        "time_sec",
        "side"
    ]
).copy()


# =====================================
# 時系列順
# =====================================

df = (
    df
    .sort_values("time_sec")
    .reset_index(drop=True)
)


# =====================================
# イベント間隔
# =====================================

df["interval_sec"] = (
    df["time_sec"].diff()
)


# =====================================
# 基本データ
# =====================================

total_events = len(df)

left_events = len(
    df[df["side"] == "left"]
)

right_events = len(
    df[df["side"] == "right"]
)


# =====================================
# 有効なステップ間隔
# =====================================

intervals = (
    df["interval_sec"]
    .dropna()
)


if intervals.empty:

    print("ステップ間隔を計算できません。")

    raise SystemExit


# =====================================
# 平均ステップ間隔
# =====================================

average_interval = (
    intervals.mean()
)


# =====================================
# 最短・最長
# =====================================

minimum_interval = (
    intervals.min()
)

maximum_interval = (
    intervals.max()
)


# =====================================
# ピッチ
#
# 1秒あたりの接地回数
# =====================================

pitch_steps_per_sec = (
    1.0 / average_interval
)


pitch_steps_per_min = (
    pitch_steps_per_sec
    * 60.0
)


# =====================================
# 左右それぞれの接地時刻
# =====================================

left_df = (
    df[
        df["side"] == "left"
    ]
    .copy()
)


right_df = (
    df[
        df["side"] == "right"
    ]
    .copy()
)


# =====================================
# 左足→左足の接地間隔
# =====================================

left_intervals = (
    left_df["time_sec"]
    .diff()
    .dropna()
)


# =====================================
# 右足→右足の接地間隔
# =====================================

right_intervals = (
    right_df["time_sec"]
    .diff()
    .dropna()
)


# =====================================
# 左右平均
# =====================================

if not left_intervals.empty:

    left_average_interval = (
        left_intervals.mean()
    )

else:

    left_average_interval = 0.0


if not right_intervals.empty:

    right_average_interval = (
        right_intervals.mean()
    )

else:

    right_average_interval = 0.0


# =====================================
# 左右差
# =====================================

if (
    left_average_interval > 0
    and
    right_average_interval > 0
):

    left_right_difference = abs(
        left_average_interval
        -
        right_average_interval
    )

else:

    left_right_difference = 0.0


# =====================================
# 左右比
# =====================================

if (
    left_average_interval > 0
    and
    right_average_interval > 0
):

    left_right_ratio = (
        left_average_interval
        /
        right_average_interval
    )

else:

    left_right_ratio = 0.0


# =====================================
# 走行時間
# =====================================

start_time = (
    df["time_sec"].min()
)

end_time = (
    df["time_sec"].max()
)

event_duration = (
    end_time
    -
    start_time
)


# =====================================
# 実質的なイベント頻度
# =====================================

if event_duration > 0:

    event_frequency = (
        (total_events - 1)
        /
        event_duration
    )

else:

    event_frequency = 0.0


# =====================================
# 結果DataFrame
# =====================================

result = pd.DataFrame([{

    "total_contact_events":
        total_events,

    "left_contact_events":
        left_events,

    "right_contact_events":
        right_events,

    "event_duration_sec":
        event_duration,

    "average_step_interval_sec":
        average_interval,

    "minimum_step_interval_sec":
        minimum_interval,

    "maximum_step_interval_sec":
        maximum_interval,

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

}])


# =====================================
# 保存
# =====================================

os.makedirs(
    "data",
    exist_ok=True
)


result.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 1イベントごとの詳細CSVも保存
# =====================================

DETAIL_CSV = (
    "data/step_metrics_detail.csv"
)


df.to_csv(
    DETAIL_CSV,
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 結果表示
# =====================================

print()
print("=====================================")
print("ステップ分析")
print("=====================================")
print()

print(
    f"総接地イベント数: "
    f"{total_events}"
)

print(
    f"左足接地数: "
    f"{left_events}"
)

print(
    f"右足接地数: "
    f"{right_events}"
)

print()

print(
    f"平均ステップ間隔: "
    f"{average_interval:.3f} 秒"
)

print(
    f"最短ステップ間隔: "
    f"{minimum_interval:.3f} 秒"
)

print(
    f"最長ステップ間隔: "
    f"{maximum_interval:.3f} 秒"
)

print()

print(
    f"ピッチ: "
    f"{pitch_steps_per_sec:.2f} steps/sec"
)

print(
    f"ピッチ: "
    f"{pitch_steps_per_min:.1f} steps/min"
)

print()

print(
    f"左足→左足平均: "
    f"{left_average_interval:.3f} 秒"
)

print(
    f"右足→右足平均: "
    f"{right_average_interval:.3f} 秒"
)

print(
    f"左右差: "
    f"{left_right_difference:.3f} 秒"
)

print(
    f"左右比: "
    f"{left_right_ratio:.3f}"
)

print()

print(
    f"イベント区間: "
    f"{event_duration:.3f} 秒"
)

print()

print(
    f"保存先: "
    f"{OUTPUT_CSV}"
)

print(
    f"詳細: "
    f"{DETAIL_CSV}"
)

print()

print("=====================================")
print("処理完了")
print("=====================================")