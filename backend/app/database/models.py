from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ============================================================
# USERS
# ============================================================

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.department_id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# DEPARTMENTS
# ============================================================

class Department(Base):
    __tablename__ = "departments"

    department_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    department_code: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
    )
    department_name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )


# ============================================================
# CORRIDORS
# ============================================================

class Corridor(Base):
    __tablename__ = "corridors"

    corridor_id: Mapped[str] = mapped_column(
        String(10),
        primary_key=True,
    )
    from_station_id: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    to_station_id: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    length_km: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    track_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )


# ============================================================
# MAINTENANCE TASKS
# ============================================================

class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    task_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    asset_id: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.department_id"),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    defect_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    maintenance_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    severity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    criticality: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    overdue_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    estimated_duration_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    safety_risk: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    operational_impact: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    deadline: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    priority_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    priority_class: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# TRAIN SCHEDULES
# ============================================================

class TrainSchedule(Base):
    __tablename__ = "train_schedules"

    schedule_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    train_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    train_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    train_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    arrival_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    departure_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    movement_date: Mapped[datetime | None] = mapped_column(
        Date,
        nullable=True,
    )

    direction: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )


# ============================================================
# BLOCK REQUESTS
# ============================================================

class BlockRequest(Base):
    __tablename__ = "block_requests"

    request_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    task_id: Mapped[str] = mapped_column(
        ForeignKey("maintenance_tasks.task_id"),
        nullable=False,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.department_id"),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    requested_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
    )

    requested_start: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    requested_end: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    duration_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# OPTIMIZED SCHEDULES
# ============================================================

class OptimizedSchedule(Base):
    __tablename__ = "optimized_schedules"

    schedule_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    planning_start: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
    )

    planning_end: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Draft",
    )

    optimization_score: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )

    total_train_delay_minutes: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    total_downtime_hours: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    combined_block_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
    )


# ============================================================
# SCHEDULE TASKS
# ============================================================

class ScheduleTask(Base):
    __tablename__ = "schedule_tasks"

    schedule_task_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    schedule_id: Mapped[str] = mapped_column(
        ForeignKey("optimized_schedules.schedule_id"),
        nullable=False,
    )

    task_id: Mapped[str] = mapped_column(
        ForeignKey("maintenance_tasks.task_id"),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    scheduled_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
    )

    scheduled_start: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    scheduled_end: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Scheduled",
    )

    combined_block_id: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )


# ============================================================
# SAFETY VALIDATION RESULTS
# ============================================================

class SafetyValidationResult(Base):
    __tablename__ = "safety_validation_results"

    validation_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    schedule_id: Mapped[str] = mapped_column(
        ForeignKey("optimized_schedules.schedule_id"),
        nullable=False,
    )

    passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    train_conflicts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    buffer_violations: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    corridor_conflicts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    dependency_violations: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    violation_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    validation_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    validated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# APPROVALS
# ============================================================

class Approval(Base):
    __tablename__ = "approvals"

    approval_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    schedule_id: Mapped[str] = mapped_column(
        ForeignKey("optimized_schedules.schedule_id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# AUDIT LOGS
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
    )

    schedule_id: Mapped[str | None] = mapped_column(
        ForeignKey("optimized_schedules.schedule_id"),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    old_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    new_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )