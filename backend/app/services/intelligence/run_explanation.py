import pandas as pd

from app.services.intelligence.explanation_engine import (
    ExplanationEngine,
)


DATA_PATH = "data/railsync_department_requests_420.csv"


def main():

    df = pd.read_csv(DATA_PATH)

    tasks = df.to_dict(orient="records")

    explanations = ExplanationEngine.explain_tasks(
        tasks
    )

    print("\nTOTAL REQUESTS:", len(explanations))

    print("\nTOP 5 REQUEST EXPLANATIONS:")

    for explanation in explanations[:5]:

        print("\n" + "=" * 70)

        print(
            "REQUEST:",
            explanation["task_id"],
        )

        print(
            "PRIORITY:",
            explanation["priority_class"],
        )

        print(
            "SCORE:",
            explanation["priority_score"],
        )

        print(
            "\nSUMMARY:"
        )

        print(
            explanation["summary"]
        )

        print(
            "\nMAIN DRIVERS:"
        )

        for driver in explanation["drivers"]:

            print(
                f"- {driver['factor']}: "
                f"{driver['score']:.2f} "
                f"→ {driver['description']}"
            )


if __name__ == "__main__":
    main()