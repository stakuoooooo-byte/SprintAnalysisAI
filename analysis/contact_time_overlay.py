import cv2
import pandas as pd
from pathlib import Path


# ==============================
# 設定
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent

VIDEO_PATH = BASE_DIR / "videos" / "contact_events_analysis_browser.mp4"
EVENT_FILE = BASE_DIR / "data" / "contact_events.csv"

OUTPUT_PATH = BASE_DIR / "videos" / "contact_time_overlay.mp4"

FPS = 30.0


# ==============================
# データ読み込み
# ==============================

events = pd.read_csv(EVENT_FILE)

events["frame"] = events["frame"].astype(int)


# ==============================
# 動画
# ==============================

cap = cv2.VideoCapture(str(VIDEO_PATH))

if not cap.isOpened():
    raise RuntimeError(
        f"動画を開けません: {VIDEO_PATH}"
    )


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_fps = cap.get(cv2.CAP_PROP_FPS)

if video_fps <= 0:
    video_fps = FPS


fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(
    str(OUTPUT_PATH),
    fourcc,
    video_fps,
    (width, height)
)


# ==============================
# イベント辞書
# ==============================

event_dict = {}

for _, row in events.iterrows():

    frame = int(row["frame"])

    event_dict[frame] = {
        "event": int(row["event"]),
        "side": str(row["side"]),
        "time": float(row["time_sec"])
    }


# ==============================
# 動画処理
# ==============================

frame_number = 0


while True:

    ret, frame = cap.read()

    if not ret:
        break

    # --------------------------------
    # 現在時刻
    # --------------------------------

    current_time = frame_number / video_fps

    # --------------------------------
    # 基本情報
    # --------------------------------

    cv2.putText(
        frame,
        f"Frame: {frame_number}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Time: {current_time:.2f} s",
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    # --------------------------------
    # 接地イベント
    # --------------------------------

    if frame_number in event_dict:

        event = event_dict[frame_number]

        side = event["side"]

        label = (
            f"CONTACT "
            f"#{event['event']} "
            f"{side.upper()}"
        )

        # 画面中央付近に大きく表示
        cv2.putText(
            frame,
            label,
            (30, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 255, 0),
            3
        )

        cv2.putText(
            frame,
            f"{event['time']:.3f} sec",
            (30, 175),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2
        )

        # 画面全体を一瞬枠で囲む
        cv2.rectangle(
            frame,
            (5, 5),
            (width - 5, height - 5),
            (0, 255, 0),
            5
        )

    writer.write(frame)

    frame_number += 1


# ==============================
# 終了
# ==============================

cap.release()
writer.release()

print()
print("=====================================")
print("接地イベント確認動画")
print("=====================================")
print()
print(f"処理フレーム数: {frame_number}")
print(f"接地イベント数: {len(events)}")
print()
print(f"保存先:")
print(OUTPUT_PATH)
print()
print("=====================================")
print("処理完了")
print("=====================================")