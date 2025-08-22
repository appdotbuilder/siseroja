from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums for role-based access and status tracking
class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    STAFF = "staff"


class PermitStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class PermitType(str, Enum):
    SICK = "sick"  # Sakit
    FAMILY_MATTER = "family_matter"  # Urusan keluarga
    OTHER = "other"  # Lainnya


class GradeLevel(str, Enum):
    GRADE_7 = "7"
    GRADE_8 = "8"
    GRADE_9 = "9"


class Gender(str, Enum):
    MALE = "L"  # Laki-laki
    FEMALE = "P"  # Perempuan


# Core persistent models
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.STAFF)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    permits_created: List["StudentPermit"] = Relationship(back_populates="created_by_user")
    permits_updated: List["StudentPermit"] = Relationship(back_populates="updated_by_user")


class SchoolClass(SQLModel, table=True):
    __tablename__ = "school_classes"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, max_length=10)  # e.g., "7A", "8B", "9G"
    grade_level: GradeLevel
    homeroom_teacher: Optional[str] = Field(default=None, max_length=100)
    academic_year: str = Field(max_length=9)  # e.g., "2023/2024"
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    students: List["Student"] = Relationship(back_populates="school_class")


class Student(SQLModel, table=True):
    __tablename__ = "students"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    nis: str = Field(unique=True, max_length=20)  # Nomor Induk Siswa
    nisn: Optional[str] = Field(default=None, max_length=20)  # Nomor Induk Siswa Nasional
    name: str = Field(max_length=100)
    gender: Gender
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    class_id: int = Field(foreign_key="school_classes.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    school_class: SchoolClass = Relationship(back_populates="students")
    permits: List["StudentPermit"] = Relationship(back_populates="student")


class Employee(SQLModel, table=True):
    __tablename__ = "employees"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    nip: Optional[str] = Field(default=None, max_length=30, unique=True)  # Nomor Induk Pegawai
    name: str = Field(max_length=100)
    gender: Gender
    position: Optional[str] = Field(default=None, max_length=100)  # Jabatan
    subject: Optional[str] = Field(default=None, max_length=100)  # Mata pelajaran
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    hire_date: Optional[date] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Alumni(SQLModel, table=True):
    __tablename__ = "alumni"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    nis: str = Field(max_length=20)  # No longer unique as student might become alumni
    nisn: Optional[str] = Field(default=None, max_length=20)
    name: str = Field(max_length=100)
    gender: Gender
    graduation_year: int = Field(ge=2000, le=3000)
    last_class: str = Field(max_length=10)  # Class when graduated
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    current_activity: Optional[str] = Field(default=None, max_length=200)  # Current school/work
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StudentPermit(SQLModel, table=True):
    __tablename__ = "student_permits"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    permit_type: PermitType
    reason: str = Field(max_length=500)
    start_date: date
    end_date: date
    status: PermitStatus = Field(default=PermitStatus.PENDING)
    notes: Optional[str] = Field(default=None, max_length=1000)
    approval_notes: Optional[str] = Field(default=None, max_length=500)
    created_by: int = Field(foreign_key="users.id")
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = Field(default=None)

    # Relationships
    student: Student = Relationship(back_populates="permits")
    created_by_user: User = Relationship(
        back_populates="permits_created", sa_relationship_kwargs={"foreign_keys": "[StudentPermit.created_by]"}
    )
    updated_by_user: Optional[User] = Relationship(
        back_populates="permits_updated", sa_relationship_kwargs={"foreign_keys": "[StudentPermit.updated_by]"}
    )


class SystemSettings(SQLModel, table=True):
    __tablename__ = "system_settings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    school_name: str = Field(default="SMP NEGERI 2 JATIROGO", max_length=200)
    school_address: Optional[str] = Field(default=None, max_length=500)
    school_phone: Optional[str] = Field(default=None, max_length=20)
    school_email: Optional[str] = Field(default=None, max_length=255)
    current_academic_year: str = Field(default="2024/2025", max_length=9)
    app_version: str = Field(default="1.0.0", max_length=10)
    maintenance_mode: bool = Field(default=False)
    public_board_enabled: bool = Field(default=True)
    max_permit_days: int = Field(default=7, ge=1, le=30)
    auto_approve_sick_permits: bool = Field(default=False)
    notification_settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: str = Field(max_length=100)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    table_name: str = Field(max_length=50)
    record_id: Optional[int] = Field(default=None)
    old_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas for validation and API
class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=100)
    name: str = Field(max_length=100)
    role: UserRole = Field(default=UserRole.STAFF)


class UserUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    role: Optional[UserRole] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class StudentCreate(SQLModel, table=False):
    nis: str = Field(max_length=20)
    nisn: Optional[str] = Field(default=None, max_length=20)
    name: str = Field(max_length=100)
    gender: Gender
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    class_id: int


class StudentUpdate(SQLModel, table=False):
    nis: Optional[str] = Field(default=None, max_length=20)
    nisn: Optional[str] = Field(default=None, max_length=20)
    name: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[Gender] = Field(default=None)
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    class_id: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class PermitCreate(SQLModel, table=False):
    student_id: int
    permit_type: PermitType
    reason: str = Field(max_length=500)
    start_date: date
    end_date: date
    notes: Optional[str] = Field(default=None, max_length=1000)


class PermitUpdate(SQLModel, table=False):
    permit_type: Optional[PermitType] = Field(default=None)
    reason: Optional[str] = Field(default=None, max_length=500)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    status: Optional[PermitStatus] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=1000)
    approval_notes: Optional[str] = Field(default=None, max_length=500)


class SchoolClassCreate(SQLModel, table=False):
    name: str = Field(max_length=10)
    grade_level: GradeLevel
    homeroom_teacher: Optional[str] = Field(default=None, max_length=100)
    academic_year: str = Field(max_length=9)


class SchoolClassUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=10)
    homeroom_teacher: Optional[str] = Field(default=None, max_length=100)
    academic_year: Optional[str] = Field(default=None, max_length=9)
    is_active: Optional[bool] = Field(default=None)


class EmployeeCreate(SQLModel, table=False):
    nip: Optional[str] = Field(default=None, max_length=30)
    name: str = Field(max_length=100)
    gender: Gender
    position: Optional[str] = Field(default=None, max_length=100)
    subject: Optional[str] = Field(default=None, max_length=100)
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    hire_date: Optional[date] = Field(default=None)


class EmployeeUpdate(SQLModel, table=False):
    nip: Optional[str] = Field(default=None, max_length=30)
    name: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[Gender] = Field(default=None)
    position: Optional[str] = Field(default=None, max_length=100)
    subject: Optional[str] = Field(default=None, max_length=100)
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    hire_date: Optional[date] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class AlumniCreate(SQLModel, table=False):
    nis: str = Field(max_length=20)
    nisn: Optional[str] = Field(default=None, max_length=20)
    name: str = Field(max_length=100)
    gender: Gender
    graduation_year: int = Field(ge=2000, le=3000)
    last_class: str = Field(max_length=10)
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    current_activity: Optional[str] = Field(default=None, max_length=200)


class AlumniUpdate(SQLModel, table=False):
    nis: Optional[str] = Field(default=None, max_length=20)
    nisn: Optional[str] = Field(default=None, max_length=20)
    name: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[Gender] = Field(default=None)
    graduation_year: Optional[int] = Field(default=None, ge=2000, le=3000)
    last_class: Optional[str] = Field(default=None, max_length=10)
    birth_place: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=20)
    parent_name: Optional[str] = Field(default=None, max_length=100)
    parent_phone: Optional[str] = Field(default=None, max_length=20)
    current_activity: Optional[str] = Field(default=None, max_length=200)


class SystemSettingsUpdate(SQLModel, table=False):
    school_name: Optional[str] = Field(default=None, max_length=200)
    school_address: Optional[str] = Field(default=None, max_length=500)
    school_phone: Optional[str] = Field(default=None, max_length=20)
    school_email: Optional[str] = Field(default=None, max_length=255)
    current_academic_year: Optional[str] = Field(default=None, max_length=9)
    maintenance_mode: Optional[bool] = Field(default=None)
    public_board_enabled: Optional[bool] = Field(default=None)
    max_permit_days: Optional[int] = Field(default=None, ge=1, le=30)
    auto_approve_sick_permits: Optional[bool] = Field(default=None)
    notification_settings: Optional[Dict[str, Any]] = Field(default=None)


# Dashboard statistics schemas
class DashboardStats(SQLModel, table=False):
    total_students: int
    total_active_students: int
    total_classes: int
    total_employees: int
    total_alumni: int
    permits_today: int
    pending_permits: int
    approved_permits_today: int
    total_permits_this_month: int


class PermitStats(SQLModel, table=False):
    total_permits: int
    pending_permits: int
    approved_permits: int
    rejected_permits: int
    permits_by_type: Dict[str, int]
    permits_by_month: Dict[str, int]


# Public board schema
class PublicPermitInfo(SQLModel, table=False):
    student_name: str
    class_name: str
    permit_type: str
    reason: str
    start_date: str
    end_date: str
