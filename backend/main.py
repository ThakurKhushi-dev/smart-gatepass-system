# backend/main.py
# Smart Gatepass System – FastAPI Backend v2
# Run with: uvicorn main:app --reload --port 8000

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import qrcode
import io
import base64
import json

from backend.database import get_db, engine, Base, User, Request, Approval, Log, Attendance
from backend.schemas import (
    LoginRequest, LoginResponse,
    UserCreate, UserResponse,
    GatepassCreate, GatepassResponse,
    ApprovalCreate, ApprovalResponse,
    AttendanceResponse, GateAction
)
from backend.auth import hash_password, verify_password, create_access_token

# ============================================================
# CREATE TABLES ON STARTUP
# ============================================================
Base.metadata.create_all(bind=engine)
from backend.database import SessionLocal
from backend.database import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

authorities = [
    {
        "name": "Warden",
        "email": "warden@gatepass.com",
        "password": "123456",
        "role": "warden"
    },
    {
        "name": "HOD",
        "email": "hod@gatepass.com",
        "password": "123456",
        "role": "hod"
    },
    {
        "name": "Guard",
        "email": "guard@gatepass.com",
        "password": "123456",
        "role": "guard"
    },
    {
        "name": "Class Incharge",
        "email": "incharge@gatepass.com",
        "password": "123456",
        "role": "incharge"
    }
]

for auth in authorities:
    existing = db.query(User).filter(User.email == auth["email"]).first()

    if not existing:
        user = User(
            name=auth["name"],
            email=auth["email"],
            password=pwd_context.hash(auth["password"]),
            role=auth["role"]
        )
        db.add(user)

db.commit()
db.close()

# ============================================================
# APP SETUP
# ============================================================
app = FastAPI(
    title="Smart Gatepass System",
    description="College Gatepass Management API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HELPER: Generate QR code as base64 PNG string
# Called ONLY when a request reaches fully_approved status.
# ============================================================
def generate_qr_code(data: dict) -> str:
    qr_data = json.dumps(data)
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


# ============================================================
# HELPER: Write to logs table
# ============================================================
def add_log(db: Session, request_id: Optional[int], user_id: Optional[int],
            action: str, details: str = ""):
    log = Log(request_id=request_id, user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()


# ============================================================
# HELPER: Determine the first approval stage for a new request
#
# DAY SCHOLAR:
#   → incharge → hod → fully_approved
#
# HOSTELLER (Mon–Fri, 09:00–14:00):
#   → warden → incharge → hod → fully_approved
#
# HOSTELLER (outside above window):
#   → warden → fully_approved  (warden is the only required approver)
# ============================================================
def get_first_stage(student_type: str, out_time_str: Optional[str]) -> str:
    if student_type == "day_scholar":
        return "incharge"

    # Hosteller: decide based on current weekday and the requested out_time
    now = datetime.now()
    weekday = now.weekday()          # 0=Mon … 6=Sun

    # Try to parse the out_time to determine office-hours context.
    # out_time is a free-text string like "10:30 AM"; fall back to current hour.
    hour = now.hour
    try:
        if out_time_str:
            # Handle formats: "10:30 AM", "14:00", "2:00 PM"
            t = out_time_str.strip().upper()
            if "AM" in t or "PM" in t:
                time_part = t.replace("AM", "").replace("PM", "").strip()
                h, m = map(int, time_part.split(":"))
                if "PM" in t and h != 12:
                    h += 12
                if "AM" in t and h == 12:
                    h = 0
                hour = h
            else:
                hour = int(out_time_str.split(":")[0])
    except Exception:
        pass

    is_weekday      = weekday < 5           # Monday to Friday
    is_office_hours = 9 <= hour < 14        # 09:00 to 13:59

    if is_weekday and is_office_hours:
        # Full chain: warden → incharge → hod
        return "warden"
    else:
        # Warden-only chain
        return "warden_only"


# ============================================================
# HELPER: Given current status + student_type + approval_stage,
# return (new_status, new_approval_stage) after an "approved" action.
# Returns ("fully_approved", "done") when the chain is complete.
# ============================================================
def advance_approval(current_status: str, approval_stage: str,
                     student_type: str) -> tuple:
    """
    Approval chains:
      day_scholar         : incharge → hod → fully_approved
      hosteller (full)    : warden → incharge → hod → fully_approved
      hosteller (warden)  : warden_only → fully_approved
    """
    if approval_stage == "incharge":
        # Day scholar: next is HOD
        # Hosteller (full chain): next is HOD
        return "approved_by_incharge", "hod"

    if approval_stage == "hod":
        # HOD is always the last step for both day scholar and hosteller full chain
        return "fully_approved", "done"

    if approval_stage == "warden":
        # Hosteller full chain: warden approved, next is incharge
        return "approved_by_warden", "incharge"

    if approval_stage == "warden_only":
        # Hosteller warden-only chain: done immediately
        return "fully_approved", "done"

    # Fallback (should not happen)
    return "fully_approved", "done"


# ============================================================
# ROOT
# ============================================================
@app.get("/")
def root():
    return {"message": "Smart Gatepass System API v2 is running!"}


# ============================================================
# AUTH ENDPOINTS
# ============================================================

@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login for ALL roles (student / authorities / guard)."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email, "role": user.role, "user_id": user.id})
    add_log(db, None, user.id, "LOGIN", f"{user.name} logged in as {user.role}")

    return LoginResponse(
        token=token,
        user_id=user.id,
        name=user.name,
        role=user.role,
        email=user.email
    )


@app.post("/auth/register", response_model=UserResponse)
def register_student(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Student self-registration.
    Authorities are pre-created via schema.sql and cannot self-register.
    """
    # Only students may self-register
    if user_data.role != "student":
        raise HTTPException(status_code=403,
                            detail="Only students can self-register. Authorities are pre-created by admin.")

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if not user_data.department:
        raise HTTPException(status_code=400, detail="Department is required for students")
    if not user_data.semester:
        raise HTTPException(status_code=400, detail="Semester is required for students")
    if not user_data.student_type:
        raise HTTPException(status_code=400, detail="Student type is required (day_scholar or hosteller)")
    if user_data.student_type not in ("day_scholar", "hosteller"):
        raise HTTPException(status_code=400, detail="student_type must be 'day_scholar' or 'hosteller'")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role="student",
        department=user_data.department,
        semester=user_data.semester,
        student_type=user_data.student_type,
        phone=user_data.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
   # AUTO GENERATE ATTENDANCE
    import random
    subjects = [
        "DBMS",
        "Operating Systems",
        "Computer Networks",
        "Python"
    ]
    for sub in subjects:
        total = random.randint(35, 45)
        attended = random.randint(25, total)
        attendance = Attendance(
            student_id=new_user.id,
            subject=sub,
            total_classes=total,
            attended_classes=attended
        )
        db.add(attendance)
    # commit ONCE after loop
    db.commit()
    add_log(
        db,
        None,
        new_user.id,
        "REGISTER",
        f"New student registered: {new_user.name}"
    )
    return new_user

# ============================================================
# USER ENDPOINTS
# ============================================================

@app.post("/users/register", response_model=UserResponse)
def register_user_legacy(user_data: UserCreate, db: Session = Depends(get_db)):
    """Legacy alias for /auth/register (keeps backward compat)."""
    return register_student(user_data, db)


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================================
# GATEPASS REQUEST ENDPOINTS
# ============================================================

def _build_response_dict(r: Request) -> dict:
    """Convert a Request ORM object to a plain dict for responses."""
    return {
        "id": r.id,
        "student_id": r.student_id,
        "student_name": r.student_name,
        "student_email": r.student_email,
        "department": r.department,
        "semester": r.semester,
        "student_type": r.student_type,
        "reason": r.reason,
        "parent_phone": r.parent_phone,
        "request_subtype": r.request_subtype or "",
        "out_time": r.out_time,
        "in_time": r.in_time,
        "out_date": r.out_date,
        "return_date": r.return_date,
        "return_time": r.return_time,
        # NO is_emergency
        "status": r.status,
        "approval_stage": r.approval_stage,
        "exit_marked": r.exit_marked,
        "entry_marked": r.entry_marked,
        "exit_time": str(r.exit_time) if r.exit_time else None,
        "entry_time": str(r.entry_time) if r.entry_time else None,
        # QR code is only set once status == fully_approved; always fetch live from DB
        "qr_code": r.qr_code,
        "created_at": str(r.created_at)
    }


@app.post("/requests/create")
def create_request(request_data: GatepassCreate, db: Session = Depends(get_db)):
    """
    Submit a new gatepass request.
    Student info is fetched from the DB using student_id (not passed by frontend form).
    """
    # Load student from DB to auto-fill denormalised fields
    student = db.query(User).filter(User.id == request_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if student.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit gatepass requests")

    # ── Backend time/date validation ──────────────────────────────────────────
    stype = student.student_type  # "day_scholar" | "hosteller"

    if stype == "day_scholar":
        # out_time is always required; in_time is optional (frontend marks when returning same day)
        if not request_data.out_time:
            raise HTTPException(status_code=400, detail="Out time is required for day scholars")

    elif stype == "hosteller":
        subtype = (request_data.request_subtype or "").strip()

        if subtype == "outing":
            # Both out_time and in_time are required
            if not request_data.out_time:
                raise HTTPException(status_code=400, detail="Out time is required for outing")
            if not request_data.in_time:
                raise HTTPException(status_code=400, detail="In time is required for outing")

        elif subtype == "leave":
            # out_date, out_time, return_date, return_time are all required
            if not request_data.out_date:
                raise HTTPException(status_code=400, detail="Out date is required for leave")
            if not request_data.out_time:
                raise HTTPException(status_code=400, detail="Out time is required for leave")
            if not request_data.return_date:
                raise HTTPException(status_code=400, detail="Return date is required for leave")
            if not request_data.return_time:
                raise HTTPException(status_code=400, detail="Return time is required for leave")

        else:
            raise HTTPException(status_code=400,
                                detail="Hosteller must choose request_subtype: 'outing' or 'leave'")

    # ── Determine approval chain ──────────────────────────────────────────────
    first_stage = get_first_stage(stype, request_data.out_time)

    new_req = Request(
        student_id     = student.id,
        student_name   = student.name,
        student_email  = student.email,
        department     = student.department or "",
        semester       = student.semester or 0,
        student_type   = stype,
        reason         = request_data.reason,
        parent_phone   = request_data.parent_phone,
        request_subtype= request_data.request_subtype or "",
        out_time       = request_data.out_time,
        in_time        = request_data.in_time,
        out_date       = request_data.out_date,
        return_date    = request_data.return_date,
        return_time    = request_data.return_time,
        # NO is_emergency
        status         = "pending",
        approval_stage = first_stage,
        # QR is NOT generated here – only on final approval
        qr_code        = None,
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    add_log(db, new_req.id, student.id,
            "REQUEST_CREATED",
            f"Request created by {student.name}. Stage: {first_stage}")

    return _build_response_dict(new_req)


@app.get("/requests/student/{student_id}")
def get_student_requests(student_id: int, db: Session = Depends(get_db)):
    """Get all requests submitted by a specific student."""
    reqs = db.query(Request)\
             .filter(Request.student_id == student_id)\
             .order_by(Request.created_at.desc())\
             .all()
    return [_build_response_dict(r) for r in reqs]


@app.get("/requests/pending/{role}")
def get_pending_requests(role: str, db: Session = Depends(get_db)):
    """
    Return requests that are currently waiting for the given role to act.

    Mapping of role → approval_stage values they handle:
      incharge → approval_stage IN ("incharge")
                        status IN ("pending", "approved_by_warden")
      hod            → approval_stage == "hod"
                        status IN ("approved_by_incharge", "approved_by_warden")
                        BUT for day_scholar: status == "approved_by_incharge"
                        For hosteller full: status == "approved_by_incharge"  (after warden+incharge)
      warden         → approval_stage IN ("warden", "warden_only")
                        status == "pending"
      guard     → status == "fully_approved"
    """
    if role == "incharge":
        reqs = db.query(Request).filter(
            Request.approval_stage == "incharge",
            Request.status.in_(["pending", "approved_by_warden"])
        ).all()

    elif role == "hod":
        reqs = db.query(Request).filter(
            Request.approval_stage == "hod",
            Request.status.in_(["approved_by_incharge"])
        ).all()

    elif role == "warden":
        reqs = db.query(Request).filter(
            Request.approval_stage.in_(["warden", "warden_only"]),
            Request.status == "pending"
        ).all()

    elif role == "guard":
        reqs = db.query(Request).filter(
            Request.status == "fully_approved"
        ).all()

    else:
        reqs = []

    return [_build_response_dict(r) for r in reqs]


@app.get("/requests/all")
def get_all_requests(db: Session = Depends(get_db)):
    """Get all requests ordered newest first."""
    reqs = db.query(Request).order_by(Request.created_at.desc()).all()
    return [_build_response_dict(r) for r in reqs]


@app.get("/requests/{request_id}")
def get_request_detail(request_id: int, db: Session = Depends(get_db)):
    """
    Get a single request by ID.
    Always reads fresh from DB so the QR / status is never stale.
    """
    r = db.query(Request).filter(Request.id == request_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Request not found")
    return _build_response_dict(r)


# ============================================================
# APPROVAL ENDPOINTS
# ============================================================

@app.post("/approvals/action")
def approve_or_reject(approval_data: ApprovalCreate, db: Session = Depends(get_db)):
    """
    Approve or reject a gatepass request.

    Full approval chains:
      Day Scholar        : incharge → hod → fully_approved
      Hosteller (office) : warden → incharge → hod → fully_approved
      Hosteller (other)  : warden_only → fully_approved
    """
    request = db.query(Request).filter(Request.id == approval_data.request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    approver = db.query(User).filter(User.id == approval_data.approver_id).first()
    if not approver:
        raise HTTPException(status_code=404, detail="Approver not found")

    # Verify that this approver's role matches what the request is waiting for
    expected_stage = request.approval_stage
    acting_role    = approval_data.approver_role

    # Map "warden_only" stage → warden can act
    valid_stage_for_role = {
        "incharge": ["incharge"],
        "hod":            ["hod"],
        "warden":         ["warden", "warden_only"],
    }
    allowed_stages = valid_stage_for_role.get(acting_role, [])
    if expected_stage not in allowed_stages:
        raise HTTPException(
            status_code=403,
            detail=f"This request is currently waiting for '{expected_stage}', not '{acting_role}'"
        )

    # Save approval record
    approval = Approval(
        request_id    = approval_data.request_id,
        approver_id   = approval_data.approver_id,
        approver_role = approval_data.approver_role,
        action        = approval_data.action,
        comments      = approval_data.comments
    )
    db.add(approval)

    if approval_data.action == "rejected":
        request.status         = "rejected"
        request.approval_stage = "rejected"

    elif approval_data.action == "approved":
        new_status, new_stage = advance_approval(
            request.status, request.approval_stage, request.student_type
        )
        request.status         = new_status
        request.approval_stage = new_stage

        # ── Generate QR ONLY when fully approved ─────────────────────────────
        if new_status == "fully_approved":
            qr_data = {
                "request_id": str(request.id),
                "student_name": str(request.student_name or ""),
                "department": str(request.department or ""),
                "out_time": str(request.out_time or ""),
                "in_time": str(request.in_time or ""),
                "out_date": str(request.out_date or ""),
                "return_date": str(request.return_date or ""),
                "return_time": str(request.return_time or ""),
                "status": "fully_approved"
                }
            request.qr_code = generate_qr_code(qr_data)

    else:
        raise HTTPException(status_code=400, detail="Action must be 'approved' or 'rejected'")

    db.commit()
    db.refresh(request)

    add_log(db, request.id, approval_data.approver_id,
            f"REQUEST_{approval_data.action.upper()}",
            f"{approver.name} ({approval_data.approver_role}) {approval_data.action} request #{request.id}")

    return {
        "message":    f"Request {approval_data.action} successfully",
        "new_status": request.status,
        "next_stage": request.approval_stage,
        "request_id": request.id
    }


@app.get("/approvals/{request_id}")
def get_approvals_for_request(request_id: int, db: Session = Depends(get_db)):
    """Return full approval history for a request."""
    approvals = db.query(Approval).filter(Approval.request_id == request_id).all()
    result = []
    for a in approvals:
        approver = db.query(User).filter(User.id == a.approver_id).first()
        result.append({
            "id":            a.id,
            "approver_name": approver.name if approver else "Unknown",
            "approver_role": a.approver_role,
            "action":        a.action,
            "comments":      a.comments,
            "approved_at":   str(a.approved_at)
        })
    return result


# ============================================================
# ATTENDANCE ENDPOINTS
# ============================================================

@app.get("/attendance/{student_id}")
def get_attendance(student_id: int, db: Session = Depends(get_db)):
    records = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    result = []
    for a in records:
        pct = round((a.attended_classes / a.total_classes) * 100, 1) if a.total_classes > 0 else 0
        result.append({
            "subject":           a.subject,
            "total_classes":     a.total_classes,
            "attended_classes":  a.attended_classes,
            "percentage":        pct
        })
    return result


# ============================================================
# GATE ENDPOINTS
# ============================================================

@app.post("/gate/action")
def gate_action(action_data: GateAction, db: Session = Depends(get_db)):
    """Mark exit or entry at the gate. Only works on fully_approved requests."""
    request = db.query(Request).filter(Request.id == action_data.request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != "fully_approved":
        raise HTTPException(status_code=400,
                            detail="Request is not fully approved yet. Cannot mark gate action.")

    if action_data.action == "exit":
        request.exit_marked = True
        request.exit_time   = datetime.utcnow()
        message = "Exit marked successfully"
    elif action_data.action == "entry":
        request.entry_marked = True
        request.entry_time   = datetime.utcnow()
        message = "Entry marked successfully"
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'exit' or 'entry'")

    db.commit()

    add_log(db, request.id, action_data.guard_id,
            f"GATE_{action_data.action.upper()}",
            f"Gate {action_data.action} marked for {request.student_name}")

    return {"message": message, "request_id": request.id}


@app.get("/gate/qr/{request_id}")
def get_qr_code(request_id: int, db: Session = Depends(get_db)):
    """
    Always reads status and QR code fresh from the DB.
    QR code is None until the request is fully_approved.
    """
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return {
        "request_id": request.id,
        "status":     request.status,
        # Only return QR when actually approved; never return stale Pending QR
        "qr_code":    request.qr_code if request.status == "fully_approved" else None
    }


# ============================================================
# LOGS ENDPOINT
# ============================================================

@app.get("/logs")
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(Log.logged_at.desc()).limit(limit).all()
    return [
        {
            "id":         l.id,
            "request_id": l.request_id,
            "user_id":    l.user_id,
            "action":     l.action,
            "details":    l.details,
            "logged_at":  str(l.logged_at)
        }
        for l in logs
    ]


# ============================================================
# STATS ENDPOINT
# ============================================================

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total    = db.query(Request).count()
    pending  = db.query(Request).filter(Request.status == "pending").count()
    approved = db.query(Request).filter(Request.status == "fully_approved").count()
    rejected = db.query(Request).filter(Request.status == "rejected").count()
    in_progress = db.query(Request).filter(
        Request.status.in_(["approved_by_incharge", "approved_by_hod", "approved_by_warden"])
    ).count()

    return {
        "total_requests": total,
        "pending":        pending,
        "approved":       approved,
        "rejected":       rejected,
        "in_progress":    in_progress
    }
