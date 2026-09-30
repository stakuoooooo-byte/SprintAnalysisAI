import pandas as pd
import os


# =====================================
# 設定
# =====================================

INPUT_CSV = "data/contact_events.csv"

OUTPUT_CSV = "data/contact_sequence.csv"


# =====================================
# CSV読み込み
# =====================================

df = pd.read_csv(
    INPUT_CSV
)


# =====================================
# データ確認
# =====================================

if df.empty:

    print("接地イベントがありません。")

    raise SystemExit


# =====================================
# 時間順に並べる
# =====================================

df = df.sort_values(
    ["frame", "side"]
).reset_index(
    drop=True
)


# =====================================
# ステップ列作成
# =====================================

sequence = []

last_side = None

last_frame = None

step_number = 0


for _, row in df.iterrows():

    side = row["side"]

    frame = int(
        row["frame"]
    )

    time_sec = float(
        row["time_sec"]
    )


    # -----------------------------
    # 同じ足の連続検出を除外
    # -----------------------------

    if side == last_side:

        continue


    # -----------------------------
    # ステップ番号
    # -----------------------------

    step_number += 1


    # -----------------------------
    # 前回接地からの時間
    # -----------------------------

    if last_frame is None:

        interval_sec = None

    else:

        interval_sec = (
            frame - last_frame
        ) / 30.0


    sequence.append({

        "step": step_number,

        "frame": frame,

        "time_sec": time_sec,

        "side": side,

        "interval_sec":
            interval_sec

    })


    last_side = side

    last_frame = frame


# =====================================
# DataFrame化
# =====================================

sequence_df = pd.DataFrame(
    sequence
)


# =====================================
# 保存
# =====================================

os.makedirs(
    "data",
    exist_ok=True
)


sequence_df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 結果表示
# =====================================

print(
    "接地ステップ列の作成完了"
)

print(
    f"元イベント数: {len(df)}"
)

print(
    f"ステップ数: {len(sequence_df)}"
)

print(
    f"保存先: {OUTPUT_CSV}"
)

print()

print(
    sequence_df.head(30).to_string(
        index=False
    )
)