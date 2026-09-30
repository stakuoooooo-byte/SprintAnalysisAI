import cv2


# =====================================
# 設定
# =====================================

DISTANCE_M = 50.0


# =====================================
# スプリントタイム計算
# =====================================

def calculate_time(
    video_path,
    start_frame,
    end_frame
):

    cap = cv2.VideoCapture(
        video_path
    )

    if not cap.isOpened():

        raise ValueError(
            "動画を開けませんでした。"
        )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    cap.release()

    if fps <= 0:

        raise ValueError(
            "FPSを取得できませんでした。"
        )

    time_sec = (
        end_frame - start_frame
    ) / fps

    return {
        "fps": fps,
        "start_frame": start_frame,
        "end_frame": end_frame,
        "time_sec": time_sec
    }


# =====================================
# 平均速度計算
# =====================================

def calculate_speed(
    distance_m,
    time_sec
):

    if time_sec <= 0:

        raise ValueError(
            "時間が0以下です。"
        )

    speed_mps = (
        distance_m / time_sec
    )

    return speed_mps


# =====================================
# テスト
# =====================================

if __name__ == "__main__":

    video_path = (
        "videos/test_browser.mp4"
    )

    start_frame = 0
    end_frame = 210

    result = calculate_time(
        video_path,
        start_frame,
        end_frame
    )

    speed = calculate_speed(
        DISTANCE_M,
        result["time_sec"]
    )

    print()
    print(
        "===== スプリント分析 ====="
    )
    print()

    print(
        f"FPS: "
        f"{result['fps']:.2f}"
    )

    print(
        f"開始フレーム: "
        f"{result['start_frame']}"
    )

    print(
        f"終了フレーム: "
        f"{result['end_frame']}"
    )

    print(
        f"距離: "
        f"{DISTANCE_M:.1f} m"
    )

    print(
        f"タイム: "
        f"{result['time_sec']:.3f} 秒"
    )

    print(
        f"平均速度: "
        f"{speed:.2f} m/s"
    )