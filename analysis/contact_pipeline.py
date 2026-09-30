from pathlib import Path

import pandas as pd

from analysis.contact_detector import ContactDetector


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def run_contact_analysis(
    angle_history_path,
    fps=30.0
):
    """
    angle_history.csv から接地候補を検出して
    data/contact_candidates.csv に保存する。
    """

    angle_history_path = Path(
        angle_history_path
    )

    # ==========================================
    # CSV読み込み
    # ==========================================

    if not angle_history_path.exists():
        raise FileNotFoundError(
            f"angle_history.csv がありません: "
            f"{angle_history_path}"
        )

    df = pd.read_csv(
        angle_history_path
    )

    # ==========================================
    # 必要な列
    # ==========================================

    required_columns = [
        "frame",
        "left_ankle_x",
        "left_ankle_y",
        "right_ankle_x",
        "right_ankle_y"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "angle_history.csv に必要な列がありません: "
            + str(missing_columns)
        )

    # ==========================================
    # FPS
    # ==========================================

    fps = float(fps)

    if fps <= 0:
        raise ValueError(
            "FPSは0より大きい値にしてください。"
        )

    # ==========================================
    # 接地検出
    # ==========================================

    detector = ContactDetector(
        fps=fps
    )

    result = detector.analyze(
        df
    )

    # ==========================================
    # 左右
    # ==========================================

    left_contacts = result[
        "left"
    ].copy()

    right_contacts = result[
        "right"
    ].copy()

    # ==========================================
    # 左右を統合
    # ==========================================

    contact_candidates = pd.concat(
        [
            left_contacts,
            right_contacts
        ],
        ignore_index=True
    )

    # ==========================================
    # 時間順に並べる
    # ==========================================

    if not contact_candidates.empty:

        contact_candidates = (
            contact_candidates
            .sort_values(
                "time_sec"
            )
            .reset_index(
                drop=True
            )
        )

        contact_candidates.insert(
            0,
            "candidate",
            range(
                1,
                len(contact_candidates) + 1
            )
        )

    # ==========================================
    # 保存
    # ==========================================

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        DATA_DIR /
        "contact_candidates.csv"
    )

    contact_candidates.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    # ==========================================
    # 結果
    # ==========================================

    return {
        "data": contact_candidates,
        "left_count": len(left_contacts),
        "right_count": len(right_contacts),
        "total_count": len(contact_candidates),
        "output_path": output_path
    }