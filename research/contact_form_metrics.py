from pathlib import Path
import pandas as pd


DATA_DIR = Path("data")


def run_contact_form_analysis():
    """
    接地イベントと骨格時系列データを結合し、
    接地瞬間のフォーム指標を抽出する。
    """

    angle_path = DATA_DIR / "angle_history.csv"
    events_path = DATA_DIR / "contact_events.csv"

    if not angle_path.exists():
        raise FileNotFoundError(
            "data/angle_history.csv が見つかりません。"
        )

    if not events_path.exists():
        raise FileNotFoundError(
            "data/contact_events.csv が見つかりません。"
        )

    angles = pd.read_csv(angle_path)
    events = pd.read_csv(events_path)

    # frame番号を整数化
    angles["frame"] = angles["frame"].astype(int)

    if "frame" in events.columns:
        events["frame"] = events["frame"].astype(int)

    # ------------------------------------------------
    # 接地イベントのframeに最も近い骨格フレームを取得
    # ------------------------------------------------

    results = []

    for _, event in events.iterrows():

        event_frame = int(event["frame"])

        # 完全一致するフレームを探す
        exact = angles[
            angles["frame"] == event_frame
        ]

        if len(exact) > 0:

            row = exact.iloc[0]

        else:

            # 万一存在しない場合は最も近いフレーム
            distances = (
                angles["frame"] - event_frame
            ).abs()

            nearest_index = distances.idxmin()

            row = angles.loc[nearest_index]

        result = {
            "event_frame": event_frame,
        }

        # ------------------------------------------------
        # event側の情報
        # ------------------------------------------------

        for column in events.columns:

            if column != "frame":

                result[f"event_{column}"] = event[column]

        # ------------------------------------------------
        # フォーム指標
        # ------------------------------------------------

        metrics = [
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

        for metric in metrics:

            if metric in angles.columns:

                result[metric] = row[metric]

        results.append(result)

    # ------------------------------------------------
    # DataFrame
    # ------------------------------------------------

    result_df = pd.DataFrame(results)

    # ------------------------------------------------
    # 保存
    # ------------------------------------------------

    output_path = (
        DATA_DIR /
        "contact_form_metrics.csv"
    )

    result_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("=" * 60)
    print("SprintAnalysisAI")
    print("接地時フォーム解析")
    print("=" * 60)

    print(
        f"\n接地イベント数: {len(result_df)}"
    )

    print(
        f"保存先: {output_path}"
    )

    if len(result_df) > 0:

        print("\n取得した指標:")

        for column in result_df.columns:

            print(f"- {column}")

    return result_df


if __name__ == "__main__":

    run_contact_form_analysis()