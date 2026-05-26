# backend/schemas.py
# Pydantic models for request and response validation

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ============================================================
# AUTH SCHEMAS
# ============================================================
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: int
    name: str
    role: str
    email: str


# ============================================================
# USER SCHEMAS
# ============================================================
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str                           # always "student" for self-registration
    department: Optional[str] = None
    semester: Optional[int] = None
    student_type: Optional[str] = None  # "day_scholar" or "hosteller"
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    department: Optional[str]
    semester: Optional[int]
    student_type: Optional[str]
    phone: Optional[str]

    class Config:
        from_attributes = True


# ============================================================
# GATEPASS REQUEST SCHEMAS
#
# REMOVED fields (auto-fetched from logged-in student):
#   student_name, student_email, department, semester, student_type
#
# REMOVED:
#   is_emergency  (feature removed completely)
#
# ADDED:
#   out_date      – for hosteller leave: departure date (YYYY-MM-DD)
#   return_date   – for hosteller leave: return date (YYYY-MM-DD)
#   return_time   – for hosteller leave: return time (HH:MM AM/PM)
#   request_subtype – "outing" | "leave" | "" (for hostellers)
# ============================================================
class GatepassCreate(BaseModel):
    # Only the student_id comes from session; everything else the student fills in
    student_id: int
    reason: str
    parent_phone: str
    request_subtype: Optional[str] = ""   # "outing" | "leave" | "" (day_scholar has no subtype)
    out_time: Optional[str] = None        # HH:MM AM/PM – required for all types
    in_time: Optional[str] = None         # HH:MM AM/PM – optional for day_scholar leaving only
    out_date: Optional[str] = None        # YYYY-MM-DD  – hosteller leave departure date
    return_date: Optional[str] = None     # YYYY-MM-DD  – hosteller leave return date
    return_time: Optional[str] = None     # HH:MM AM/PM – hosteller leave return time


class GatepassResponse(BaseModel):
    id: int
    student_id: int
    # These are stored on the Request row (denormalised for convenience)
    student_name: str
    student_email: str
    department: str
    semester: int
    student_type: str
    reason: str
    parent_phone: str
    request_subtype: Optional[str]
    out_time: Optional[str]
    in_time: Optional[str]
    out_date: Optional[str]
    return_date: Optional[str]
    return_time: Optional[str]
    # NO is_emergency field
    status: str                 # pending | approved_by_incharge | approved_by_hod | fully_approved | rejected
    approval_stage: str         # tracks which role must act next
    exit_marked: bool
    entry_marked: bool
    exit_time: Optional[datetime]
    entry_time: Optional[datetime]
    qr_code: Optional[str]      # NULL until status == "fully_approved"
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# APPROVAL SCHEMAS
# ============================================================
class ApprovalCreate(BaseModel):
    request_id: int
    approver_id: int
    approver_role: str          # "incharge" | "hod" | "warden"
    action: str                 # "approved" | "rejected"
    comments: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    request_id: int
    approver_id: int
    approver_role: str
    action: str
    comments: Optional[str]
    approved_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# ATTENDANCE SCHEMAS
# ============================================================
class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    subject: str
    total_classes: int
    attended_classes: int
    percentage: float

    class Config:
        from_attributes = True


# ============================================================
# GATE ACTION SCHEMAS
# guard_id is optional – frontend passes it when available
# ============================================================
class GateAction(BaseModel):
    request_id: int
    action: str                 # "exit" or "entry"
    guard_id: Optional[int] = None
