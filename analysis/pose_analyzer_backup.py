import cv2
import mediapipe as mp
import math


class PoseAnalyzer:

    def __init__(self):

        model_path = "models/pose_landmarker_full.task"

        base_options = mp.tasks.BaseOptions(
            model_asset_path=model_path
        )

        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.landmarker = (
            mp.tasks.vision.PoseLandmarker.create_from_options(
                options
            )
        )

    def calculate_angle(self, a, b, c):
        """
        3点A-B-Cの角度を計算する
        Bが関節
        """

        ba = (
            a.x - b.x,
            a.y - b.y
        )

        bc = (
            c.x - b.x,
            c.y - b.y
        )

        dot_product = (
            ba[0] * bc[0]
            + ba[1] * bc[1]
        )

        magnitude_ba = math.sqrt(
            ba[0] ** 2
            + ba[1] ** 2
        )

        magnitude_bc = math.sqrt(
            bc[0] ** 2
            + bc[1] ** 2
        )

        if magnitude_ba == 0 or magnitude_bc == 0:
            return 0.0

        cosine = (
            dot_product
            / (magnitude_ba * magnitude_bc)
        )

        cosine = max(-1.0, min(1.0, cosine))

        angle = math.degrees(
            math.acos(cosine)
        )

        return angle

    def analyze_video(self, input_path, output_path):

        cap = cv2.VideoCapture(input_path)

        if not cap.isOpened():
            raise ValueError(
                "動画を開けませんでした。"
            )

        fps = cap.get(cv2.CAP_PROP_FPS)

        if fps <= 0:
            fps = 30

        width = int(
            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        height = int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        frames = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        fourcc = cv2.VideoWriter_fourcc(
            *"mp4v"
        )

        out = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (width, height)
        )

        frame_index = 0

        angle_history = []

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            timestamp_ms = int(
                frame_index * 1000 / fps
            )

            result = self.landmarker.detect_for_video(
                mp_image,
                timestamp_ms
            )

            if result.pose_landmarks:

                landmarks = result.pose_landmarks[0]

                # -------------------------
                # 左脚
                # -------------------------

                left_hip = landmarks[23]
                left_knee = landmarks[25]
                left_ankle = landmarks[27]
                left_foot = landmarks[31]

                # -------------------------
                # 右脚
                # -------------------------

                right_hip = landmarks[24]
                right_knee = landmarks[26]
                right_ankle = landmarks[28]
                right_foot = landmarks[32]

                # -------------------------
                # 左膝角度
                # -------------------------

                left_knee_angle = self.calculate_angle(
                    left_hip,
                    left_knee,
                    left_ankle
                )

                # -------------------------
                # 右膝角度
                # -------------------------

                right_knee_angle = self.calculate_angle(
                    right_hip,
                    right_knee,
                    right_ankle
                )

                # -------------------------
                # 左股関節角度
                # -------------------------

                left_shoulder = landmarks[11]

                left_hip_angle = self.calculate_angle(
                    left_shoulder,
                    left_hip,
                    left_knee
                )

                # -------------------------
                # 右股関節角度
                # -------------------------

                right_shoulder = landmarks[12]

                right_hip_angle = self.calculate_angle(
                    right_shoulder,
                    right_hip,
                    right_knee
                )

                # -------------------------
                # 左足首角度
                # -------------------------

                left_ankle_angle = self.calculate_angle(
                    left_knee,
                    left_ankle,
                    left_foot
                )

                # -------------------------
                # 右足首角度
                # -------------------------

                right_ankle_angle = self.calculate_angle(
                    right_knee,
                    right_ankle,
                    right_foot
                )

                angle_history.append({
                    "frame": frame_index,
                    "left_knee": left_knee_angle,
                    "right_knee": right_knee_angle,
                    "left_hip": left_hip_angle,
                    "right_hip": right_hip_angle,
                    "left_ankle": left_ankle_angle,
                    "right_ankle": right_ankle_angle
                })

                # -------------------------
                # 骨格点
                # -------------------------

                for landmark in landmarks:

                    x = int(
                        landmark.x * width
                    )

                    y = int(
                        landmark.y * height
                    )

                    if (
                        0 <= x < width
                        and 0 <= y < height
                    ):

                        cv2.circle(
                            frame,
                            (x, y),
                            4,
                            (0, 255, 0),
                            -1
                        )

                # -------------------------
                # 骨格線
                # -------------------------

                connections = [
                    (11, 12),
                    (11, 13),
                    (13, 15),
                    (12, 14),
                    (14, 16),
                    (11, 23),
                    (12, 24),
                    (23, 24),
                    (23, 25),
                    (25, 27),
                    (24, 26),
                    (26, 28),
                    (27, 31),
                    (28, 32)
                ]

                for start, end in connections:

                    x1 = int(
                        landmarks[start].x * width
                    )

                    y1 = int(
                        landmarks[start].y * height
                    )

                    x2 = int(
                        landmarks[end].x * width
                    )

                    y2 = int(
                        landmarks[end].y * height
                    )

                    cv2.line(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                # -------------------------
                # 現在フレームの角度表示
                # -------------------------

                cv2.putText(
                    frame,
                    f"L Knee: {left_knee_angle:.1f}",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"R Knee: {right_knee_angle:.1f}",
                    (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"L Hip: {left_hip_angle:.1f}",
                    (20, 95),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"R Hip: {right_hip_angle:.1f}",
                    (20, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"L Ankle: {left_ankle_angle:.1f}",
                    (20, 155),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"R Ankle: {right_ankle_angle:.1f}",
                    (20, 185),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

            out.write(frame)

            frame_index += 1

        cap.release()
        out.release()

        self.landmarker.close()

        # -------------------------
        # 平均角度
        # -------------------------

        if angle_history:

            average_angles = {
                "left_knee": sum(
                    x["left_knee"]
                    for x in angle_history
                ) / len(angle_history),

                "right_knee": sum(
                    x["right_knee"]
                    for x in angle_history
                ) / len(angle_history),

                "left_hip": sum(
                    x["left_hip"]
                    for x in angle_history
                ) / len(angle_history),

                "right_hip": sum(
                    x["right_hip"]
                    for x in angle_history
                ) / len(angle_history),

                "left_ankle": sum(
                    x["left_ankle"]
                    for x in angle_history
                ) / len(angle_history),

                "right_ankle": sum(
                    x["right_ankle"]
                    for x in angle_history
                ) / len(angle_history)
            }

        else:

            average_angles = {
                "left_knee": 0,
                "right_knee": 0,
                "left_hip": 0,
                "right_hip": 0,
                "left_ankle": 0,
                "right_ankle": 0
            }

        return {
            "fps": fps,
            "width": width,
            "height": height,
            "frames": frames,
            "angles": average_angles,
            "angle_history": angle_history
        }
