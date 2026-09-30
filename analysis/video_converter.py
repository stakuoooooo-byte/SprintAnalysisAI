import os
import imageio_ffmpeg
import subprocess


def convert_to_browser_mp4(
    input_path,
    output_path
):

    ffmpeg_path = (
        imageio_ffmpeg.get_ffmpeg_exe()
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        input_path,

        "-c:v",
        "libx264",

        "-preset",
        "fast",

        "-crf",
        "23",

        "-pix_fmt",
        "yuv420p",

        "-movflags",
        "+faststart",

        "-an",

        output_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "動画変換に失敗しました。\n"
            + result.stderr
        )

    if not os.path.exists(
        output_path
    ):

        raise RuntimeError(
            "変換後の動画が生成されませんでした。"
        )

    return output_path