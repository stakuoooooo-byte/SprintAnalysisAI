import pandas as pd
import os


# =====================================
# 設定
# =====================================

INPUT_CSV = "data/contact_candidates.csv"

OUTPUT_CSV = "data/contact_events.csv"

# 同じ足の接地イベント間の最小時間
MIN_INTERVAL_SEC = 0.16

# 左右を合わせたイベント間の最小時間
GLOBAL_MIN_INTERVAL_SEC = 0.10

# 接地候補として許容する足首の上下速度
# 値が小さいほど厳しくなる
MAX_ABSOLUTE_VERTICAL_VELOCITY = 0.20


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

    print(
        "接地候補データがありません。"
    )

    raise SystemExit


required_columns = [
    "frame",
    "time_sec",
    "side",
    "ankle_x",
    "ankle_y",
    "vertical_velocity"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print(
        "必要な列がありません："
    )

    print(
        missing_columns
    )

    raise SystemExit


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

df["ankle_y"] = pd.to_numeric(
    df["ankle_y"],
    errors="coerce"
)

df["vertical_velocity"] = pd.to_numeric(
    df["vertical_velocity"],
    errors="coerce"
)


df = df.dropna(
    subset=[
        "frame",
        "time_sec",
        "side",
        "ankle_x",
        "ankle_y",
        "vertical_velocity"
    ]
)


# =====================================
# 時系列順
# =====================================

df = df.sort_values(
    "time_sec"
).reset_index(
    drop=True
)


# =====================================
# ① 足首の上下速度によるフィルター
# =====================================

filtered = df[
    df["vertical_velocity"].abs()
    <= MAX_ABSOLUTE_VERTICAL_VELOCITY
].copy()


# =====================================
# ② 接地候補を時間順に整理
# =====================================

events = []

last_time = {
    "left": -999.0,
    "right": -999.0
}

last_global_time = -999.0


for _, row in filtered.iterrows():

    side = str(
        row["side"]
    ).lower()

    if side not in [
        "left",
        "right"
    ]:

        continue


    time_sec = float(
        row["time_sec"]
    )

    frame = int(
        row["frame"]
    )


    # =================================
    # 同じ足の連続候補を除外
    # =================================

    if (
        time_sec
        - last_time[side]
        < MIN_INTERVAL_SEC
    ):

        continue


    # =================================
    # 全体として近すぎるイベントを除外
    # =================================

    if (
        time_sec
        - last_global_time
        < GLOBAL_MIN_INTERVAL_SEC
    ):

        continue


    # =================================
    # イベント登録
    # =================================

    events.append({

        "event":
            len(events) + 1,

        "frame":
            frame,

        "time_sec":
            time_sec,

        "side":
            side,

        "ankle_x":
            float(row["ankle_x"]),

        "ankle_y":
            float(row["ankle_y"]),

        "vertical_velocity":
            float(
                row["vertical_velocity"]
            )

    })


    last_time[side] = time_sec

    last_global_time = time_sec


# =====================================
# DataFrame
# =====================================

events_df = pd.DataFrame(
    events
)


# =====================================
# 保存
# =====================================

os.makedirs(
    "data",
    exist_ok=True
)


events_df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


# =====================================
# 結果表示
# =====================================

print(
    "接地イベント整理完了"
)

print(
    f"元の候補数: {len(df)}"
)

print(
    f"速度フィルター後: {len(filtered)}"
)

print(
    f"整理後イベント数: {len(events_df)}"
)

print(
    f"保存先: {OUTPUT_CSV}"
)


print()


if not events_df.empty:

    print(
        events_df.head(30).to_string(
            index=False
        )
    )