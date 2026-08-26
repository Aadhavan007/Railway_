import pandas as pd

from app.services.intelligence.priority_engine import PriorityEngine


DATA_PATH = "data/railsync_department_requests_420.csv"


def main():
    df = pd.read_csv(DATA_PATH)

    tasks = df.to_dict(orient="records")

    prioritized = PriorityEngine.prioritize_tasks(tasks)

    result = pd.DataFrame(prioritized)

    print("\nTOTAL REQUESTS:", len(result))

    print("\nPRIORITY DISTRIBUTION:")
    print(result["priority_class"].value_counts())

    print("\nTOP 10 PRIORITY REQUESTS:")
    print(
        result[
            [
                "request_id",
                "department",
                "asset_type",
                "severity",
                "criticality",
                "safety_risk",
                "operational_impact",
                "priority_score",
                "priority_class",
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()