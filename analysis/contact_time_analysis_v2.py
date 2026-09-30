import pandas as pd
import numpy as np
from pathlib import Path


# ==============================
# 設定
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

EVENT_FILE = BASE_DIR / "data" / "contact_events.csv"
ANGLE_FILE = BASE_DIR / "data" / "angle_history.csv"
OUTPUT_FILE = BASE_DIR / "data" / "contact_time_analysis_v2.csv"

FPS = 30.0

# 接地イベント前後の探索範囲
SEARCH_BEFORE = 8
SEARCH_AFTER = 8


# ==============================
# データ読み込み
# ==============================

events = pd.read_csv(EVENT_FILE)
angles = pd.read_csv(ANGLE_FILE)

events["frame"] = events["frame"].astype(int)
angles["frame"] = angles["frame"].astype(int)


# ==============================
# 左右の足首Y列
# ==============================

def ankle_column(side):
    if side == "left":
        return "left_ankle_y"
    return "right_ankle_y"


# ==============================
# 結果
# ==============================

results = []


for _, event in events.iterrows():

    event_frame = int(event["frame"])
    side = event["side"]

    col = ankle_column(side)

    # --------------------------------
    # イベント周辺のデータ
    # --------------------------------

    window = angles[
        (angles["frame"] >= event_frame - SEARCH_BEFORE)
        & (angles["frame"] <= event_frame + SEARCH_AFTER)
    ].copy()

    if len(window) < 5:
        continue

    window = window.sort_values("frame").reset_index(drop=True)

    frames = window["frame"].to_numpy()
    y = window[col].to_numpy()

    # --------------------------------
    # Y座標を平滑化
    # --------------------------------

    y_smooth = (
        pd.Series(y)
        .rolling(
            window=3,
            center=True,
            min_periods=1
        )
        .mean()
        .to_numpy()
    )

    # --------------------------------
    # 足首Y速度
    #
    # 画像座標では
    # Yが増える → 下方向
    # Yが減る → 上方向
    # --------------------------------

    velocity = np.gradient(y_smooth) * FPS

    # --------------------------------
    # 接地候補
    #
    # 接地付近では
    # 下方向速度 → 0 → 上方向速度
    #
    # となるピーク付近を探す
    # --------------------------------

    local_max_index = int(np.argmax(y_smooth))

    contact_frame = int(frames[local_max_index])

    # --------------------------------
    # 接地前の下降開始
    # --------------------------------

    start_index = local_max_index

    for i in range(local_max_index - 1, -1, -1):

        if velocity[i] > 0:
            start_index = i
        else:
            break

    # --------------------------------
    # 接地後の上昇開始
    # --------------------------------

    end_index = local_max_index

    for i in range(local_max_index + 1, len(frames)):

        if velocity[i] < 0:
            end_index = i
        else:
            break

    start_frame = int(frames[start_index])
    end_frame = int(frames[end_index])

    duration_frames = end_frame - start_frame

    duration_sec = duration_frames / FPS

    results.append({
        "event": int(event["event"]),
        "event_frame": event_frame,
        "contact_frame": contact_frame,
        "side": side,
        "start_frame": start_frame,
        "end_frame": end_frame,
        "duration_frames": duration_frames,
        "contact_time_sec": duration_sec
    })


# ==============================
# 保存
# ==============================

result_df = pd.DataFrame(results)

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
print("接地時間分析 V2")
print("=====================================")
print()

print(f"分析イベント数: {len(result_df)}")

if len(result_df) > 0:

    print(
        f"平均接地時間: "
        f"{result_df['contact_time_sec'].mean():.3f} 秒"
    )

    print(
        f"最短接地時間: "
        f"{result_df['contact_time_sec'].min():.3f} 秒"
    )

    print(
        f"最長接地時間: "
        f"{result_df['contact_time_sec'].max():.3f} 秒"
    )

    print()

    left = result_df[result_df["side"] == "left"]
    right = result_df[result_df["side"] == "right"]

    if len(left) > 0:
        print(
            f"左足平均接地時間: "
            f"{left['contact_time_sec'].mean():.3f} 秒"
        )

    if len(right) > 0:
        print(
            f"右足平均接地時間: "
            f"{right['contact_time_sec'].mean():.3f} 秒"
        )

print()
print(f"保存先: {OUTPUT_FILE}")
print()
print("=====================================")
print("処理完了")
print("=====================================")