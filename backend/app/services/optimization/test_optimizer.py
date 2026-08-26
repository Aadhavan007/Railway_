import pandas as pd

from app.services.intelligence.priority_engine import PriorityEngine
from app.services.scheduling.block_matcher import BlockMatcher
from app.services.optimization.optimizer import BlockOptimizer


def main():

    df = pd.read_csv(
        "data/maintenance_tasks.csv"
    )

    # Small test set first.
    df = df.head(10)

    tasks = df.to_dict(
        orient="records"
    )

    # Calculate our priority scores.
    tasks = [
        PriorityEngine.prioritize_task(task)
        for task in tasks
    ]

    # Generate ranked candidates.
    matcher = BlockMatcher()

    ranked_candidates = {
        str(task["task_id"]):
        matcher.rank_candidates(task)
        for task in tasks
    }

    # Optimize.
    optimizer = BlockOptimizer()

    result = optimizer.optimize(
        tasks,
        ranked_candidates,
    )

    print("\nOPTIMIZER STATUS:")
    print(result.status)

    print("\nTOTAL TASKS:")
    print(result.total_tasks)

    print("\nSELECTED:")
    print(result.total_selected)

    print("\nOBJECTIVE:")
    print(result.objective_value)

    print("\nSCHEDULE:")
    for task in result.selected_tasks:
        print(task)


if __name__ == "__main__":
    main()