from sqlalchemy.orm import Session

from app.database.models import (
    Department,
    Station,
    Corridor,
    Subsection,
    WorkArea,
    Asset,
    MaintenanceRequest,
    TrainMovement,
    BlockOpportunity,
    WorkRequirement,
)

from app.services.ingestion.csv_loader import CSVLoader
from app.services.ingestion.cleaner import DataCleaner
from app.services.ingestion.normalizer import DataNormalizer
from app.services.ingestion.validator import DataValidator


class DatabaseLoader:
    """
    Loads the validated RailSync datasets into SQLite.

    Pipeline:

        CSV
          ↓
        Clean
          ↓
        Normalize
          ↓
        Validate
          ↓
        Database
    """

    def __init__(self, db: Session):
        self.db = db

    # ========================================================
    # PREPARE DATA
    # ========================================================

    @staticmethod
    def prepare_datasets() -> dict:

        raw = CSVLoader.load_all()

        cleaned = {
            name: DataCleaner.clean(df)
            for name, df in raw.items()
        }

        normalized = DataNormalizer.normalize_all(
            cleaned
        )

        DataValidator.validate_all(
            normalized
        )

        return normalized

    # ========================================================
    # DEPARTMENTS
    # ========================================================

    def load_departments(
        self,
        datasets: dict,
    ) -> dict[str, int]:

        department_codes = set()

        for dataset_name in [
            "assets",
            "department_requests",
            "work_requirements",
        ]:

            df = datasets[dataset_name]

            department_codes.update(
                str(value).strip().upper()
                for value in df["department"]
                if str(value).strip()
            )

        department_map = {}

        department_names = {
            "ENG": "Engineering",
            "SNT": "Signal & Telecommunications",
            "TRD": "Traction",
            "ELEC": "Electrical",
        }

        for code in sorted(department_codes):

            department = (
                self.db.query(Department)
                .filter(
                    Department.department_code == code
                )
                .first()
            )

            if department is None:

                department = Department(
                    department_code=code,
                    department_name=department_names.get(
                        code,
                        code,
                    ),
                )

                self.db.add(department)
                self.db.flush()

            department_map[code] = (
                department.department_id
            )

        return department_map

    # ========================================================
    # STATIONS
    # ========================================================

    def load_stations(
        self,
        df,
    ) -> int:

        inserted = 0

        for _, row in df.iterrows():

            station_id = str(
                row["station_id"]
            ).strip()

            if self.db.get(
                Station,
                station_id,
            ):
                continue

            station = Station(
                station_id=station_id,
                station_name=str(
                    row["station_name"]
                ).strip(),
                station_type=str(
                    row["station_type"]
                ).strip(),
                control_area=str(
                    row["control_area"]
                ).strip(),
                electrification=str(
                    row["electrification"]
                ).strip(),
                operational_status=str(
                    row["operational_status"]
                ).strip(),
            )

            self.db.add(station)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # CORRIDORS
    # ========================================================

    def load_corridors(
        self,
        df,
    ) -> int:

        inserted = 0
        seen = set()

        for _, row in df.iterrows():

            corridor_id = str(
                row["corridor_id"]
            ).strip()

            if corridor_id in seen:
                continue

            seen.add(corridor_id)

            if self.db.get(
                Corridor,
                corridor_id,
            ):
                continue

            corridor = Corridor(
                corridor_id=corridor_id,
                section_name=str(
                    row["section_name"]
                ).strip(),
                from_station_id=str(
                    row["from_station"]
                ).strip(),
                to_station_id=str(
                    row["to_station"]
                ).strip(),
                line_type=str(
                    row["line_type"]
                ).strip(),
                electrification=str(
                    row["electrification"]
                ).strip(),
                direction=str(
                    row["direction"]
                ).strip(),
            )

            self.db.add(corridor)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # SUBSECTIONS
    # ========================================================

    def load_subsections(
        self,
        df,
    ) -> int:

        inserted = 0
        seen = set()

        for _, row in df.iterrows():

            subsection_id = str(
                row["subsection_id"]
            ).strip()

            if subsection_id in seen:
                continue

            seen.add(subsection_id)

            if self.db.get(
                Subsection,
                subsection_id,
            ):
                continue

            subsection = Subsection(
                subsection_id=subsection_id,
                corridor_id=str(
                    row["corridor_id"]
                ).strip(),
                subsection_name=subsection_id,
                from_station_id=str(
                    row["from_station"]
                ).strip(),
                to_station_id=str(
                    row["to_station"]
                ).strip(),
            )

            self.db.add(subsection)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # WORK AREAS
    # ========================================================

    def load_work_areas(
        self,
        df,
    ) -> int:

        inserted = 0
        seen = set()

        for _, row in df.iterrows():

            work_area_id = str(
                row["work_area_id"]
            ).strip()

            if work_area_id in seen:
                continue

            seen.add(work_area_id)

            if self.db.get(
                WorkArea,
                work_area_id,
            ):
                continue

            work_area = WorkArea(
                work_area_id=work_area_id,
                subsection_id=str(
                    row["subsection_id"]
                ).strip(),
                work_area_name=work_area_id,
            )

            self.db.add(work_area)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # ASSETS
    # ========================================================

    def load_assets(
        self,
        df,
        department_map: dict[str, int],
    ) -> int:

        inserted = 0

        for _, row in df.iterrows():

            asset_id = str(
                row["asset_id"]
            ).strip()

            if self.db.get(
                Asset,
                asset_id,
            ):
                continue

            department_code = str(
                row["department"]
            ).strip().upper()

            department_id = department_map.get(
                department_code
            )

            if department_id is None:
                raise ValueError(
                    f"Unknown department: "
                    f"{department_code}"
                )

            asset = Asset(
                asset_id=asset_id,
                department_id=department_id,
                asset_type=str(
                    row["asset_type"]
                ).strip(),
                component_type=str(
                    row["component_type"]
                ).strip(),
                corridor_id=str(
                    row["corridor_id"]
                ).strip(),
                subsection_id=str(
                    row["subsection_id"]
                ).strip(),
                work_area_id=str(
                    row["work_area_id"]
                ).strip(),
                asset_status=str(
                    row["asset_status"]
                ).strip(),
                criticality_class=str(
                    row["criticality_class"]
                ).strip(),
                typical_issue=str(
                    row["typical_issue"]
                ).strip(),
            )

            self.db.add(asset)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # MAINTENANCE REQUESTS
    # ========================================================

    def load_maintenance_requests(
        self,
        df,
        department_map: dict[str, int],
    ) -> int:

        inserted = 0

        for _, row in df.iterrows():

            request_id = str(
                row["request_id"]
            ).strip()

            if self.db.get(
                MaintenanceRequest,
                request_id,
            ):
                continue

            department_code = str(
                row["department"]
            ).strip().upper()

            department_id = department_map.get(
                department_code
            )

            if department_id is None:
                raise ValueError(
                    f"Unknown department: "
                    f"{department_code}"
                )

            request = MaintenanceRequest(
                request_id=request_id,
                department_id=department_id,
                planning_type=str(
                    row["planning_type"]
                ).strip(),
                preferred_day=str(
                    row["preferred_day"]
                ).strip(),
                corridor_id=str(
                    row["corridor_id"]
                ).strip(),
                subsection_id=str(
                    row["subsection_id"]
                ).strip(),
                work_area_id=str(
                    row["work_area_id"]
                ).strip(),
                from_station_id=str(
                    row["from_station"]
                ).strip(),
                to_station_id=str(
                    row["to_station"]
                ).strip(),
                asset_id=str(
                    row["asset_id"]
                ).strip(),
                asset_type=str(
                    row["asset_type"]
                ).strip(),
                maintenance_type=str(
                    row["maintenance_type"]
                ).strip(),
                issue=str(
                    row["issue"]
                ).strip(),
                severity=float(
                    row["severity"]
                ),
                criticality=float(
                    row["criticality"]
                ),
                urgency=str(
                    row["urgency"]
                ).strip(),
                overdue_days=float(
                    row["overdue_days"]
                ),
                estimated_duration_hours=float(
                    row["estimated_duration_hours"]
                ),
                safety_risk=float(
                    row["safety_risk"]
                ),
                operational_impact=float(
                    row["operational_impact"]
                ),
                request_status=str(
                    row["request_status"]
                ).strip(),
                planning_cycle=str(
                    row["planning_cycle"]
                ).strip(),
                request_source=str(
                    row["request_source"]
                ).strip(),
                deadline_day=str(
                    row["deadline_day"]
                ).strip(),
                controller_status=str(
                    row["controller_status"]
                ).strip(),
                approval_required=bool(
                    row["approval_required"]
                ),
            )

            self.db.add(request)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # TRAIN MOVEMENTS
    # ========================================================

    def load_train_movements(
        self,
        df,
    ) -> int:

        inserted = 0

        for _, row in df.iterrows():

            movement_id = str(
                row["movement_id"]
            ).strip()

            if self.db.get(
                TrainMovement,
                movement_id,
            ):
                continue

            movement = TrainMovement(
                movement_id=movement_id,
                day=str(
                    row["day"]
                ).strip(),
                corridor_id=str(
                    row["corridor_id"]
                ).strip(),
                subsection_id=str(
                    row["subsection_id"]
                ).strip(),
                from_station_id=str(
                    row["from_station"]
                ).strip(),
                to_station_id=str(
                    row["to_station"]
                ).strip(),
                train_no=int(
                    row["train_no"]
                ),
                train_type=str(
                    row["train_type"]
                ).strip(),
                entry_time=row["entry_time"],
                exit_time=row["exit_time"],
                minimum_maintenance_buffer_minutes=int(
                    row[
                        "minimum_maintenance_buffer_minutes"
                    ]
                ),
                line_id=str(
                    row["line_id"]
                ).strip(),
                movement_status=str(
                    row["movement_status"]
                ).strip(),
                direction=str(
                    row["direction"]
                ).strip(),
                movement_source=str(
                    row["movement_source"]
                ).strip(),
            )

            self.db.add(movement)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # BLOCK OPPORTUNITIES
    # ========================================================

    def load_block_opportunities(
        self,
        df,
    ) -> int:

        inserted = 0

        for _, row in df.iterrows():

            block_id = str(
                row["block_id"]
            ).strip()

            if self.db.get(
                BlockOpportunity,
                block_id,
            ):
                continue

            block = BlockOpportunity(
                block_id=block_id,
                day=str(
                    row["day"]
                ).strip(),
                corridor_id=str(
                    row["corridor_id"]
                ).strip(),
                subsection_id=str(
                    row["subsection_id"]
                ).strip(),
                work_area_id=str(
                    row["work_area_id"]
                ).strip(),
                from_station_id=str(
                    row["from_station"]
                ).strip(),
                to_station_id=str(
                    row["to_station"]
                ).strip(),
                start_time=row["start_time"],
                end_time=row["end_time"],
                available=bool(
                    row["available"]
                ),
                block_type=str(
                    row["block_type"]
                ).strip(),
                availability_source=str(
                    row["availability_source"]
                ).strip(),
                derived_safe_window=bool(
                    row["derived_safe_window"]
                ),
                safety_buffer_minutes=int(
                    row["safety_buffer_minutes"]
                ),
            )

            self.db.add(block)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # WORK REQUIREMENTS
    # ========================================================

    def load_work_requirements(
        self,
        df,
        department_map: dict[str, int],
    ) -> int:

        inserted = 0

        for _, row in df.iterrows():

            department_code = str(
                row["department"]
            ).strip().upper()

            department_id = department_map.get(
                department_code
            )

            if department_id is None:
                raise ValueError(
                    f"Unknown department: "
                    f"{department_code}"
                )

            maintenance_type = str(
                row["maintenance_type"]
            ).strip()

            existing = (
                self.db.query(
                    WorkRequirement
                )
                .filter(
                    WorkRequirement.department_id
                    == department_id,
                    WorkRequirement.maintenance_type
                    == maintenance_type,
                )
                .first()
            )

            if existing:
                continue

            requirement = WorkRequirement(
                department_id=department_id,
                maintenance_type=maintenance_type,
                planning_class=str(
                    row["planning_class"]
                ).strip(),
                minimum_duration_hours=float(
                    row["minimum_duration_hours"]
                ),
                maximum_duration_hours=float(
                    row["maximum_duration_hours"]
                ),
                project_safety_buffer_minutes=int(
                    row[
                        "project_safety_buffer_minutes"
                    ]
                ),
                coordination_scope=str(
                    row["coordination_scope"]
                ).strip(),
                requires_controller_approval=bool(
                    row[
                        "requires_controller_approval"
                    ]
                ),
            )

            self.db.add(requirement)
            inserted += 1

        self.db.flush()

        return inserted

    # ========================================================
    # FULL LOAD
    # ========================================================

    def load_all(self) -> dict:

        datasets = self.prepare_datasets()

        department_map = self.load_departments(
            datasets
        )

        stations = self.load_stations(
            datasets["stations"]
        )

        corridors = self.load_corridors(
            datasets["topology"]
        )

        subsections = self.load_subsections(
            datasets["topology"]
        )

        work_areas = self.load_work_areas(
            datasets["topology"]
        )

        assets = self.load_assets(
            datasets["assets"],
            department_map,
        )

        requirements = self.load_work_requirements(
            datasets["work_requirements"],
            department_map,
        )

        requests = self.load_maintenance_requests(
            datasets["department_requests"],
            department_map,
        )

        movements = self.load_train_movements(
            datasets["train_movements"]
        )

        blocks = self.load_block_opportunities(
            datasets["block_availability"]
        )

        self.db.commit()

        return {
            "status": "success",
            "departments": len(
                department_map
            ),
            "stations": stations,
            "corridors": corridors,
            "subsections": subsections,
            "work_areas": work_areas,
            "assets": assets,
            "work_requirements": requirements,
            "maintenance_requests": requests,
            "train_movements": movements,
            "block_opportunities": blocks,
        }