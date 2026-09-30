import pandas as pd
import os


# =====================================
# 設定
# =====================================

INPUT_CSV = "data/contact_candidates.csv"

OUTPUT_CSV = "data/contact_events.csv"

# 同じ足の接地間隔
MIN_SAME_SIDE_INTERVAL_SEC = 0.20

# 左右の接地が近すぎる場合
MIN_GLOBAL_INTERVAL_SEC = 0.08


# =====================================
# CSV読み込み
# =====================================

df = pd.read_csv(
    INPUT_CSV
)


if df.empty:

    print(
        "接地候補データがありません。"
    )

    raise SystemExit


# =====================================
# 必要な列
# =====================================

required_columns = [

    "candidate",
    "frame",
    "time_sec",
    "ankle_x",
    "ankle_y",
    "vertical_velocity",
    "side"

]


missing_columns = [

    column
    for column in required_columns
    if column not in df.columns

]


if missing_columns:

    print(
        "必要な列がありません:"
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
        "ankle_x",
        "ankle_y",
        "vertical_velocity",
        "side"
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
# 接地イベント整理
# =====================================

events = []


last_time = {
    "left": -999.0,
    "right": -999.0
}


last_global_time = -999.0

last_side = None


for _, row in df.iterrows():

    side = str(
        row["side"]
    ).lower()

    time_sec = float(
        row["time_sec"]
    )

    frame = int(
        row["frame"]
    )


    if side not in [
        "left",
        "right"
    ]:

        continue


    # =================================
    # 同じ足の近すぎる候補を除外
    # =================================

    if (
        time_sec
        - last_time[side]
        < MIN_SAME_SIDE_INTERVAL_SEC
    ):

        continue


    # =================================
    # 全体として近すぎる候補を除外
    # =================================

    if (
        time_sec
        - last_global_time
        < MIN_GLOBAL_INTERVAL_SEC
    ):

        continue


    # =================================
    # 左右交互性
    # =================================
    #
    # 直前と同じ足が続いた場合、
    # そのまま採用するのではなく、
    # 近い候補の中から時間的に妥当なものを残す。
    #
    # 完全な交互性を強制すると、
    # 実際の動作を誤って消す可能性があるため、
    # ここでは「同じ足の連続を抑制」する。

    if (
        last_side == side
        and
        time_sec
        - last_time[side]
        < 0.35
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
            float(
                row["ankle_x"]
            ),

        "ankle_y":
            float(
                row["ankle_y"]
            ),

        "vertical_velocity":
            float(
                row["vertical_velocity"]
            )

    })


    last_time[side] = time_sec

    last_global_time = time_sec

    last_side = side


# =====================================
# DataFrame
# =====================================

events_df = pd.DataFrame(
    events
)


# =====================================
# イベント間時間
# =====================================

if len(events_df) >= 2:

    events_df[
        "interval_sec"
    ] = (
        events_df[
            "time_sec"
        ].diff()
    )

else:

    events_df[
        "interval_sec"
    ] = []


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
    f"最終イベント数: {len(events_df)}"
)

print(
    f"保存先: {OUTPUT_CSV}"
)


print()


if not events_df.empty:

    print(
        events_df.to_string(
            index=False
        )
    )