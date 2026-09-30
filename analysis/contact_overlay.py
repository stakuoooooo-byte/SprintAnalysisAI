import cv2
import pandas as pd
import os


# =====================================
# 設定
# =====================================

INPUT_VIDEO = "videos/test_browser.mp4"
OUTPUT_VIDEO = "videos/contact_analysis.mp4"

CONTACT_CSV = "data/contact_candidates.csv"

FPS = 30.0


# =====================================
# 接地候補CSV読み込み
# =====================================

contacts = pd.read_csv(CONTACT_CSV)

if contacts.empty:
    raise ValueError("接地候補データが空です。")


# 数値化
contacts["frame"] = pd.to_numeric(
    contacts["frame"],
    errors="coerce"
)

contacts["ankle_x"] = pd.to_numeric(
    contacts["ankle_x"],
    errors="coerce"
)

contacts["ankle_y"] = pd.to_numeric(
    contacts["ankle_y"],
    errors="coerce"
)

contacts["side"] = contacts["side"].astype(str).str.lower()

contacts = contacts.dropna(
    subset=["frame", "ankle_x", "ankle_y"]
)

contacts["frame"] = contacts["frame"].astype(int)


# =====================================
# 動画を開く
# =====================================

cap = cv2.VideoCapture(INPUT_VIDEO)

if not cap.isOpened():
    raise ValueError(
        f"入力動画を開けません: {INPUT_VIDEO}"
    )


width = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)

video_fps = cap.get(
    cv2.CAP_PROP_FPS
)

if video_fps <= 0:
    video_fps = FPS


# =====================================
# フレームごとの接地候補を作成
# =====================================

contacts_by_frame = {}

for _, row in contacts.iterrows():

    frame_no = int(row["frame"])

    if frame_no not in contacts_by_frame:
        contacts_by_frame[frame_no] = []

    contacts_by_frame[frame_no].append(
        {
            "side": row["side"],
            "x": float(row["ankle_x"]),
            "y": float(row["ankle_y"]),
        }
    )


# =====================================
# 出力動画
# =====================================

fourcc = cv2.VideoWriter_fourcc(
    *"mp4v"
)

out = cv2.VideoWriter(
    OUTPUT_VIDEO,
    fourcc,
    video_fps,
    (width, height)
)


if not out.isOpened():
    raise ValueError(
        f"出力動画を作成できません: {OUTPUT_VIDEO}"
    )


# =====================================
# 動画処理
# =====================================

frame_index = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break


    # ---------------------------------
    # 接地候補があるフレーム
    # ---------------------------------

    current_contacts = contacts_by_frame.get(
        frame_index,
        []
    )


    for contact in current_contacts:

        side = contact["side"]

        # 正規化座標 → ピクセル座標
        x = int(
            contact["x"] * width
        )

        y = int(
            contact["y"] * height
        )


        # 画面外対策
        x = max(
            0,
            min(width - 1, x)
        )

        y = max(
            0,
            min(height - 1, y)
        )


        # ---------------------------------
        # 接地マーカー
        # ---------------------------------

        cv2.circle(
            frame,
            (x, y),
            18,
            (0, 255, 255),
            -1
        )

        cv2.circle(
            frame,
            (x, y),
            25,
            (255, 255, 255),
            3
        )


        # ---------------------------------
        # 左右ラベル
        # ---------------------------------

        if side == "left":

            label = "L CONTACT"

        else:

            label = "R CONTACT"


        cv2.putText(
            frame,
            label,
            (x + 25, y - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )


    # ---------------------------------
    # 接地候補数
    # ---------------------------------

    if current_contacts:

        cv2.putText(
            frame,
            f"CONTACT CANDIDATE: {len(current_contacts)}",
            (40, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            3
        )


    # ---------------------------------
    # フレーム番号
    # ---------------------------------

    cv2.putText(
        frame,
        f"Frame: {frame_index}",
        (40, height - 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    out.write(frame)

    frame_index += 1


# =====================================
# 終了
# =====================================

cap.release()
out.release()


print("=====================================")
print("接地候補マーカー動画を作成しました")
print(f"動画: {OUTPUT_VIDEO}")
print(f"CSV: {CONTACT_CSV}")
print(f"接地候補数: {len(contacts)}")
print("=====================================")