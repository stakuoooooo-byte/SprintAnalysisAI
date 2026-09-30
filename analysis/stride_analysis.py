import pandas as pd
import os


INPUT_FILE = "data/contact_events.csv"
OUTPUT_FILE = "data/stride_analysis.csv"


# =====================================
# データ読み込み
# =====================================

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"{INPUT_FILE} が見つかりません"
    )

df = pd.read_csv(INPUT_FILE)


required_columns = [
    "event",
    "frame",
    "time_sec",
    "side",
    "ankle_x"
]

for column in required_columns:

    if column not in df.columns:
        raise ValueError(
            f"{column} がありません"
        )


# =====================================
# 数値化
# =====================================

df["frame"] = pd.to_numeric(
    df["frame"],
    errors="coerce"
)

df["time_sec"] = pd.to_numeric(
    df["time_sec"],
    errors="coerce"
)

df["ankle_x"] = pd.to_numeric(
    df["ankle_x"],
    errors="coerce"
)


df = df.dropna(
    subset=[
        "frame",
        "time_sec",
        "ankle_x"
    ]
)

df = df.sort_values(
    "time_sec"
).reset_index(drop=True)


# =====================================
# ステップごとの移動距離
# =====================================

df["step_horizontal_displacement"] = (
    df["ankle_x"].diff().abs()
)


df["step_time_sec"] = (
    df["time_sec"].diff()
)


# =====================================
# 同じ足のストライド
# =====================================

df["stride_horizontal_displacement"] = None
df["stride_time_sec"] = None


last_left_x = None
last_left_time = None

last_right_x = None
last_right_time = None


for i, row in df.iterrows():

    side = row["side"]

    x = row["ankle_x"]

    time = row["time_sec"]


    if side == "left":

        if last_left_x is not None:

            df.loc[
                i,
                "stride_horizontal_displacement"
            ] = abs(x - last_left_x)

            df.loc[
                i,
                "stride_time_sec"
            ] = time - last_left_time


        last_left_x = x
        last_left_time = time


    elif side == "right":

        if last_right_x is not None:

            df.loc[
                i,
                "stride_horizontal_displacement"
            ] = abs(x - last_right_x)

            df.loc[
                i,
                "stride_time_sec"
            ] = time - last_right_time


        last_right_x = x
        last_right_time = time


# =====================================
# 数値化
# =====================================

df["stride_horizontal_displacement"] = pd.to_numeric(
    df["stride_horizontal_displacement"],
    errors="coerce"
)

df["stride_time_sec"] = pd.to_numeric(
    df["stride_time_sec"],
    errors="coerce"
)


# =====================================
# 画像上の速度
# =====================================

df["image_stride_velocity"] = (
    df["stride_horizontal_displacement"]
    / df["stride_time_sec"]
)


# =====================================
# 保存
# =====================================

output_columns = [

    "event",
    "frame",
    "time_sec",
    "side",
    "ankle_x",

    "step_horizontal_displacement",
    "step_time_sec",

    "stride_horizontal_displacement",
    "stride_time_sec",

    "image_stride_velocity"
]


result = df[output_columns].copy()


result.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 結果表示
# =====================================

print()
print("=====================================")
print("ストライド分析")
print("=====================================")
print()

print(
    f"接地イベント数: {len(result)}"
)

print()

print(
    "平均ステップ画像移動量:",
    f"{result['step_horizontal_displacement'].mean():.4f}"
)

print(
    "平均ストライド画像移動量:",
    f"{result['stride_horizontal_displacement'].mean():.4f}"
)

print(
    "平均ストライド時間:",
    f"{result['stride_time_sec'].mean():.3f} 秒"
)

print()

left_stride = result[
    result["side"] == "left"
]

right_stride = result[
    result["side"] == "right"
]


print("左右比較")
print()

print(
    "左足ストライド画像移動量:",
    f"{left_stride['stride_horizontal_displacement'].mean():.4f}"
)

print(
    "右足ストライド画像移動量:",
    f"{right_stride['stride_horizontal_displacement'].mean():.4f}"
)

print()

print(
    "左足ストライド時間:",
    f"{left_stride['stride_time_sec'].mean():.3f} 秒"
)

print(
    "右足ストライド時間:",
    f"{right_stride['stride_time_sec'].mean():.3f} 秒"
)

print()

print("保存先:")
print(OUTPUT_FILE)

print()
print("=====================================")
print("処理完了")
print("=====================================")