import pandas as pd
import os


INPUT_CSV = "data/contact_sequence.csv"
OUTPUT_CSV = "data/step_metrics.csv"


# =====================================
# データ読み込み
# =====================================

df = pd.read_csv(INPUT_CSV)


if df.empty:
    print("接地ステップデータがありません。")
    raise SystemExit


# =====================================
# interval_sec の数値化
# =====================================

df["interval_sec"] = pd.to_numeric(
    df["interval_sec"],
    errors="coerce"
)


# 最初のステップは間隔がないので除外
intervals = df["interval_sec"].dropna()


if intervals.empty:
    print("接地間隔を計算できません。")
    raise SystemExit


# =====================================
# 平均接地間隔
# =====================================

average_interval = intervals.mean()


# =====================================
# ピッチ
# 1秒あたりのステップ数
# =====================================

pitch = 1 / average_interval


# =====================================
# 左右別の接地間隔
# =====================================

left_df = df[
    df["side"] == "left"
]

right_df = df[
    df["side"] == "right"
]


left_intervals = (
    left_df["interval_sec"]
    .dropna()
)


right_intervals = (
    right_df["interval_sec"]
    .dropna()
)


if not left_intervals.empty:

    left_average = (
        left_intervals.mean()
    )

else:

    left_average = 0


if not right_intervals.empty:

    right_average = (
        right_intervals.mean()
    )

else:

    right_average = 0


# =====================================
# 左右差
# =====================================

if left_average > 0 and right_average > 0:

    asymmetry = abs(
        left_average - right_average
    )

else:

    asymmetry = 0


# =====================================
# 結果保存
# =====================================

result = pd.DataFrame([{

    "average_interval_sec":
        average_interval,

    "pitch_steps_per_sec":
        pitch,

    "left_interval_sec":
        left_average,

    "right_interval_sec":
        right_average,

    "left_right_difference_sec":
        asymmetry

}])


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
# 結果表示
# =====================================

print()
print("===== ステップ解析結果 =====")
print()

print(
    f"平均接地間隔: "
    f"{average_interval:.3f} 秒"
)

print(
    f"ピッチ: "
    f"{pitch:.2f} steps/sec"
)

print(
    f"左側平均間隔: "
    f"{left_average:.3f} 秒"
)

print(
    f"右側平均間隔: "
    f"{right_average:.3f} 秒"
)

print(
    f"左右差: "
    f"{asymmetry:.3f} 秒"
)

print()

print(
    f"保存先: {OUTPUT_CSV}"
)