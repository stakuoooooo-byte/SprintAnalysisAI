import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# パス
# ============================================================

DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
)

CONTACT_FILE = (
    DATA_DIR /
    "contact_events.csv"
)

ANGLE_FILE = (
    DATA_DIR /
    "angle_history.csv"
)

OUTPUT_FILE = (
    DATA_DIR /
    "stride_phase_metrics.csv"
)


# ============================================================
# データ読み込み
# ============================================================

def load_data():

    if not CONTACT_FILE.exists():

        raise FileNotFoundError(
            f"{CONTACT_FILE} がありません。"
        )

    if not ANGLE_FILE.exists():

        raise FileNotFoundError(
            f"{ANGLE_FILE} がありません。"
        )

    contacts = pd.read_csv(
        CONTACT_FILE
    )

    angles = pd.read_csv(
        ANGLE_FILE
    )

    if contacts.empty:

        raise ValueError(
            "contact_events.csv が空です。"
        )

    if angles.empty:

        raise ValueError(
            "angle_history.csv が空です。"
        )

    return contacts, angles


# ============================================================
# フレームから姿勢データを取得
# ============================================================

def get_frame_data(
    angles,
    frame
):

    rows = angles[
        angles["frame"] == frame
    ]

    if rows.empty:

        return None

    return rows.iloc[0]


# ============================================================
# 1歩単位の指標を作成
# ============================================================

def build_stride_metrics(
    contacts,
    angles
):

    contacts = contacts.copy()

    # --------------------------------------------------------
    # contact_events.csv の実際の列名
    #
    # frame
    # time_sec
    # side
    # --------------------------------------------------------

    contacts["frame"] = pd.to_numeric(
        contacts["frame"],
        errors="coerce"
    )

    contacts["time_sec"] = pd.to_numeric(
        contacts["time_sec"],
        errors="coerce"
    )

    contacts = contacts.dropna(
        subset=[
            "frame",
            "time_sec"
        ]
    )

    # --------------------------------------------------------
    # 時系列順に並べる
    # --------------------------------------------------------

    contacts = contacts.sort_values(
        "time_sec"
    ).reset_index(
        drop=True
    )

    rows = []

    # ========================================================
    # 連続する接地イベントから1歩を作成
    # ========================================================

    for i in range(
        1,
        len(contacts)
    ):

        previous = contacts.iloc[
            i - 1
        ]

        current = contacts.iloc[
            i
        ]

        # ----------------------------------------------------
        # フレーム
        # ----------------------------------------------------

        previous_frame = int(
            previous["frame"]
        )

        current_frame = int(
            current["frame"]
        )

        # ----------------------------------------------------
        # 時刻
        # ----------------------------------------------------

        previous_time = float(
            previous["time_sec"]
        )

        current_time = float(
            current["time_sec"]
        )

        # ----------------------------------------------------
        # 1歩時間
        # ----------------------------------------------------

        stride_time = (
            current_time
            - previous_time
        )

        if stride_time <= 0:

            continue

        # ----------------------------------------------------
        # 左右
        # ----------------------------------------------------

        previous_side = str(
            previous.get(
                "side",
                ""
            )
        )

        current_side = str(
            current.get(
                "side",
                ""
            )
        )

        alternating = (
            previous_side
            != current_side
        )

        # ----------------------------------------------------
        # 接地時の姿勢データ
        # ----------------------------------------------------

        previous_pose = get_frame_data(
            angles,
            previous_frame
        )

        current_pose = get_frame_data(
            angles,
            current_frame
        )

        if (
            previous_pose is None
            or current_pose is None
        ):

            continue

        # ====================================================
        # 基本情報
        # ====================================================

        row = {

            "stride_number":
                i,

            "previous_event_frame":
                previous_frame,

            "current_event_frame":
                current_frame,

            "previous_time_sec":
                previous_time,

            "current_time_sec":
                current_time,

            "previous_side":
                previous_side,

            "current_side":
                current_side,

            "alternating":
                alternating,

            "stride_time_sec":
                stride_time,

            "step_rate_steps_per_sec":
                1.0 / stride_time,

            "step_rate_steps_per_min":
                60.0 / stride_time,
        }

        # ====================================================
        # 接地時角度
        # ====================================================

        angle_columns = [

            "left_knee",
            "right_knee",

            "left_hip",
            "right_hip",

            "left_ankle",
            "right_ankle",

            "left_thigh_angle",
            "right_thigh_angle",

            "trunk_angle",
            "pelvis_angle",

        ]

        for column in angle_columns:

            row[
                f"previous_{column}"
            ] = previous_pose.get(
                column,
                np.nan
            )

            row[
                f"current_{column}"
            ] = current_pose.get(
                column,
                np.nan
            )

        # ====================================================
        # 足首位置
        # ====================================================

        coordinate_columns = [

            "left_ankle_x",
            "left_ankle_y",

            "right_ankle_x",
            "right_ankle_y",

        ]

        for column in coordinate_columns:

            row[
                f"previous_{column}"
            ] = previous_pose.get(
                column,
                np.nan
            )

            row[
                f"current_{column}"
            ] = current_pose.get(
                column,
                np.nan
            )

        # ====================================================
        # 前回接地時の足首
        # ====================================================

        if previous_side == "left":

            previous_x = previous_pose.get(
                "left_ankle_x",
                np.nan
            )

            previous_y = previous_pose.get(
                "left_ankle_y",
                np.nan
            )

        else:

            previous_x = previous_pose.get(
                "right_ankle_x",
                np.nan
            )

            previous_y = previous_pose.get(
                "right_ankle_y",
                np.nan
            )

        # ====================================================
        # 今回接地時の足首
        # ====================================================

        if current_side == "left":

            current_x = current_pose.get(
                "left_ankle_x",
                np.nan
            )

            current_y = current_pose.get(
                "left_ankle_y",
                np.nan
            )

        else:

            current_x = current_pose.get(
                "right_ankle_x",
                np.nan
            )

            current_y = current_pose.get(
                "right_ankle_y",
                np.nan
            )

        # ====================================================
        # 画像上の足首移動量
        #
        # 注意:
        # これはメートルではない
        # ====================================================

        if not any(
            pd.isna(
                [
                    previous_x,
                    previous_y,
                    current_x,
                    current_y,
                ]
            )
        ):

            displacement = np.sqrt(

                (
                    current_x
                    - previous_x
                ) ** 2

                +

                (
                    current_y
                    - previous_y
                ) ** 2

            )

        else:

            displacement = np.nan

        row[
            "ankle_image_displacement"
        ] = displacement

        # ====================================================
        # 結果に追加
        # ====================================================

        rows.append(
            row
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# 統計情報
# ============================================================

def calculate_summary(
    result
):

    if result.empty:

        return {}

    summary = {

        "stride_count":
            len(result),

        "average_stride_time_sec":
            result[
                "stride_time_sec"
            ].mean(),

        "minimum_stride_time_sec":
            result[
                "stride_time_sec"
            ].min(),

        "maximum_stride_time_sec":
            result[
                "stride_time_sec"
            ].max(),

        "average_step_rate_steps_per_sec":
            result[
                "step_rate_steps_per_sec"
            ].mean(),

        "average_step_rate_steps_per_min":
            result[
                "step_rate_steps_per_min"
            ].mean(),

    }

    return summary


# ============================================================
# 実行
# ============================================================

def run():

    print(
        "============================================================"
    )

    print(
        "SprintAnalysisAI"
    )

    print(
        "1歩単位フォーム・ステップ解析"
    )

    print(
        "============================================================"
    )

    # --------------------------------------------------------
    # 読み込み
    # --------------------------------------------------------

    contacts, angles = load_data()

    print(
        f"接地イベント数: {len(contacts)}"
    )

    print(
        f"骨格フレーム数: {len(angles)}"
    )

    # --------------------------------------------------------
    # 1歩解析
    # --------------------------------------------------------

    result = build_stride_metrics(
        contacts,
        angles
    )

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    result.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()

    print(
        f"1歩データ数: {len(result)}"
    )

    # --------------------------------------------------------
    # 統計
    # --------------------------------------------------------

    summary = calculate_summary(
        result
    )

    if summary:

        print()

        print(
            "=============================="
        )

        print(
            "1歩データ統計"
        )

        print(
            "=============================="
        )

        print(
            f"1歩データ数: "
            f"{summary['stride_count']}"
        )

        print(
            f"平均1歩時間: "
            f"{summary['average_stride_time_sec']:.3f} 秒"
        )

        print(
            f"最短1歩時間: "
            f"{summary['minimum_stride_time_sec']:.3f} 秒"
        )

        print(
            f"最長1歩時間: "
            f"{summary['maximum_stride_time_sec']:.3f} 秒"
        )

        print(
            f"平均ピッチ: "
            f"{summary['average_step_rate_steps_per_sec']:.2f} steps/s"
        )

        print(
            f"平均ピッチ: "
            f"{summary['average_step_rate_steps_per_min']:.1f} steps/min"
        )

    # --------------------------------------------------------
    # 注意事項
    # --------------------------------------------------------

    print()

    print(
        "注意:"
    )

    print(
        "ankle_image_displacement は画像上の移動量です。"
    )

    print(
        "現時点ではメートル単位のストライド長・速度"
    )

    print(
        "として使用しません。"
    )

    print()

    print(
        f"保存先: {OUTPUT_FILE}"
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    run()