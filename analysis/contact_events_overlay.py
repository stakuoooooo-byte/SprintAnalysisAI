import cv2
import pandas as pd
import os


# =====================================
# ファイル設定
# =====================================

INPUT_VIDEO = "videos/test_browser.mp4"

CANDIDATE_CSV = "data/contact_candidates.csv"

EVENT_CSV = "data/contact_events.csv"

OUTPUT_VIDEO = "videos/contact_events_analysis.mp4"


# =====================================
# CSV読み込み
# =====================================

if not os.path.exists(INPUT_VIDEO):
    print("入力動画がありません:")
    print(INPUT_VIDEO)
    raise SystemExit


if not os.path.exists(CANDIDATE_CSV):
    print("接地候補CSVがありません:")
    print(CANDIDATE_CSV)
    raise SystemExit


if not os.path.exists(EVENT_CSV):
    print("接地イベントCSVがありません:")
    print(EVENT_CSV)
    raise SystemExit


candidates = pd.read_csv(
    CANDIDATE_CSV
)

events = pd.read_csv(
    EVENT_CSV
)


# =====================================
# 必要な列を数値化
# =====================================

for df in [candidates, events]:

    df["frame"] = pd.to_numeric(
        df["frame"],
        errors="coerce"
    )

    df["ankle_x"] = pd.to_numeric(
        df["ankle_x"],
        errors="coerce"
    )

    df["ankle_y"] = pd.to_numeric(
        df["ankle_y"],
        errors="coerce"
    )

    df["time_sec"] = pd.to_numeric(
        df["time_sec"],
        errors="coerce"
    )

    df["side"] = (
        df["side"]
        .astype(str)
        .str.lower()
    )


candidates = candidates.dropna(
    subset=[
        "frame",
        "ankle_x",
        "ankle_y"
    ]
).copy()


events = events.dropna(
    subset=[
        "frame",
        "ankle_x",
        "ankle_y"
    ]
).copy()


# =====================================
# frameを整数化
# =====================================

candidates["frame"] = (
    candidates["frame"]
    .astype(int)
)

events["frame"] = (
    events["frame"]
    .astype(int)
)


# =====================================
# フレームごとのイベントを作る
# =====================================

candidate_by_frame = {}

for _, row in candidates.iterrows():

    frame = int(row["frame"])

    if frame not in candidate_by_frame:
        candidate_by_frame[frame] = []

    candidate_by_frame[frame].append(row)


event_by_frame = {}

for _, row in events.iterrows():

    frame = int(row["frame"])

    if frame not in event_by_frame:
        event_by_frame[frame] = []

    event_by_frame[frame].append(row)


# =====================================
# 動画を開く
# =====================================

cap = cv2.VideoCapture(
    INPUT_VIDEO
)


if not cap.isOpened():

    print("動画を開けません:")
    print(INPUT_VIDEO)

    raise SystemExit


fps = cap.get(
    cv2.CAP_PROP_FPS
)

width = int(
    cap.get(
        cv2.CAP_PROP_FRAME_WIDTH
    )
)

height = int(
    cap.get(
        cv2.CAP_PROP_FRAME_HEIGHT
    )
)

frame_count = int(
    cap.get(
        cv2.CAP_PROP_FRAME_COUNT
    )
)


print()
print("=====================================")
print("接地イベント確認動画")
print("=====================================")
print()

print(
    f"FPS: {fps:.2f}"
)

print(
    f"解像度: {width} x {height}"
)

print(
    f"フレーム数: {frame_count}"
)

print(
    f"接地候補: {len(candidates)}"
)

print(
    f"最終イベント: {len(events)}"
)

print()


# =====================================
# 出力動画
# =====================================

fourcc = cv2.VideoWriter_fourcc(
    *"mp4v"
)

out = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    fps,
    (width, height)
)


# =====================================
# 動画処理
# =====================================

frame_index = 0


while True:

    ret, frame = cap.read()

    if not ret:
        break


    # =================================
    # 接地候補を表示
    # =================================

    if frame_index in candidate_by_frame:

        for row in candidate_by_frame[
            frame_index
        ]:

            x = int(
                float(row["ankle_x"])
                * width
            )

            y = int(
                float(row["ankle_y"])
                * height
            )

            side = row["side"]


            # 候補マーカー
            cv2.circle(
                frame,
                (x, y),
                10,
                (0, 255, 255),
                -1
            )


            cv2.circle(
                frame,
                (x, y),
                15,
                (255, 255, 255),
                2
            )


            cv2.putText(
                frame,
                "CANDIDATE",
                (x + 15, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 255),
                1,
                cv2.LINE_AA
            )


    # =================================
    # 最終イベントを表示
    # =================================

    if frame_index in event_by_frame:

        for row in event_by_frame[
            frame_index
        ]:

            x = int(
                float(row["ankle_x"])
                * width
            )

            y = int(
                float(row["ankle_y"])
                * height
            )

            side = row["side"]

            event_number = int(
                row["event"]
            )


            # ---------------------------------
            # 最終イベント
            # ---------------------------------

            cv2.circle(
                frame,
                (x, y),
                22,
                (0, 0, 255),
                -1
            )


            cv2.circle(
                frame,
                (x, y),
                30,
                (255, 255, 255),
                3
            )


            # ---------------------------------
            # イベント番号
            # ---------------------------------

            label = (
                f"EVENT {event_number} "
                f"{side.upper()}"
            )


            cv2.putText(
                frame,
                label,
                (x + 35, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )


    # =================================
    # 左上情報
    # =================================

    cv2.rectangle(
        frame,
        (10, 10),
        (360, 100),
        (0, 0, 0),
        -1
    )


    cv2.putText(
        frame,
        "YELLOW = candidate",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )


    cv2.putText(
        frame,
        "RED = final event",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )


    cv2.putText(
        frame,
        f"Frame: {frame_index}",
        (20, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )


    # =================================
    # 出力
    # =================================

    out.write(
        frame
    )


    frame_index += 1


# =====================================
# 終了
# =====================================

cap.release()
out.release()


print()
print("=====================================")
print("接地イベント確認動画を作成しました")
print("=====================================")
print()

print(
    f"動画: {OUTPUT_VIDEO}"
)

print(
    f"接地候補: {len(candidates)}"
)

print(
    f"最終イベント: {len(events)}"
)

print()