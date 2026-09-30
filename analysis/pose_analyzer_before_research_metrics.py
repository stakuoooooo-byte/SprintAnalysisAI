import cv2
import mediapipe as mp
import math
import csv
import os


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


    # =====================================
    # 3点から関節角度を計算
    # =====================================

    def calculate_angle(self, a, b, c):

        ba = (
            a[0] - b[0],
            a[1] - b[1]
        )

        bc = (
            c[0] - b[0],
            c[1] - b[1]
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

        if (
            magnitude_ba == 0
            or magnitude_bc == 0
        ):
            return 0

        cosine_angle = (
            dot_product
            / (magnitude_ba * magnitude_bc)
        )

        cosine_angle = max(
            -1,
            min(1, cosine_angle)
        )

        angle = math.degrees(
            math.acos(cosine_angle)
        )

        return angle


    # =====================================
    # 動画分析
    # =====================================

    def analyze_video(
        self,
        input_path,
        output_path
    ):

        cap = cv2.VideoCapture(
            input_path
        )

        if not cap.isOpened():

            raise ValueError(
                "動画を開けませんでした。"
            )

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        if fps <= 0:
            fps = 30

        width = int(
            cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        height = int(
            cap.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

        frames = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
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


        # =====================================
        # 動画フレーム処理
        # =====================================

        while True:

            ret, frame = cap.read()

            if not ret:
                break


            # ---------------------------------
            # RGB変換
            # ---------------------------------

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


            # ---------------------------------
            # MediaPipe Pose
            # ---------------------------------

            result = (
                self.landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms
                )
            )


            if result.pose_landmarks:

                landmarks = (
                    result.pose_landmarks[0]
                )


                # =================================
                # 必要な骨格点
                # =================================

                left_shoulder = (
                    landmarks[11].x,
                    landmarks[11].y
                )

                right_shoulder = (
                    landmarks[12].x,
                    landmarks[12].y
                )

                left_elbow = (
                    landmarks[13].x,
                    landmarks[13].y
                )

                right_elbow = (
                    landmarks[14].x,
                    landmarks[14].y
                )

                left_wrist = (
                    landmarks[15].x,
                    landmarks[15].y
                )

                right_wrist = (
                    landmarks[16].x,
                    landmarks[16].y
                )

                left_hip = (
                    landmarks[23].x,
                    landmarks[23].y
                )

                right_hip = (
                    landmarks[24].x,
                    landmarks[24].y
                )

                left_knee = (
                    landmarks[25].x,
                    landmarks[25].y
                )

                right_knee = (
                    landmarks[26].x,
                    landmarks[26].y
                )

                left_ankle = (
                    landmarks[27].x,
                    landmarks[27].y
                )

                right_ankle = (
                    landmarks[28].x,
                    landmarks[28].y
                )

                left_foot = (
                    landmarks[31].x,
                    landmarks[31].y
                )

                right_foot = (
                    landmarks[32].x,
                    landmarks[32].y
                )


                # =================================
                # 関節角度
                # =================================

                left_knee_angle = (
                    self.calculate_angle(
                        left_hip,
                        left_knee,
                        left_ankle
                    )
                )

                right_knee_angle = (
                    self.calculate_angle(
                        right_hip,
                        right_knee,
                        right_ankle
                    )
                )


                left_hip_angle = (
                    self.calculate_angle(
                        left_shoulder,
                        left_hip,
                        left_knee
                    )
                )

                right_hip_angle = (
                    self.calculate_angle(
                        right_shoulder,
                        right_hip,
                        right_knee
                    )
                )


                left_ankle_angle = (
                    self.calculate_angle(
                        left_knee,
                        left_ankle,
                        left_foot
                    )
                )

                right_ankle_angle = (
                    self.calculate_angle(
                        right_knee,
                        right_ankle,
                        right_foot
                    )
                )


                # =================================
                # CSV用データ
                # =================================

                angle_history.append({

                    "frame": frame_index,

                    "left_knee":
                        left_knee_angle,

                    "right_knee":
                        right_knee_angle,

                    "left_hip":
                        left_hip_angle,

                    "right_hip":
                        right_hip_angle,

                    "left_ankle":
                        left_ankle_angle,

                    "right_ankle":
                        right_ankle_angle,

                    # 左足首座標
                    "left_ankle_x":
                        left_ankle[0],

                    "left_ankle_y":
                        left_ankle[1],

                    # 右足首座標
                    "right_ankle_x":
                        right_ankle[0],

                    "right_ankle_y":
                        right_ankle[1]
                })


                # =================================
                # 骨格描画
                # =================================

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


                # =================================
                # 骨格線
                # =================================

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

                    if (
                        start < len(landmarks)
                        and end < len(landmarks)
                    ):

                        x1 = int(
                            landmarks[start].x
                            * width
                        )

                        y1 = int(
                            landmarks[start].y
                            * height
                        )

                        x2 = int(
                            landmarks[end].x
                            * width
                        )

                        y2 = int(
                            landmarks[end].y
                            * height
                        )

                        cv2.line(
                            frame,
                            (x1, y1),
                            (x2, y2),
                            (0, 255, 0),
                            2
                        )


            # =================================
            # フレーム保存
            # =================================

            out.write(frame)

            frame_index += 1


        # =====================================
        # 後処理
        # =====================================

        cap.release()

        out.release()


        # =====================================
        # 平均角度
        # =====================================

        if angle_history:

            average_angles = {

                "left_knee":
                    sum(
                        x["left_knee"]
                        for x in angle_history
                    ) / len(angle_history),

                "right_knee":
                    sum(
                        x["right_knee"]
                        for x in angle_history
                    ) / len(angle_history),

                "left_hip":
                    sum(
                        x["left_hip"]
                        for x in angle_history
                    ) / len(angle_history),

                "right_hip":
                    sum(
                        x["right_hip"]
                        for x in angle_history
                    ) / len(angle_history),

                "left_ankle":
                    sum(
                        x["left_ankle"]
                        for x in angle_history
                    ) / len(angle_history),

                "right_ankle":
                    sum(
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


        # =====================================
        # CSV保存
        # =====================================

        os.makedirs(
            "data",
            exist_ok=True
        )

        csv_path = os.path.join(
            "data",
            "angle_history.csv"
        )


        if angle_history:

            with open(
                csv_path,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as f:

                writer = csv.DictWriter(
                    f,
                    fieldnames=angle_history[0].keys()
                )

                writer.writeheader()

                writer.writerows(
                    angle_history
                )


        # =====================================
        # 結果
        # =====================================

        return {

            "fps": fps,

            "width": width,

            "height": height,

            "frames": frames,

            "angles": average_angles,

            "angle_history":
                angle_history
        }