import pandas as pd
import os


# =====================================
# ファイル設定
# =====================================

CONTACT_FILE = "data/contact_events.csv"
ANGLE_FILE = "data/angle_history.csv"
OUTPUT_FILE = "data/contact_angle_analysis.csv"


# =====================================
# データ読み込み
# =====================================

if not os.path.exists(CONTACT_FILE):
    raise FileNotFoundError(
        f"{CONTACT_FILE} が見つかりません"
    )

if not os.path.exists(ANGLE_FILE):
    raise FileNotFoundError(
        f"{ANGLE_FILE} が見つかりません"
    )


contact_df = pd.read_csv(
    CONTACT_FILE
)

angle_df = pd.read_csv(
    ANGLE_FILE
)


# =====================================
# 必要な列を確認
# =====================================

required_contact = [
    "event",
    "frame",
    "time_sec",
    "side"
]

required_angle = [
    "frame",
    "left_knee",
    "right_knee",
    "left_hip",
    "right_hip",
    "left_ankle",
    "right_ankle"
]


for column in required_contact:

    if column not in contact_df.columns:
        raise ValueError(
            f"contact_events.csv に {column} がありません"
        )


for column in required_angle:

    if column not in angle_df.columns:
        raise ValueError(
            f"angle_history.csv に {column} がありません"
        )


# =====================================
# 数値化
# =====================================

contact_df["frame"] = pd.to_numeric(
    contact_df["frame"],
    errors="coerce"
)

angle_df["frame"] = pd.to_numeric(
    angle_df["frame"],
    errors="coerce"
)


contact_df = contact_df.dropna(
    subset=["frame"]
)

angle_df = angle_df.dropna(
    subset=["frame"]
)


contact_df["frame"] = contact_df["frame"].astype(int)
angle_df["frame"] = angle_df["frame"].astype(int)


# =====================================
# 接地イベントと角度を結合
# =====================================

result = pd.merge(
    contact_df,
    angle_df,
    on="frame",
    how="left"
)


# =====================================
# 接地した足に対応する角度を抽出
# =====================================

def get_contact_angle(row, side, column):

    if side == "left":

        return row[f"left_{column}"]

    elif side == "right":

        return row[f"right_{column}"]

    return None


result["contact_knee_angle"] = result.apply(
    lambda row: get_contact_angle(
        row,
        row["side"],
        "knee"
    ),
    axis=1
)

result["contact_hip_angle"] = result.apply(
    lambda row: get_contact_angle(
        row,
        row["side"],
        "hip"
    ),
    axis=1
)

result["contact_ankle_angle"] = result.apply(
    lambda row: get_contact_angle(
        row,
        row["side"],
        "ankle"
    ),
    axis=1
)


# =====================================
# 左右差
# =====================================

result["knee_left_right_difference"] = (
    result["left_knee"]
    - result["right_knee"]
).abs()


result["hip_left_right_difference"] = (
    result["left_hip"]
    - result["right_hip"]
).abs()


result["ankle_left_right_difference"] = (
    result["left_ankle"]
    - result["right_ankle"]
).abs()


# =====================================
# 保存する列
# =====================================

output_columns = [

    "event",
    "frame",
    "time_sec",
    "side",

    "contact_knee_angle",
    "contact_hip_angle",
    "contact_ankle_angle",

    "left_knee",
    "right_knee",

    "left_hip",
    "right_hip",

    "left_ankle",
    "right_ankle",

    "knee_left_right_difference",
    "hip_left_right_difference",
    "ankle_left_right_difference"
]


result = result[output_columns]


# =====================================
# 保存
# =====================================

os.makedirs(
    "data",
    exist_ok=True
)

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
print("接地時角度分析")
print("=====================================")

print()

print(
    f"接地イベント数: {len(result)}"
)

print()

print(
    "接地時膝角度 平均:",
    f"{result['contact_knee_angle'].mean():.2f}°"
)

print(
    "接地時股関節角度 平均:",
    f"{result['contact_hip_angle'].mean():.2f}°"
)

print(
    "接地時足関節角度 平均:",
    f"{result['contact_ankle_angle'].mean():.2f}°"
)

print()

print("左右別")

print()

for side in ["left", "right"]:

    side_df = result[
        result["side"] == side
    ]

    if len(side_df) == 0:
        continue

    print(
        f"{side} 膝角度:",
        f"{side_df['contact_knee_angle'].mean():.2f}°"
    )

    print(
        f"{side} 股関節角度:",
        f"{side_df['contact_hip_angle'].mean():.2f}°"
    )

    print(
        f"{side} 足関節角度:",
        f"{side_df['contact_ankle_angle'].mean():.2f}°"
    )

    print()


print("保存先:")
print(OUTPUT_FILE)

print()
print("=====================================")
print("処理完了")
print("=====================================")