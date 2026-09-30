import pandas as pd


class ContactDetector:

    def __init__(
        self,
        fps=30,
        velocity_threshold=0.20,
        min_interval_sec=0.16
    ):

        self.fps = fps

        # 足首の上下速度の閾値
        self.velocity_threshold = (
            velocity_threshold
        )

        # 同じ足の接地候補の最小間隔
        self.min_interval_sec = (
            min_interval_sec
        )


    # =====================================
    # 垂直速度
    # =====================================

    def calculate_vertical_velocity(
        self,
        df,
        column
    ):

        velocity = []

        for i in range(
            len(df)
        ):

            if i == 0:

                value = 0.0

            else:

                current = float(
                    df.loc[
                        i,
                        column
                    ]
                )

                previous = float(
                    df.loc[
                        i - 1,
                        column
                    ]
                )

                value = (
                    current - previous
                ) * self.fps

            velocity.append(
                value
            )

        return velocity


    # =====================================
    # 接地候補検出
    # =====================================

    def detect_contacts(
        self,
        df,
        ankle_y_column,
        ankle_x_column
    ):

        df = df.copy()

        # -----------------------------
        # 必要な列の確認
        # -----------------------------

        required_columns = [
            "frame",
            ankle_y_column,
            ankle_x_column
        ]

        for column in required_columns:

            if column not in df.columns:

                raise ValueError(
                    f"必要な列がありません: {column}"
                )


        # -----------------------------
        # 数値化
        # -----------------------------

        df["frame"] = pd.to_numeric(
            df["frame"],
            errors="coerce"
        )

        df[ankle_y_column] = pd.to_numeric(
            df[ankle_y_column],
            errors="coerce"
        )

        df[ankle_x_column] = pd.to_numeric(
            df[ankle_x_column],
            errors="coerce"
        )

        df = df.dropna(
            subset=[
                "frame",
                ankle_y_column,
                ankle_x_column
            ]
        ).reset_index(
            drop=True
        )


        # -----------------------------
        # 垂直速度
        # -----------------------------

        velocity_column = (
            ankle_y_column
            + "_velocity"
        )

        df[velocity_column] = (
            self.calculate_vertical_velocity(
                df,
                ankle_y_column
            )
        )


        # -----------------------------
        # 接地候補
        # -----------------------------

        candidates = []

        last_contact_time = -999.0


        for i in range(
            1,
            len(df) - 1
        ):

            previous_velocity = float(
                df.loc[
                    i - 1,
                    velocity_column
                ]
            )

            current_velocity = float(
                df.loc[
                    i,
                    velocity_column
                ]
            )

            next_velocity = float(
                df.loc[
                    i + 1,
                    velocity_column
                ]
            )


            # =================================
            # 条件①
            # 現在の速度が小さい
            # =================================

            if abs(
                current_velocity
            ) > self.velocity_threshold:

                continue


            # =================================
            # 条件②
            # 前後より速度が小さい
            # =================================

            if not (
                abs(current_velocity)
                <= abs(previous_velocity)
                and
                abs(current_velocity)
                <= abs(next_velocity)
            ):

                continue


            # =================================
            # 時間
            # =================================

            frame = int(
                df.loc[
                    i,
                    "frame"
                ]
            )

            time_sec = (
                frame / self.fps
            )


            # =================================
            # 条件③
            # 同じ足の近すぎる候補を除外
            # =================================

            if (
                time_sec
                - last_contact_time
                < self.min_interval_sec
            ):

                continue


            # =================================
            # 候補登録
            # =================================

            candidates.append({

                "frame":
                    frame,

                "time_sec":
                    time_sec,

                "ankle_x":
                    float(
                        df.loc[
                            i,
                            ankle_x_column
                        ]
                    ),

                "ankle_y":
                    float(
                        df.loc[
                            i,
                            ankle_y_column
                        ]
                    ),

                "vertical_velocity":
                    current_velocity
            })


            last_contact_time = (
                time_sec
            )


        return pd.DataFrame(
            candidates
        )


    # =====================================
    # 左右の接地分析
    # =====================================

    def analyze(
        self,
        df
    ):

        left_contacts = (
            self.detect_contacts(
                df,
                "left_ankle_y",
                "left_ankle_x"
            )
        )

        right_contacts = (
            self.detect_contacts(
                df,
                "right_ankle_y",
                "right_ankle_x"
            )
        )


        # =================================
        # 左右にsideを追加
        # =================================

        if not left_contacts.empty:

            left_contacts[
                "side"
            ] = "left"


        if not right_contacts.empty:

            right_contacts[
                "side"
            ] = "right"


        return {

            "left":
                left_contacts,

            "right":
                right_contacts
        }