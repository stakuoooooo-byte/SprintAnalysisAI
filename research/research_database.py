from pathlib import Path
import pandas as pd


RESEARCH_DIR = Path("research")

REFERENCE_PATH = (
    RESEARCH_DIR / "references.csv"
)


def load_references():

    if not REFERENCE_PATH.exists():

        raise FileNotFoundError(
            f"{REFERENCE_PATH} がありません。"
        )

    return pd.read_csv(
        REFERENCE_PATH
    )


def get_metric_references(metric):

    df = load_references()

    return df[
        df["metric"].str.lower()
        == metric.lower()
    ]


def get_phase_references(phase):

    df = load_references()

    return df[
        df["phase"].str.lower()
        == phase.lower()
    ]


def print_database():

    df = load_references()

    print("=" * 60)
    print("SprintAnalysisAI")
    print("研究データベース")
    print("=" * 60)

    print(
        f"\n登録論文・研究レコード: {len(df)}"
    )

    print("\n【指標】")

    for metric in sorted(
        df["metric"].unique()
    ):

        count = len(
            df[df["metric"] == metric]
        )

        print(
            f"- {metric}: {count}件"
        )

    print("\n【局面】")

    for phase in sorted(
        df["phase"].unique()
    ):

        count = len(
            df[df["phase"] == phase]
        )

        print(
            f"- {phase}: {count}件"
        )


if __name__ == "__main__":

    print_database()