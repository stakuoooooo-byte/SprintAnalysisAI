import pandas as pd
from pathlib import Path


# ==========================================
# SprintAnalysisAI
# スプリント総合分析データ作成
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

STEP_FILE = DATA_DIR / "step_metrics.csv"
ANGLE_FILE = DATA_DIR / "contact_angle_analysis.csv"
STRIDE_FILE = DATA_DIR / "stride_analysis.csv"

OUTPUT_FILE = DATA_DIR / "performance_summary.csv"


# ==========================================
# ファイル存在確認
# ==========================================

required_files = [
    STEP_FILE,
    ANGLE_FILE,
    STRIDE_FILE,
]

for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            f"必要なファイルがありません: {file_path}"
        )


# ==========================================
# データ読み込み
# ==========================================

step = pd.read_csv(STEP_FILE)
angle = pd.read_csv(ANGLE_FILE)
stride = pd.read_csv(STRIDE_FILE)


# ==========================================
# 数値取得用関数
# ==========================================

def get_value(df, column, default=None):

    if column not in df.columns:
        return default

    if len(df) == 0:
        return default

    value = df.iloc[0][column]

    if pd.isna(value):
        return default

    return value


# ==========================================
# ステップ分析
# ==========================================

total_events = get_value(
    step,
    "total_contact_events"
)

left_events = get_value(
    step,
    "left_contact_events"
)

right_events = get_value(
    step,
    "right_contact_events"
)

event_duration = get_value(
    step,
    "event_duration_sec"
)

average_step_interval = get_value(
    step,
    "average_step_interval_sec"
)

min_step_interval = get_value(
    step,
    "minimum_step_interval_sec"
)

max_step_interval = get_value(
    step,
    "maximum_step_interval_sec"
)

pitch_steps_sec = get_value(
    step,
    "pitch_steps_per_sec"
)

pitch_steps_min = get_value(
    step,
    "pitch_steps_per_min"
)

left_contact_interval = get_value(
    step,
    "left_average_contact_interval_sec"
)

right_contact_interval = get_value(
    step,
    "right_average_contact_interval_sec"
)

left_right_difference = get_value(
    step,
    "left_right_difference_sec"
)

left_right_ratio = get_value(
    step,
    "left_right_ratio"
)

event_frequency = get_value(
    step,
    "event_frequency_steps_per_sec"
)


# ==========================================
# 接地時角度分析
# ==========================================

contact_knee = angle[
    "contact_knee_angle"
].mean()

contact_hip = angle[
    "contact_hip_angle"
].mean()

contact_ankle = angle[
    "contact_ankle_angle"
].mean()


# ==========================================
# 左右別角度
# ==========================================

left_angle = angle[
    angle["side"] == "left"
]

right_angle = angle[
    angle["side"] == "right"
]


left_knee = left_angle[
    "contact_knee_angle"
].mean()

right_knee = right_angle[
    "contact_knee_angle"
].mean()

left_hip = left_angle[
    "contact_hip_angle"
].mean()

right_hip = right_angle[
    "contact_hip_angle"
].mean()

left_ankle = left_angle[
    "contact_ankle_angle"
].mean()

right_ankle = right_angle[
    "contact_ankle_angle"
].mean()


# ==========================================
# ストライド分析
# ==========================================

average_stride_time = stride[
    "stride_time_sec"
].dropna().mean()


left_stride_image = stride[
    stride["side"] == "left"
]["stride_horizontal_displacement"].mean()


right_stride_image = stride[
    stride["side"] == "right"
]["stride_horizontal_displacement"].mean()


# ==========================================
# 総合分析データ
# ==========================================

summary = {

    # ------------------------------
    # 接地イベント
    # ------------------------------

    "total_contact_events":
        total_events,

    "left_contact_events":
        left_events,

    "right_contact_events":
        right_events,

    "event_duration_sec":
        event_duration,


    # ------------------------------
    # ピッチ
    # ------------------------------

    "average_step_interval_sec":
        average_step_interval,

    "minimum_step_interval_sec":
        min_step_interval,

    "maximum_step_interval_sec":
        max_step_interval,

    "pitch_steps_per_sec":
        pitch_steps_sec,

    "pitch_steps_per_min":
        pitch_steps_min,

    "event_frequency_steps_per_sec":
        event_frequency,


    # ------------------------------
    # 左右バランス
    # ------------------------------

    "left_average_contact_interval_sec":
        left_contact_interval,

    "right_average_contact_interval_sec":
        right_contact_interval,

    "left_right_difference_sec":
        left_right_difference,

    "left_right_ratio":
        left_right_ratio,


    # ------------------------------
    # 接地時角度
    # ------------------------------

    "contact_knee_angle_avg":
        contact_knee,

    "contact_hip_angle_avg":
        contact_hip,

    "contact_ankle_angle_avg":
        contact_ankle,


    # ------------------------------
    # 左脚
    # ------------------------------

    "left_knee_angle_avg":
        left_knee,

    "left_hip_angle_avg":
        left_hip,

    "left_ankle_angle_avg":
        left_ankle,


    # ------------------------------
    # 右脚
    # ------------------------------

    "right_knee_angle_avg":
        right_knee,

    "right_hip_angle_avg":
        right_hip,

    "right_ankle_angle_avg":
        right_ankle,


    # ------------------------------
    # ストライド時間
    # ------------------------------

    "average_stride_time_sec":
        average_stride_time,


    # ------------------------------
    # 画像上のストライド
    # ------------------------------
    #
    # 注意：
    # カメラ追従撮影のため、
    # メートルには変換しない。
    #

    "left_stride_image_displacement":
        left_stride_image,

    "right_stride_image_displacement":
        right_stride_image
}


# ==========================================
# DataFrame化
# ==========================================

summary_df = pd.DataFrame(
    [summary]
)


# ==========================================
# CSV保存
# ==========================================

summary_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# コンソール表示
# ==========================================

print()
print("========================================")
print("      SprintAnalysisAI")
print("      スプリント総合分析")
print("========================================")
print()


def print_value(name, value):

    if value is None:

        print(f"{name}: None")

    elif isinstance(value, (float, int)):

        print(f"{name}: {value:.3f}")

    else:

        print(f"{name}: {value}")


# 接地イベント

print("【接地イベント】")

print_value(
    "総接地イベント数",
    total_events
)

print_value(
    "左脚イベント数",
    left_events
)

print_value(
    "右脚イベント数",
    right_events
)

print_value(
    "イベント区間",
    event_duration
)

print()


# ピッチ

print("【ピッチ・ステップ】")

print_value(
    "平均ステップ間隔",
    average_step_interval
)

print_value(
    "最小ステップ間隔",
    min_step_interval
)

print_value(
    "最大ステップ間隔",
    max_step_interval
)

print_value(
    "ピッチ steps/sec",
    pitch_steps_sec
)

print_value(
    "ピッチ steps/min",
    pitch_steps_min
)

print()


# 左右バランス

print("【左右バランス】")

print_value(
    "左→左接地間隔",
    left_contact_interval
)

print_value(
    "右→右接地間隔",
    right_contact_interval
)

print_value(
    "左右差",
    left_right_difference
)

print_value(
    "左右比",
    left_right_ratio
)

print()


# 角度

print("【接地時角度】")

print_value(
    "膝角度",
    contact_knee
)

print_value(
    "股関節角度",
    contact_hip
)

print_value(
    "足関節角度",
    contact_ankle
)

print()


# 左右角度

print("【左右別角度】")

print_value(
    "左膝",
    left_knee
)

print_value(
    "右膝",
    right_knee
)

print_value(
    "左股関節",
    left_hip
)

print_value(
    "右股関節",
    right_hip
)

print_value(
    "左足関節",
    left_ankle
)

print_value(
    "右足関節",
    right_ankle
)

print()


# ストライド

print("【ストライド】")

print_value(
    "平均ストライド時間",
    average_stride_time
)

print_value(
    "左画像ストライド",
    left_stride_image
)

print_value(
    "右画像ストライド",
    right_stride_image
)

print()

print("※画像ストライドはメートルではありません。")
print("※カメラ追従撮影のため、現段階では参考値です。")

print()

print("========================================")
print("保存完了")
print("========================================")

print()
print(f"保存先:")
print(OUTPUT_FILE)