from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    User,
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
    OptimizedSchedule,
    ScheduleTask,
    SafetyValidationResult,
    Approval,
    AuditLog,
)


# ============================================================
# DEPARTMENTS
# ============================================================

def create_department(
    db: Session,
    department_code: str,
    department_name: str,
) -> Department:

    department = Department(
        department_code=department_code,
        department_name=department_name,
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


def get_department(
    db: Session,
    department_id: int,
) -> Department | None:

    return db.get(
        Department,
        department_id,
    )


def get_department_by_code(
    db: Session,
    department_code: str,
) -> Department | None:

    statement = select(Department).where(
        Department.department_code == department_code
    )

    return db.scalar(statement)


def get_departments(
    db: Session,
) -> list[Department]:

    return list(
        db.scalars(
            select(Department)
        ).all()
    )


# ============================================================
# USERS
# ============================================================

def create_user(
    db: Session,
    name: str,
    role: str,
    department_id: int | None = None,
) -> User:

    user = User(
        name=name,
        role=role,
        department_id=department_id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(
    db: Session,
    user_id: int,
) -> User | None:

    return db.get(
        User,
        user_id,
    )


def get_users(
    db: Session,
) -> list[User]:

    return list(
        db.scalars(
            select(User)
        ).all()
    )


# ============================================================
# STATIONS
# ============================================================

def create_station(
    db: Session,
    **data,
) -> Station:

    station = Station(**data)

    db.add(station)
    db.commit()
    db.refresh(station)

    return station


def get_station(
    db: Session,
    station_id: str,
) -> Station | None:

    return db.get(
        Station,
        station_id,
    )


def get_stations(
    db: Session,
) -> list[Station]:

    return list(
        db.scalars(
            select(Station)
        ).all()
    )


# ============================================================
# CORRIDORS
# ============================================================

def create_corridor(
    db: Session,
    **data,
) -> Corridor:

    corridor = Corridor(**data)

    db.add(corridor)
    db.commit()
    db.refresh(corridor)

    return corridor


def get_corridor(
    db: Session,
    corridor_id: str,
) -> Corridor | None:

    return db.get(
        Corridor,
        corridor_id,
    )


def get_corridors(
    db: Session,
) -> list[Corridor]:

    return list(
        db.scalars(
            select(Corridor)
        ).all()
    )


# ============================================================
# SUBSECTIONS
# ============================================================

def create_subsection(
    db: Session,
    **data,
) -> Subsection:

    subsection = Subsection(**data)

    db.add(subsection)
    db.commit()
    db.refresh(subsection)

    return subsection


def get_subsection(
    db: Session,
    subsection_id: str,
) -> Subsection | None:

    return db.get(
        Subsection,
        subsection_id,
    )


def get_subsections(
    db: Session,
    corridor_id: str | None = None,
) -> list[Subsection]:

    statement = select(Subsection)

    if corridor_id is not None:
        statement = statement.where(
            Subsection.corridor_id == corridor_id
        )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# WORK AREAS
# ============================================================

def create_work_area(
    db: Session,
    **data,
) -> WorkArea:

    work_area = WorkArea(**data)

    db.add(work_area)
    db.commit()
    db.refresh(work_area)

    return work_area


def get_work_area(
    db: Session,
    work_area_id: str,
) -> WorkArea | None:

    return db.get(
        WorkArea,
        work_area_id,
    )


def get_work_areas(
    db: Session,
    subsection_id: str | None = None,
) -> list[WorkArea]:

    statement = select(WorkArea)

    if subsection_id is not None:
        statement = statement.where(
            WorkArea.subsection_id == subsection_id
        )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# ASSETS
# ============================================================

def create_asset(
    db: Session,
    **data,
) -> Asset:

    asset = Asset(**data)

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


def get_asset(
    db: Session,
    asset_id: str,
) -> Asset | None:

    return db.get(
        Asset,
        asset_id,
    )


def get_assets(
    db: Session,
    department_id: int | None = None,
    subsection_id: str | None = None,
) -> list[Asset]:

    statement = select(Asset)

    if department_id is not None:
        statement = statement.where(
            Asset.department_id == department_id
        )

    if subsection_id is not None:
        statement = statement.where(
            Asset.subsection_id == subsection_id
        )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# MAINTENANCE REQUESTS
# ============================================================

def create_maintenance_request(
    db: Session,
    **data,
) -> MaintenanceRequest:

    request = MaintenanceRequest(**data)

    db.add(request)
    db.commit()
    db.refresh(request)

    return request


def get_maintenance_request(
    db: Session,
    request_id: str,
) -> MaintenanceRequest | None:

    return db.get(
        MaintenanceRequest,
        request_id,
    )


def get_maintenance_requests(
    db: Session,
    department_id: int | None = None,
    status: str | None = None,
    planning_type: str | None = None,
    controller_status: str | None = None,
) -> list[MaintenanceRequest]:

    statement = select(MaintenanceRequest)

    if department_id is not None:
        statement = statement.where(
            MaintenanceRequest.department_id == department_id
        )

    if status is not None:
        statement = statement.where(
            MaintenanceRequest.request_status == status
        )

    if planning_type is not None:
        statement = statement.where(
            MaintenanceRequest.planning_type == planning_type
        )

    if controller_status is not None:
        statement = statement.where(
            MaintenanceRequest.controller_status
            == controller_status
        )

    return list(
        db.scalars(statement).all()
    )


def update_maintenance_request(
    db: Session,
    request_id: str,
    **updates,
) -> MaintenanceRequest | None:

    request = get_maintenance_request(
        db,
        request_id,
    )

    if request is None:
        return None

    for field, value in updates.items():

        if hasattr(request, field):
            setattr(
                request,
                field,
                value,
            )

    db.commit()
    db.refresh(request)

    return request


def delete_maintenance_request(
    db: Session,
    request_id: str,
) -> bool:

    request = get_maintenance_request(
        db,
        request_id,
    )

    if request is None:
        return False

    db.delete(request)
    db.commit()

    return True


# ============================================================
# TRAIN MOVEMENTS
# ============================================================

def create_train_movement(
    db: Session,
    **data,
) -> TrainMovement:

    movement = TrainMovement(**data)

    db.add(movement)
    db.commit()
    db.refresh(movement)

    return movement


def get_train_movement(
    db: Session,
    movement_id: str,
) -> TrainMovement | None:

    return db.get(
        TrainMovement,
        movement_id,
    )


def get_train_movements(
    db: Session,
    day: str | None = None,
    corridor_id: str | None = None,
    subsection_id: str | None = None,
) -> list[TrainMovement]:

    statement = select(TrainMovement)

    if day is not None:
        statement = statement.where(
            TrainMovement.day == day
        )

    if corridor_id is not None:
        statement = statement.where(
            TrainMovement.corridor_id == corridor_id
        )

    if subsection_id is not None:
        statement = statement.where(
            TrainMovement.subsection_id == subsection_id
        )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# BLOCK OPPORTUNITIES
# ============================================================

def create_block_opportunity(
    db: Session,
    **data,
) -> BlockOpportunity:

    block = BlockOpportunity(**data)

    db.add(block)
    db.commit()
    db.refresh(block)

    return block


def get_block_opportunity(
    db: Session,
    block_id: str,
) -> BlockOpportunity | None:

    return db.get(
        BlockOpportunity,
        block_id,
    )


def get_block_opportunities(
    db: Session,
    day: str | None = None,
    corridor_id: str | None = None,
    subsection_id: str | None = None,
    available_only: bool = False,
) -> list[BlockOpportunity]:

    statement = select(BlockOpportunity)

    if day is not None:
        statement = statement.where(
            BlockOpportunity.day == day
        )

    if corridor_id is not None:
        statement = statement.where(
            BlockOpportunity.corridor_id
            == corridor_id
        )

    if subsection_id is not None:
        statement = statement.where(
            BlockOpportunity.subsection_id
            == subsection_id
        )

    if available_only:
        statement = statement.where(
            BlockOpportunity.available.is_(True)
        )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# WORK REQUIREMENTS
# ============================================================

def create_work_requirement(
    db: Session,
    **data,
) -> WorkRequirement:

    requirement = WorkRequirement(**data)

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    return requirement


def get_work_requirement(
    db: Session,
    requirement_id: int,
) -> WorkRequirement | None:

    return db.get(
        WorkRequirement,
        requirement_id,
    )


def get_work_requirements(
    db: Session,
    department_id: int | None = None,
    maintenance_type: str | None = None,
) -> list[WorkRequirement]:

    statement = select(WorkRequirement)

    if department_id is not None:
        statement = statement.where(
            WorkRequirement.department_id
            == department_id
        )

    if maintenance_type is not None:
        statement = statement.where(
            WorkRequirement.maintenance_type
            == maintenance_type
        )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# OPTIMIZED SCHEDULES
# ============================================================

def create_optimized_schedule(
    db: Session,
    **data,
) -> OptimizedSchedule:

    schedule = OptimizedSchedule(**data)

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


def get_optimized_schedule(
    db: Session,
    schedule_id: str,
) -> OptimizedSchedule | None:

    return db.get(
        OptimizedSchedule,
        schedule_id,
    )


def get_optimized_schedules(
    db: Session,
    status: str | None = None,
) -> list[OptimizedSchedule]:

    statement = select(OptimizedSchedule)

    if status is not None:
        statement = statement.where(
            OptimizedSchedule.status == status
        )

    return list(
        db.scalars(statement).all()
    )


def update_schedule_status(
    db: Session,
    schedule_id: str,
    status: str,
) -> OptimizedSchedule | None:

    schedule = get_optimized_schedule(
        db,
        schedule_id,
    )

    if schedule is None:
        return None

    schedule.status = status

    db.commit()
    db.refresh(schedule)

    return schedule


# ============================================================
# SCHEDULE TASKS
# ============================================================

def create_schedule_task(
    db: Session,
    **data,
) -> ScheduleTask:

    schedule_task = ScheduleTask(**data)

    db.add(schedule_task)
    db.commit()
    db.refresh(schedule_task)

    return schedule_task


def get_schedule_task(
    db: Session,
    schedule_task_id: int,
) -> ScheduleTask | None:

    return db.get(
        ScheduleTask,
        schedule_task_id,
    )


def get_schedule_tasks(
    db: Session,
    schedule_id: str | None = None,
    request_id: str | None = None,
) -> list[ScheduleTask]:

    statement = select(ScheduleTask)

    if schedule_id is not None:
        statement = statement.where(
            ScheduleTask.schedule_id
            == schedule_id
        )

    if request_id is not None:
        statement = statement.where(
            ScheduleTask.request_id
            == request_id
        )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# SAFETY VALIDATION
# ============================================================

def create_safety_validation(
    db: Session,
    **data,
) -> SafetyValidationResult:

    validation = SafetyValidationResult(**data)

    db.add(validation)
    db.commit()
    db.refresh(validation)

    return validation


def get_safety_validation(
    db: Session,
    validation_id: int,
) -> SafetyValidationResult | None:

    return db.get(
        SafetyValidationResult,
        validation_id,
    )


def get_schedule_safety_results(
    db: Session,
    schedule_id: str,
) -> list[SafetyValidationResult]:

    statement = select(
        SafetyValidationResult
    ).where(
        SafetyValidationResult.schedule_id
        == schedule_id
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# APPROVALS
# ============================================================

def create_approval(
    db: Session,
    **data,
) -> Approval:

    approval = Approval(**data)

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return approval


def get_approval(
    db: Session,
    approval_id: int,
) -> Approval | None:

    return db.get(
        Approval,
        approval_id,
    )


def get_schedule_approvals(
    db: Session,
    schedule_id: str,
) -> list[Approval]:

    statement = select(Approval).where(
        Approval.schedule_id == schedule_id
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# AUDIT LOG
# ============================================================

def create_audit_log(
    db: Session,
    **data,
) -> AuditLog:

    audit = AuditLog(**data)

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


def get_schedule_audit_logs(
    db: Session,
    schedule_id: str,
) -> list[AuditLog]:

    statement = select(AuditLog).where(
        AuditLog.schedule_id == schedule_id
    )

    return list(
        db.scalars(statement).all()
    )
