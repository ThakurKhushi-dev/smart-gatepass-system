# backend/database.py
# Database connection and SQLAlchemy models

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# ============================================================
# DATABASE CONNECTION
# Change username / password / host to match your MySQL setup
# ============================================================
DATABASE_URL = "mysql+pymysql://root:KmQnLShIEdlMyhjdXwezHifzTWWIbBWD@mysql.railway.internal:3306/railway"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# DATABASE MODELS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100), nullable=False)
    email        = Column(String(100), unique=True, nullable=False)
    password     = Column(String(255), nullable=False)
    # role values: student | incharge | hod | warden | guard
    role         = Column(String(50), nullable=False)
    department   = Column(String(100))
    semester     = Column(Integer)
    # student_type values: day_scholar | hosteller
    student_type = Column(String(20))
    phone        = Column(String(15))
    created_at   = Column(DateTime, default=datetime.utcnow)


class Request(Base):
    __tablename__ = "requests"

    id             = Column(Integer, primary_key=True, index=True)
    student_id     = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Denormalised student info (snapshot at time of submission)
    student_name   = Column(String(100), nullable=False)
    student_email  = Column(String(100), nullable=False)
    department     = Column(String(100), nullable=False)
    semester       = Column(Integer, nullable=False)
    student_type   = Column(String(20), nullable=False)  # day_scholar | hosteller

    reason         = Column(Text, nullable=False)
    parent_phone   = Column(String(15), nullable=False)

    # Request sub-type: "outing" | "leave" | "" (day_scholars have no subtype)
    request_subtype = Column(String(20), default="")

    # Time / date fields
    out_time       = Column(String(20))   # e.g. "10:30 AM"
    in_time        = Column(String(20))   # e.g. "04:00 PM" – optional for day_scholar leaving only
    out_date       = Column(String(20))   # YYYY-MM-DD – hosteller leave departure date
    return_date    = Column(String(20))   # YYYY-MM-DD – hosteller leave return date
    return_time    = Column(String(20))   # e.g. "06:00 PM" – hosteller leave return time

    # ── REMOVED: is_emergency ──

    # Approval flow
    # status values:
    #   pending | approved_by_incharge | approved_by_hod | fully_approved | rejected
    status         = Column(String(50), default="pending")

    # approval_stage: which role must act NEXT
    #   "incharge" | "hod" | "warden" | "done" | "rejected"
    approval_stage = Column(String(50), default="incharge")

    # Gate tracking
    exit_marked    = Column(Boolean, default=False)
    entry_marked   = Column(Boolean, default=False)
    exit_time      = Column(DateTime)
    entry_time     = Column(DateTime)

    # QR code – stored as base64 PNG string, set ONLY when status == fully_approved
    qr_code        = Column(Text)

    created_at     = Column(DateTime, default=datetime.utcnow)


class Approval(Base):
    __tablename__ = "approvals"

    id            = Column(Integer, primary_key=True, index=True)
    request_id    = Column(Integer, ForeignKey("requests.id"), nullable=False)
    approver_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_role = Column(String(50), nullable=False)
    action        = Column(String(20), nullable=False)   # approved | rejected
    comments      = Column(Text)
    approved_at   = Column(DateTime, default=datetime.utcnow)


class Log(Base):
    __tablename__ = "logs"

    id         = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    user_id    = Column(Integer, ForeignKey("users.id"))
    action     = Column(String(255), nullable=False)
    details    = Column(Text)
    logged_at  = Column(DateTime, default=datetime.utcnow)


class Attendance(Base):
    __tablename__ = "attendance"

    id               = Column(Integer, primary_key=True, index=True)
    student_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject          = Column(String(100), nullable=False)
    total_classes    = Column(Integer, default=0)
    attended_classes = Column(Integer, default=0)


# ============================================================
# DEPENDENCY – get DB session
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
