from datetime import datetime, date, time

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
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ============================================================
# BASE
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# USERS
# ============================================================

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

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
        String(20),
        unique=True,
        nullable=False,
    )

    department_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )


# ============================================================
# STATIONS
# ============================================================

class Station(Base):
    __tablename__ = "stations"

    station_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    station_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    station_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    control_area: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    electrification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    operational_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ACTIVE",
    )


# ============================================================
# CORRIDORS / SECTIONS
# ============================================================

class Corridor(Base):
    __tablename__ = "corridors"

    corridor_id: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
    )

    section_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    from_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    to_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    line_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    electrification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    direction: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )


# ============================================================
# SUBSECTIONS
# ============================================================

class Subsection(Base):
    __tablename__ = "subsections"

    subsection_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    subsection_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    from_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    to_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )


# ============================================================
# WORK AREAS
# ============================================================

class WorkArea(Base):
    __tablename__ = "work_areas"

    work_area_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    subsection_id: Mapped[str] = mapped_column(
        ForeignKey("subsections.subsection_id"),
        nullable=False,
    )

    work_area_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


# ============================================================
# ASSET MASTER
# ============================================================

class Asset(Base):
    __tablename__ = "assets"

    asset_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.department_id"),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    component_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    subsection_id: Mapped[str] = mapped_column(
        ForeignKey("subsections.subsection_id"),
        nullable=False,
    )

    work_area_id: Mapped[str] = mapped_column(
        ForeignKey("work_areas.work_area_id"),
        nullable=False,
    )

    asset_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    criticality_class: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    typical_issue: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


# ============================================================
# MAINTENANCE REQUESTS
# ============================================================

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    request_id: Mapped[str] = mapped_column(
        String(30),
        primary_key=True,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.department_id"),
        nullable=False,
    )

    planning_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    preferred_day: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    subsection_id: Mapped[str] = mapped_column(
        ForeignKey("subsections.subsection_id"),
        nullable=False,
    )

    work_area_id: Mapped[str] = mapped_column(
        ForeignKey("work_areas.work_area_id"),
        nullable=False,
    )

    from_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    to_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    asset_id: Mapped[str] = mapped_column(
        ForeignKey("assets.asset_id"),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    maintenance_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    issue: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    severity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    criticality: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    urgency: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    overdue_days: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    estimated_duration_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    safety_risk: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    operational_impact: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    request_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    planning_cycle: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    request_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    deadline_day: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    controller_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING_REVIEW",
    )

    approval_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    priority_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    priority_class: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# TRAIN MOVEMENTS
# ============================================================

class TrainMovement(Base):
    __tablename__ = "train_movements"

    movement_id: Mapped[str] = mapped_column(
        String(40),
        primary_key=True,
    )

    day: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    subsection_id: Mapped[str] = mapped_column(
        ForeignKey("subsections.subsection_id"),
        nullable=False,
    )

    from_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    to_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    train_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    train_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    entry_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    exit_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    minimum_maintenance_buffer_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )

    line_id: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    movement_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    direction: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    movement_source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


# ============================================================
# BLOCK OPPORTUNITIES
# ============================================================

class BlockOpportunity(Base):
    __tablename__ = "block_opportunities"

    block_id: Mapped[str] = mapped_column(
        String(40),
        primary_key=True,
    )

    day: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    subsection_id: Mapped[str] = mapped_column(
        ForeignKey("subsections.subsection_id"),
        nullable=False,
    )

    work_area_id: Mapped[str] = mapped_column(
        ForeignKey("work_areas.work_area_id"),
        nullable=False,
    )

    from_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    to_station_id: Mapped[str] = mapped_column(
        ForeignKey("stations.station_id"),
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    block_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    availability_source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    derived_safe_window: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    safety_buffer_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )


# ============================================================
# WORK REQUIREMENTS
# ============================================================

class WorkRequirement(Base):
    __tablename__ = "work_requirements"

    requirement_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.department_id"),
        nullable=False,
    )

    maintenance_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    planning_class: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    minimum_duration_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    maximum_duration_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    project_safety_buffer_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )

    coordination_scope: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    requires_controller_approval: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "department_id",
            "maintenance_type",
            name="uq_work_requirement_department_type",
        ),
    )


# ============================================================
# OPTIMIZED SCHEDULES
# ============================================================

class OptimizedSchedule(Base):
    __tablename__ = "optimized_schedules"

    schedule_id: Mapped[str] = mapped_column(
        String(40),
        primary_key=True,
    )

    planning_start_day: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    planning_end_day: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="DRAFT",
    )

    optimization_score: Mapped[float | None] = mapped_column(
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

    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
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

    request_id: Mapped[str] = mapped_column(
        ForeignKey("maintenance_requests.request_id"),
        nullable=False,
    )

    block_id: Mapped[str] = mapped_column(
        ForeignKey("block_opportunities.block_id"),
        nullable=False,
    )

    corridor_id: Mapped[str] = mapped_column(
        ForeignKey("corridors.corridor_id"),
        nullable=False,
    )

    subsection_id: Mapped[str] = mapped_column(
        ForeignKey("subsections.subsection_id"),
        nullable=False,
    )

    work_area_id: Mapped[str] = mapped_column(
        ForeignKey("work_areas.work_area_id"),
        nullable=False,
    )

    scheduled_day: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    scheduled_start: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    scheduled_end: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="SCHEDULED",
    )

    combined_block_id: Mapped[str | None] = mapped_column(
        String(40),
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