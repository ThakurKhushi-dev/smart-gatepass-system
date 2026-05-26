# frontend/pages/student.py
# Student Dashboard
#
# CHANGES:
#   - New sidebar UI: Dashboard | Create Request | My Requests | Attendance | Logout
#   - Request form: removed Name/Email/Dept/Sem/Type (auto-fetched from logged-in student)
#   - Removed is_emergency checkbox completely
#   - Added proper time/date validation per student type
#   - QR code shown ONLY when status == "fully_approved"

import streamlit as st
import base64
from datetime import date, datetime


def show_student_dashboard(api_get, api_post, status_badge):
    # ── Sidebar navigation ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 📌 Student Menu")
        page = st.radio(
            "Navigate",
            [
                "🏠 Dashboard",
                "📋 Create Request",
                "📁 My Requests",
                "📊 Attendance",
            ],
            label_visibility="collapsed"
        )
        # Note: Logout button is rendered in app.py sidebar (above this block)

    # ── Route to sub-page ─────────────────────────────────────────────────────
    if page == "🏠 Dashboard":
        show_dashboard(api_get)
    elif page == "📋 Create Request":
        show_new_request(api_get, api_post)
    elif page == "📁 My Requests":
        show_my_requests(api_get, status_badge)
    elif page == "📊 Attendance":
        show_attendance(api_get)


# ============================================================
# DASHBOARD
# ============================================================
def show_dashboard(api_get):
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Student Dashboard</h1>
        <p>Submit and track your gatepass requests</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch student info for a personalised greeting
    user_data = api_get(f"/users/{st.session_state.user_id}")
    if user_data:
        stype = "Day Scholar" if user_data.get("student_type") == "day_scholar" else "Hosteller"
        st.markdown(f"""
        <div class="info-card">
            <strong>👤 {user_data['name']}</strong> &nbsp;|&nbsp;
            {user_data.get('department','—')} &nbsp;|&nbsp;
            Semester {user_data.get('semester','—')} &nbsp;|&nbsp;
            {stype}
        </div>
        """, unsafe_allow_html=True)

    # Request summary stats
    requests = api_get(f"/requests/student/{st.session_state.user_id}")
    if requests:
        total    = len(requests)
        pending  = sum(1 for r in requests if r["status"] == "pending")
        approved = sum(1 for r in requests if r["status"] == "fully_approved")
        rejected = sum(1 for r in requests if r["status"] == "rejected")
        in_prog  = total - pending - approved - rejected

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="stat-box"><h2>{total}</h2><p>Total</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-box" style="background:linear-gradient(135deg,#f57c00,#ff9800)"><h2>{pending}</h2><p>Pending</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-box" style="background:linear-gradient(135deg,#0277bd,#039be5)"><h2>{in_prog}</h2><p>In Progress</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stat-box" style="background:linear-gradient(135deg,#2e7d32,#43a047)"><h2>{approved}</h2><p>Approved</p></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="stat-box" style="background:linear-gradient(135deg,#c62828,#e53935)"><h2>{rejected}</h2><p>Rejected</p></div>', unsafe_allow_html=True)
    else:
        st.info("No requests yet. Click **Create Request** in the sidebar to get started.")


# ============================================================
# CREATE REQUEST
# Auto-fetches student info. NO emergency checkbox.
# ============================================================
def show_new_request(api_get, api_post):
    st.markdown("""
    <div class="main-header">
        <h1>📋 New Gatepass Request</h1>
        <p>Fill in the details below to submit your request</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load student info from backend ────────────────────────────────────────
    user_data = api_get(f"/users/{st.session_state.user_id}")
    if not user_data:
        st.error("⚠️ Could not load your profile. Make sure the backend is running.")
        return

    student_type = user_data.get("student_type", "day_scholar")   # "day_scholar" | "hosteller"
    stype_label  = "Day Scholar" if student_type == "day_scholar" else "Hosteller"

    # Show auto-fetched info (read-only)
    st.markdown(f"""
    <div class="alert-info">
        ℹ️ <strong>Submitting as:</strong>
        {user_data['name']} &nbsp;|&nbsp;
        {user_data.get('department','—')} &nbsp;|&nbsp;
        Sem {user_data.get('semester','—')} &nbsp;|&nbsp;
        <strong>{stype_label}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Approval chain preview ────────────────────────────────────────────────
    if student_type == "day_scholar":
        st.info("📋 **Approval chain:** Class Incharge → HOD")
    else:
        now = datetime.now()
        if now.weekday() < 5 and 9 <= now.hour < 14:
            st.info("📋 **Approval chain (Mon–Fri 9AM–2PM):** Warden → Class Incharge → HOD")
        else:
            st.info("📋 **Approval chain (outside office hours):** Warden only")

    st.markdown("---")
    # ── HOSTELLER REQUEST TYPE SELECTOR ─────────────────────────
    if student_type == "hosteller":
        request_subtype = st.radio(
            "📌 Request Type *",
            ["outing", "leave"],
            horizontal=True,
            format_func=lambda x: 
              "Outing (same day)"
              if x == "outing"
              else "Leave (overnight / multi-day)"
        )
    else:
        request_subtype = ""

    with st.form("gatepass_form", clear_on_submit=True):
        # ── Common fields (kept as required) ──────────────────────────────────
        reason       = st.text_area("📝 Reason for Leave / Outing *",
                                    placeholder="Describe the reason clearly…", height=100)
        parent_phone = st.text_input("📞 Parent Phone Number *",
                                     placeholder="e.g. 9876543210")

        st.markdown("---")

        # ── Time / date fields (depend on student type) ───────────────────────
        out_time_val    = None
        in_time_val     = None
        out_date_val    = None
        return_date_val = None
        return_time_val = None
       

        # ── DAY SCHOLAR ────────────────────────────────────────────────────────
        if student_type == "day_scholar":
            st.markdown("#### 🕐 Time Details")
            st.caption("Out Time is always required. Fill In Time only if you are returning the same day.")

            returning_same_day = st.checkbox("Returning same day?", value=True,
                                             key="day_scholar_return")

            col1, col2 = st.columns(2)
            with col1:
                out_time_val = st.text_input("⏰ Out Time *", placeholder="e.g. 10:30 AM",
                                             key="ds_out")
            with col2:
                if returning_same_day:
                    in_time_val = st.text_input("⏰ In Time *", placeholder="e.g. 04:00 PM",
                                                key="ds_in")
                else:
                    st.text_input("⏰ In Time", placeholder="Not required (not returning today)",
                                  disabled=True, key="ds_in_dis")
            # ── HOSTELLER ──────────────────────────────────────────────────────────
        else:
            st.markdown("---")
            # ================= OUTING =================  
            if request_subtype == "outing":
                st.markdown("#### 🕐 Outing Time Details")
                st.caption("Both Out Time and In Time are required for an outing.")
                
                col1, col2 = st.columns(2)
                with col1:
                    out_time_val = st.text_input(
                        "⏰ Out Time *",
                        placeholder="e.g. 10:30 AM",
                        key="outing_out_time"
                        )
                    
                with col2:
                    in_time_val = st.text_input(
                        "⏰ In Time *",
                        placeholder="e.g. 07:00 PM",
                        key="outing_in_time"
                        )
            # ================= LEAVE =================
            elif request_subtype == "leave":
                st.markdown("#### 📅 Leave Details")
                st.caption("Fill all departure and return details.")
                col1, col2 = st.columns(2)
                with col1:
                    out_date_obj = st.date_input(
                        "📅 Going Date *",
                        min_value=date.today(),
                        key="leave_out_date"
                        )
                    
                    out_date_val = str(out_date_obj)
                    out_time_val = st.text_input(
                        "⏰ Going Time *",
                        placeholder="e.g. 10:30 AM",
                        key="leave_out_time"
                        )
                with col2:
                    return_date_obj = st.date_input(
                        "📅 Return Date *",
                        min_value=date.today(),
                        key="leave_return_date"
                        )
                    return_date_val = str(return_date_obj)
                    return_time_val = st.text_input(
                        "⏰ Return Time *",
                        placeholder="e.g. 06:00 PM",
                        key="leave_return_time"
                        )
                            # ── Submit button ───────────────────────────────────────────────
        submitted = st.form_submit_button("🚀 Submit Request")
        if submitted:
            errors = []
            if not reason.strip():
                errors.append("Reason is required")
            if not parent_phone.strip():
                errors.append("Parent phone number is required")
            if student_type == "day_scholar":
                if not out_time_val or not out_time_val.strip():
                    errors.append("Out Time is required")
                # If returning same day, in_time is also required
                returning = st.session_state.get("day_scholar_return", True)
                if returning and (not in_time_val or not in_time_val.strip()):
                    errors.append("In Time is required when returning same day")
            elif student_type == "hosteller":
                if request_subtype == "outing":
                    if not out_time_val or not out_time_val.strip():
                        errors.append("Out Time is required for outing")
                    if not in_time_val or not in_time_val.strip():
                        errors.append("In Time is required for outing")
                elif request_subtype == "leave":
                    if not out_date_val:
                        errors.append("Departure Date is required for leave")
                    if not out_time_val or not out_time_val.strip():
                        errors.append("Departure Time is required for leave")
                    if not return_date_val:
                        errors.append("Return Date is required for leave")
                    if not return_time_val or not return_time_val.strip():
                        errors.append("Return Time is required for leave")
                    # Date order check
                    if out_date_val and return_date_val and return_date_val < out_date_val:
                        errors.append("Return Date cannot be before Departure Date")

            if errors:
                for e in errors:
                    st.error(f"❌ {e}")
            else:
                payload = {
                    "student_id":     st.session_state.user_id,
                    "reason":         reason.strip(),
                    "parent_phone":   parent_phone.strip(),
                    "request_subtype": request_subtype,
                    "out_time":       out_time_val.strip()    if out_time_val    else None,
                    "in_time":        in_time_val.strip()     if in_time_val     else None,
                    "out_date":       out_date_val            if out_date_val    else None,
                    "return_date":    return_date_val         if return_date_val else None,
                    "return_time":    return_time_val.strip() if return_time_val else None,
                    }
                result, status = api_post("/requests/create", payload)
                if status == 200:
                    st.session_state.notification = {
                        "type": "success",
                        "msg":  f"Request #{result.get('id')} submitted successfully! Awaiting approval."
                        }
                    st.rerun()
                else:
                    st.error(f"❌ Failed: {result.get('detail', 'Unknown error')}")


# ============================================================
# MY REQUESTS
# ============================================================
def show_my_requests(api_get, status_badge):
    st.markdown("""
    <div class="main-header">
        <h1>📁 My Requests</h1>
        <p>Track status of all your gatepass requests</p>
    </div>
    """, unsafe_allow_html=True)

    requests = api_get(f"/requests/student/{st.session_state.user_id}")
    if not requests:
        st.info("You haven't submitted any requests yet. Click **Create Request** to get started.")
        return

    # Summary row
    pending  = sum(1 for r in requests if r["status"] == "pending")
    approved = sum(1 for r in requests if r["status"] == "fully_approved")
    rejected = sum(1 for r in requests if r["status"] == "rejected")
    in_prog  = len(requests) - pending - approved - rejected

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="stat-box"><h2>{len(requests)}</h2><p>Total</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box" style="background:linear-gradient(135deg,#f57c00,#ff9800)"><h2>{pending}</h2><p>Pending</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box" style="background:linear-gradient(135deg,#0277bd,#039be5)"><h2>{in_prog}</h2><p>In Progress</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-box" style="background:linear-gradient(135deg,#2e7d32,#43a047)"><h2>{approved}</h2><p>Approved</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="stat-box" style="background:linear-gradient(135deg,#c62828,#e53935)"><h2>{rejected}</h2><p>Rejected</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    for r in requests:
        label = f"Request #{r['id']} — {r['reason'][:50]}... | {status_badge(r['status'])}"
        with st.expander(label):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {r.get('request_subtype','—') or 'Day Scholar Leave'}")
                st.write(f"**Reason:** {r['reason']}")
                st.write(f"**Parent Phone:** {r['parent_phone']}")
                st.write(f"**Submitted:** {r['created_at'][:16]}")
            with col2:
                st.write(f"**Out Time:** {r.get('out_time') or '—'}")
                st.write(f"**In Time:** {r.get('in_time') or '—'}")
                if r.get("out_date"):
                    st.write(f"**Departure Date:** {r['out_date']}")
                if r.get("return_date"):
                    st.write(f"**Return Date:** {r['return_date']}")
                if r.get("return_time"):
                    st.write(f"**Return Time:** {r['return_time']}")

            # Approval history
            approvals = api_get(f"/approvals/{r['id']}")
            if approvals:
                st.markdown("**✅ Approval History:**")
                for a in approvals:
                    icon = "✅" if a["action"] == "approved" else "❌"
                    st.write(
                        f"  {icon} **{a['approver_role'].replace('_',' ').title()}** "
                        f"— {a['approver_name']} ({a['approved_at'][:16]})"
                    )
                    if a.get("comments"):
                        st.caption(f"    Comment: {a['comments']}")

            # Gate status (only relevant for fully approved)
            if r["status"] == "fully_approved":
                st.markdown("---")
                st.markdown("**🚪 Gate Status:**")
                c1, c2 = st.columns(2)
                with c1:
                    if r["exit_marked"]:
                        st.success(f"✅ Exit: {(r['exit_time'] or '')[:16] or 'N/A'}")
                    else:
                        st.warning("⏳ Exit not yet marked")
                with c2:
                    if r["entry_marked"]:
                        st.success(f"✅ Entry: {(r['entry_time'] or '')[:16] or 'N/A'}")
                    else:
                        st.warning("⏳ Entry not yet marked")

            # ── QR Code: only show after fully_approved ────────────────────────
            if r["status"] == "fully_approved":
                st.markdown("---")
                st.markdown("**📱 Your Gatepass QR Code:**")
                # Always fetch fresh from DB
                qr_data = api_get(f"/gate/qr/{r['id']}")
                if qr_data and qr_data.get("qr_code"):
                    img_bytes = base64.b64decode(qr_data["qr_code"])
                    st.image(img_bytes, caption=f"QR Pass — Request #{r['id']}", width=200)
                else:
                    st.info("QR code not available yet.")
            else:
                # Do NOT show QR for pending / in-progress requests
                st.caption("🔒 QR code will be generated once all approvals are complete.")


# ============================================================
# ATTENDANCE
# ============================================================
def show_attendance(api_get):
    st.markdown("""
    <div class="main-header">
        <h1>📊 My Attendance</h1>
        <p>Subject-wise attendance summary</p>
    </div>
    """, unsafe_allow_html=True)

    records = api_get(f"/attendance/{st.session_state.user_id}")
    if not records:
        st.info("No attendance data found for your account.")
        return

    # Overall average
    avg = sum(r["percentage"] for r in records) / len(records)
    color = "#2e7d32" if avg >= 75 else "#f57c00" if avg >= 60 else "#c62828"
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color},{color}99);
                color:white;padding:20px;border-radius:12px;
                text-align:center;margin-bottom:20px;">
        <h2 style="margin:0;">{avg:.1f}%</h2>
        <p style="margin:5px 0 0;">Overall Attendance Average</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Subject-wise Attendance:**")
    for r in records:
        pct   = r["percentage"]
        color = "#4caf50" if pct >= 75 else "#ff9800" if pct >= 60 else "#f44336"
        label = "✅ Good" if pct >= 75 else "⚠️ Low" if pct >= 60 else "❌ Critical"
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{r['subject']}** — {r['attended_classes']}/{r['total_classes']} classes")
            st.progress(pct / 100)
        with c2:
            st.markdown(
                f"<br><span style='color:{color};font-weight:bold;'>{pct:.1f}% {label}</span>",
                unsafe_allow_html=True
            )
        st.markdown("")

    if any(r["percentage"] < 75 for r in records):
        st.markdown(
            '<div class="alert-warning">⚠️ Your attendance in some subjects is below 75%. '
            'This may affect your gatepass approvals.</div>',
            unsafe_allow_html=True
        )
