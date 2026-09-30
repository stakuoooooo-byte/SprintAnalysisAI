import pandas as pd
import numpy as np
from pathlib import Path


# ==============================
# 設定
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

EVENT_FILE = BASE_DIR / "data" / "contact_events.csv"
ANGLE_FILE = BASE_DIR / "data" / "angle_history.csv"
OUTPUT_FILE = BASE_DIR / "data" / "contact_time_analysis.csv"

FPS = 30.0

# 接地イベントの前後を見るフレーム数
WINDOW_BEFORE = 4
WINDOW_AFTER = 6


# ==============================
# データ読み込み
# ==============================

events = pd.read_csv(EVENT_FILE)
angles = pd.read_csv(ANGLE_FILE)

# フレーム番号を整数化
events["frame"] = events["frame"].astype(int)
angles["frame"] = angles["frame"].astype(int)


# ==============================
# 足首Y座標の列
# ==============================

def get_ankle_y_column(side):
    if side == "left":
        return "left_ankle_y"
    else:
        return "right_ankle_y"


# ==============================
# 接地時間推定
# ==============================

results = []

for _, event in events.iterrows():

    frame = int(event["frame"])
    side = event["side"]

    ankle_y_col = get_ankle_y_column(side)

    # 対象イベント前後のデータ
    window = angles[
        (angles["frame"] >= frame - WINDOW_BEFORE)
        & (angles["frame"] <= frame + WINDOW_AFTER)
    ].copy()

    if len(window) < 3:
        continue

    window = window.sort_values("frame")

    # 足首Y座標
    y_values = window[ankle_y_col].values
    frame_values = window["frame"].values

    # ==============================
    # 接地付近の最低位置を探す
    # ==============================

    min_index = int(np.argmax(y_values))

    contact_frame = int(frame_values[min_index])

    # ==============================
    # 接地前の下降
    # 接地後の上昇
    # ==============================

    contact_start_frame = contact_frame
    contact_end_frame = contact_frame

    # 接地前方向へ探索
    for i in range(min_index - 1, -1, -1):

        if y_values[i] < y_values[i + 1]:
            contact_start_frame = int(frame_values[i])
        else:
            break

    # 接地後方向へ探索
    for i in range(min_index + 1, len(y_values)):

        if y_values[i] < y_values[i - 1]:
            contact_end_frame = int(frame_values[i])
        else:
            break

    # ==============================
    # 接地時間
    # ==============================

    contact_duration_frames = (
        contact_end_frame - contact_start_frame
    )

    contact_duration_sec = (
        contact_duration_frames / FPS
    )

    results.append({
        "event": int(event["event"]),
        "frame": frame,
        "time_sec": event["time_sec"],
        "side": side,
        "contact_start_frame": contact_start_frame,
        "contact_frame": contact_frame,
        "contact_end_frame": contact_end_frame,
        "contact_duration_frames": contact_duration_frames,
        "contact_duration_sec": contact_duration_sec
    })


# ==============================
# DataFrame
# ==============================

result_df = pd.DataFrame(results)


# ==============================
# 保存
# ==============================

result_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ==============================
# 結果表示
# ==============================

print()
print("=====================================")
print("接地時間分析")
print("=====================================")
print()

print(f"分析イベント数: {len(result_df)}")

if len(result_df) > 0:

    print(
        f"平均接地時間: "
        f"{result_df['contact_duration_sec'].mean():.3f} 秒"
    )

    print(
        f"最短接地時間: "
        f"{result_df['contact_duration_sec'].min():.3f} 秒"
    )

    print(
        f"最長接地時間: "
        f"{result_df['contact_duration_sec'].max():.3f} 秒"
    )

    print()

    left = result_df[
        result_df["side"] == "left"
    ]

    right = result_df[
        result_df["side"] == "right"
    ]

    if len(left) > 0:
        print(
            f"左足平均接地時間: "
            f"{left['contact_duration_sec'].mean():.3f} 秒"
        )

    if len(right) > 0:
        print(
            f"右足平均接地時間: "
            f"{right['contact_duration_sec'].mean():.3f} 秒"
        )

print()
print(f"保存先: {OUTPUT_FILE}")
print()
print("=====================================")
print("処理完了")
print("=====================================")