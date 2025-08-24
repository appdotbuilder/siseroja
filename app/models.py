from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class AbsenceRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STAFF = "staff"


# Persistent models (stored in database)
class Student(SQLModel, table=True):
    """Student information model."""

    __tablename__ = "students"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: str = Field(unique=True, max_length=20, description="Unique student identifier")
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    grade: str = Field(max_length=10, description="Grade level (e.g., '10A', '11B')")
    class_name: str = Field(max_length=50, description="Class name")
    guardian_name: Optional[str] = Field(default=None, max_length=200)
    guardian_phone: Optional[str] = Field(default=None, max_length=20)
    is_active: bool = Field(default=True, description="Whether student is currently enrolled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    attendance_records: List["AttendanceRecord"] = Relationship(back_populates="student")
    absence_requests: List["AbsenceRequest"] = Relationship(back_populates="student")


class User(SQLModel, table=True):
    """Administrative user model for school staff."""

    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True, max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole = Field(description="User role (admin, teacher, staff)")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    attendance_records: List["AttendanceRecord"] = Relationship(back_populates="recorded_by_user")
    processed_requests: List["AbsenceRequest"] = Relationship(back_populates="processed_by_user")


class AttendanceRecord(SQLModel, table=True):
    """Daily attendance record for students."""

    __tablename__ = "attendance_records"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    attendance_date: date = Field(description="Date of attendance")
    status: AttendanceStatus = Field(description="Attendance status")
    check_in_time: Optional[datetime] = Field(default=None, description="Time when student checked in")
    notes: str = Field(default="", max_length=500, description="Additional notes about attendance")
    recorded_by: int = Field(foreign_key="users.id", description="Staff member who recorded attendance")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Student = Relationship(back_populates="attendance_records")
    recorded_by_user: User = Relationship(back_populates="attendance_records")


class AbsenceRequest(SQLModel, table=True):
    """Student absence request model."""

    __tablename__ = "absence_requests"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    absence_date: date = Field(description="Date of requested absence")
    reason: str = Field(max_length=1000, description="Reason for absence")
    submitted_by_name: str = Field(max_length=200, description="Name of person submitting request")
    submitted_by_phone: Optional[str] = Field(default=None, max_length=20)
    submitted_by_email: Optional[str] = Field(default=None, max_length=255)
    status: AbsenceRequestStatus = Field(default=AbsenceRequestStatus.PENDING)
    processed_by: Optional[int] = Field(default=None, foreign_key="users.id")
    processed_at: Optional[datetime] = Field(default=None)
    processing_notes: str = Field(default="", max_length=500)
    supporting_documents: List[str] = Field(
        default=[], sa_column=Column(JSON), description="List of document URLs/paths"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Student = Relationship(back_populates="absence_requests")
    processed_by_user: Optional[User] = Relationship(back_populates="processed_requests")


class AttendanceSummary(SQLModel, table=True):
    """Daily attendance summary statistics."""

    __tablename__ = "attendance_summaries"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    summary_date: date = Field(unique=True, description="Date of the summary")
    total_students: int = Field(description="Total number of active students")
    present_count: int = Field(default=0)
    absent_count: int = Field(default=0)
    late_count: int = Field(default=0)
    excused_count: int = Field(default=0)
    attendance_percentage: float = Field(default=0.0, description="Overall attendance percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class StudentCreate(SQLModel, table=False):
    """Schema for creating a new student."""

    student_id: str = Field(max_length=20)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    grade: str = Field(max_length=10)
    class_name: str = Field(max_length=50)
    guardian_name: Optional[str] = Field(default=None, max_length=200)
    guardian_phone: Optional[str] = Field(default=None, max_length=20)


class StudentUpdate(SQLModel, table=False):
    """Schema for updating student information."""

    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    grade: Optional[str] = Field(default=None, max_length=10)
    class_name: Optional[str] = Field(default=None, max_length=50)
    guardian_name: Optional[str] = Field(default=None, max_length=200)
    guardian_phone: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = Field(default=None)


class AttendanceRecordCreate(SQLModel, table=False):
    """Schema for creating attendance record."""

    student_id: int
    attendance_date: date
    status: AttendanceStatus
    check_in_time: Optional[datetime] = Field(default=None)
    notes: str = Field(default="", max_length=500)


class AttendanceRecordUpdate(SQLModel, table=False):
    """Schema for updating attendance record."""

    status: Optional[AttendanceStatus] = Field(default=None)
    check_in_time: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)


class AbsenceRequestCreate(SQLModel, table=False):
    """Schema for creating absence request."""

    student_id: int
    absence_date: date
    reason: str = Field(max_length=1000)
    submitted_by_name: str = Field(max_length=200)
    submitted_by_phone: Optional[str] = Field(default=None, max_length=20)
    submitted_by_email: Optional[str] = Field(default=None, max_length=255)
    supporting_documents: List[str] = Field(default=[])


class AbsenceRequestProcess(SQLModel, table=False):
    """Schema for processing absence request."""

    status: AbsenceRequestStatus
    processing_notes: str = Field(default="", max_length=500)


class UserCreate(SQLModel, table=False):
    """Schema for creating administrative user."""

    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole


class PublicAbsentStudent(SQLModel, table=False):
    """Schema for public display of approved absent students."""

    student_id: str
    full_name: str
    grade: str
    class_name: str
    absence_date: date
    reason: str


class AttendanceStats(SQLModel, table=False):
    """Schema for attendance statistics."""

    date: date
    total_students: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_percentage: float
    pending_requests: int
    approved_absences: int
