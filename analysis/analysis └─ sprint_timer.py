import cv2


def calculate_time(
    video_path,
    start_frame,
    end_frame
):
    """
    動画の開始フレームと終了フレームから
    走行時間を計算する
    """

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


if __name__ == "__main__":

    video_path = (
        "videos/test_browser.mp4"
    )

    # テスト用
    start_frame = 0
    end_frame = 210

    result = calculate_time(
        video_path,
        start_frame,
        end_frame
    )

    print()
    print("===== スプリントタイム計測 =====")
    print()

    print(
        f"FPS: {result['fps']:.2f}"
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
        f"走行時間: "
        f"{result['time_sec']:.3f} 秒"
    )