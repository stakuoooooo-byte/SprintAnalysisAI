"""
SprintAnalysisAI
研究ベースのスプリントフォーム評価項目

注意:
このファイルでは「全選手に共通する唯一の理想フォーム」を定義しない。
研究で利用されている指標を整理し、
実測値・比較基準・信頼度を分けて扱う。
"""

RESEARCH_METRICS = {

    # =========================
    # パフォーマンス
    # =========================

    "step_rate": {
        "name": "ステップ頻度",
        "unit": "steps/s",
        "category": "performance",
        "available": True,
        "importance": "high",
    },

    "step_interval": {
        "name": "ステップ間隔",
        "unit": "s",
        "category": "performance",
        "available": True,
        "importance": "high",
    },

    "stride_time": {
        "name": "ストライド時間",
        "unit": "s",
        "category": "performance",
        "available": True,
        "importance": "high",
    },

    # =========================
    # 接地時フォーム
    # =========================

    "contact_knee_angle": {
        "name": "接地時膝関節角度",
        "unit": "deg",
        "category": "contact",
        "available": True,
        "importance": "high",
    },

    "contact_hip_angle": {
        "name": "接地時股関節角度",
        "unit": "deg",
        "category": "contact",
        "available": True,
        "importance": "high",
    },

    "contact_ankle_angle": {
        "name": "接地時足関節角度",
        "unit": "deg",
        "category": "contact",
        "available": True,
        "importance": "medium",
    },

    "contact_thigh_angle": {
        "name": "接地時大腿角度",
        "unit": "deg",
        "category": "contact",
        "available": True,
        "importance": "high",
    },

    "contact_trunk_angle": {
        "name": "接地時体幹角度",
        "unit": "deg",
        "category": "contact",
        "available": True,
        "importance": "high",
    },

    "contact_pelvis_angle": {
        "name": "接地時骨盤角度",
        "unit": "deg",
        "category": "contact",
        "available": True,
        "importance": "medium",
    },

    # =========================
    # 左右差
    # =========================

    "left_right_asymmetry": {
        "name": "左右非対称性",
        "unit": "%",
        "category": "symmetry",
        "available": True,
        "importance": "high",
    },

    # =========================
    # 研究上重要だが
    # 現在のシステムでは未実装
    # =========================

    "ground_contact_time": {
        "name": "接地時間",
        "unit": "s",
        "category": "temporal",
        "available": False,
        "importance": "high",
        "reason": "接地開始・離地イベントの精度向上が必要",
    },

    "flight_time": {
        "name": "滞空時間",
        "unit": "s",
        "category": "temporal",
        "available": False,
        "importance": "high",
        "reason": "接地イベントから離地イベントを安定して取得する必要がある",
    },

    "stride_length": {
        "name": "ストライド長",
        "unit": "m",
        "category": "spatial",
        "available": False,
        "importance": "high",
        "reason": "絶対距離キャリブレーションが未実装",
    },

    "maximum_thigh_extension": {
        "name": "最大大腿伸展",
        "unit": "deg",
        "category": "swing",
        "available": False,
        "importance": "high",
        "reason": "ステップ単位の最大値抽出が必要",
    },

    "maximum_thigh_flexion": {
        "name": "最大大腿屈曲",
        "unit": "deg",
        "category": "swing",
        "available": False,
        "importance": "high",
        "reason": "ステップ単位の最大値抽出が必要",
    },

    "pelvic_tilt": {
        "name": "骨盤傾斜",
        "unit": "deg",
        "category": "pelvis",
        "available": True,
        "importance": "medium",
    },

    "trunk_angle": {
        "name": "体幹角度",
        "unit": "deg",
        "category": "trunk",
        "available": True,
        "importance": "high",
    },
}


def get_available_metrics():

    return {
        key: value
        for key, value in RESEARCH_METRICS.items()
        if value["available"]
    }


def get_unavailable_metrics():

    return {
        key: value
        for key, value in RESEARCH_METRICS.items()
        if not value["available"]
    }


def print_report():

    print("=" * 60)
    print("SprintAnalysisAI")
    print("研究ベース フォーム評価項目")
    print("=" * 60)

    print("\n【現在利用可能】")

    for key, metric in get_available_metrics().items():

        print(
            f"- {metric['name']}"
            f" / {metric['unit']}"
            f" / importance={metric['importance']}"
        )

    print("\n【今後実装】")

    for key, metric in get_unavailable_metrics().items():

        print(
            f"- {metric['name']}"
            f" → {metric['reason']}"
        )

    print("\n※単一の「理想フォーム」を設定しない。")


if __name__ == "__main__":
    print_report()