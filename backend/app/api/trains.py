"""
NEW FILE: backend/app/api/trains.py

Exposes the real train_movements dataset (railsync_train_movements_7day.csv)
via a GET endpoint, matching the exact pattern already used by
tasks.py/schedules.py -- this data is already loadable via CSVLoader,
it's just never been wired to a route.

After adding this file:
1. In backend/app/main.py, add:
     from app.api import trains
   and:
     app.include_router(trains.router)
   (alongside the other app.include_router(...) calls)
2. Redeploy.
"""

from fastapi import APIRouter, HTTPException

from app.services.ingestion.csv_loader import CSVLoader

router = APIRouter(
    prefix="/api/trains",
    tags=["Trains"],
)


@router.get("/")
def get_trains(
    day: str | None = None,
    corridor_id: str | None = None,
    train_no: str | None = None,
):
    try:
        df = CSVLoader.load(
            CSVLoader.DATA_DIR / CSVLoader.DATASETS["train_movements"]
        )

        if day:
            df = df[df["day"].str.lower() == day.lower()]

        if corridor_id:
            df = df[df["corridor_id"] == corridor_id]

        if train_no:
            df = df[df["train_no"].astype(str) == str(train_no)]

        records = df.to_dict(orient="records")

        return {
            "count": len(records),
            "trains": records,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
