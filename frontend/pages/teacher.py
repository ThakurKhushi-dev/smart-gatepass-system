# frontend/pages/teacher.py
# Teacher / Authority Dashboard  (Class Incharge, HOD, Warden)
#
# CHANGES:
#   - New sidebar: Dashboard | Pending Requests | Approved/Rejected | Logs | Logout
#   - Removed all is_emergency / emergency references
#   - Fixed approval payload to use new field names (no is_emergency)
#   - Fixed status filter values for new approval chain
#   - Fixed "next stage" display so teachers see who acts next

import streamlit as st


ROLE_LABELS = {
    "incharge": "Class Incharge",
    "hod":            "HOD",
    "warden":         "Warden"
}

ROLE_ICONS = {
    "incharge": "👩‍🏫",
    "hod":            "🏛️",
    "warden":         "🏠"
}

# Human-readable status labels (no emergency)
STATUS_LABELS = {
    "pending":               "⏳ Pending",
    "approved_by_incharge":  "🔵 Approved by Class Incharge",
    "approved_by_hod":       "🔵 Approved by HOD",
    "approved_by_warden":    "🔵 Approved by Warden",
    "fully_approved":        "✅ Fully Approved",
    "rejected":              "❌ Rejected"
}

STAGE_LABELS = {
    "incharge": "Class Incharge",
    "hod":            "HOD",
    "warden":         "Warden",
    "warden_only":    "Warden",
    "done":           "—",
    "rejected":       "—"
}


def show_teacher_dashboard(api_get, api_post, status_badge, role):
    role_label = ROLE_LABELS.get(role, role)
    role_icon  = ROLE_ICONS.get(role, "👤")

    st.markdown(f"""
    <div class="main-header">
        <h1>{role_icon} {role_label} Dashboard</h1>
        <p>Review and approve student gatepass requests</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar navigation ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### 📌 {role_label} Menu")
        page = st.radio(
            "Navigate",
            [
                "🏠 Dashboard",
                "📬 Pending Requests",
                "📋 Approved / Rejected",
                "📜 Logs",
            ],
            label_visibility="collapsed"
        )
        # Logout is rendered in app.py sidebar above this block

    # ── Route ─────────────────────────────────────────────────────────────────
    if page == "🏠 Dashboard":
        show_dashboard(api_get, role, role_label)
    elif page == "📬 Pending Requests":
        show_pending(api_get, api_post, role, role_label)
    elif page == "📋 Approved / Rejected":
        show_approved_rejected(api_get, status_badge)
    elif page == "📜 Logs":
        show_logs(api_get)


# ============================================================
# DASHBOARD
# ============================================================
def show_dashboard(api_get, role, role_label):
    st.markdown(f"### 🏠 Welcome, {role_label}")

    stats = api_get("/stats")
    if stats:
        col1, col2, col3, col4, col5 = st.columns(5)
        items = [
            ("Total",       stats["total_requests"], "#3949ab"),
            ("Pending",     stats["pending"],        "#f57c00"),
            ("In Progress", stats["in_progress"],    "#0277bd"),
            ("Approved",    stats["approved"],        "#2e7d32"),
            ("Rejected",    stats["rejected"],        "#c62828"),
        ]
        for col, (label, val, color) in zip([col1, col2, col3, col4, col5], items):
            with col:
                st.markdown(
                    f'<div class="stat-box" style="background:linear-gradient(135deg,{color},{color}aa)">'
                    f'<h2>{val}</h2><p>{label}</p></div>',
                    unsafe_allow_html=True
                )

    # How many are waiting for THIS role
    my_pending = api_get(f"/requests/pending/{role}")
    count = len(my_pending) if my_pending else 0
    if count > 0:
        st.markdown(
            f'<div class="alert-warning">⚠️ You have <strong>{count}</strong> request(s) '
            f'waiting for your approval.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="alert-success">✅ No pending requests. You\'re all caught up!</div>',
            unsafe_allow_html=True
        )

    # Approval chain reminder for this role
    st.markdown("---")
    st.markdown("**📋 Approval Chain Reference:**")
    st.markdown("""
    | Student Type | Condition | Chain |
    |---|---|---|
    | Day Scholar | Always | Class Incharge → HOD |
    | Hosteller | Mon–Fri, 9 AM – 2 PM | Warden → Class Incharge → HOD |
    | Hosteller | Outside office hours | Warden only |
    """)


# ============================================================
# PENDING REQUESTS
# ============================================================
def show_pending(api_get, api_post, role, role_label):
    st.markdown("### 📬 Requests Pending Your Approval")

    pending = api_get(f"/requests/pending/{role}")
    if pending is None:
        st.error("⚠️ Could not connect to backend. Make sure the API is running.")
        return

    if not pending:
        st.markdown(
            '<div class="alert-info">✅ No pending requests for you right now.</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown(f"**{len(pending)} request(s) awaiting your review:**")

    for r in pending:
        stype = "Day Scholar" if r["student_type"] == "day_scholar" else "Hosteller"
        subtype_label = r.get("request_subtype", "") or "—"

        with st.expander(
            f"Request #{r['id']} — {r['student_name']} | {r['department']} | {stype}",
            expanded=False
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**👤 Student Info:**")
                st.write(f"**Name:** {r['student_name']}")
                st.write(f"**Email:** {r['student_email']}")
                st.write(f"**Department:** {r['department']}")
                st.write(f"**Semester:** {r['semester']}")
                st.write(f"**Type:** {stype}")
                st.write(f"**Parent Phone:** {r['parent_phone']}")

            with col2:
                st.markdown("**📋 Request Details:**")
                st.write(f"**Reason:** {r['reason']}")
                st.write(f"**Sub-type:** {subtype_label}")
                st.write(f"**Out Time:** {r.get('out_time') or '—'}")
                st.write(f"**In Time:** {r.get('in_time') or '—'}")
                if r.get("out_date"):
                    st.write(f"**Departure Date:** {r['out_date']}")
                if r.get("return_date"):
                    st.write(f"**Return Date:** {r['return_date']}")
                if r.get("return_time"):
                    st.write(f"**Return Time:** {r['return_time']}")
                st.write(f"**Submitted:** {r['created_at'][:16]}")
                st.write(f"**Current Status:** {STATUS_LABELS.get(r['status'], r['status'])}")

            # Student attendance
            st.markdown("---")
            st.markdown("**📊 Student Attendance:**")
            attendance = api_get(f"/attendance/{r.get('student_id', 0)}")
            if attendance:
                cols = st.columns(min(len(attendance), 4))
                for idx, att in enumerate(attendance[:4]):
                    pct   = att["percentage"]
                    color = "#4caf50" if pct >= 75 else "#ff9800" if pct >= 60 else "#f44336"
                    with cols[idx % 4]:
                        st.markdown(f"""
                        <div style="background:#f8f9fa;padding:10px;border-radius:8px;
                                    text-align:center;border-left:3px solid {color};">
                            <strong>{att['subject'][:15]}</strong><br>
                            <span style="color:{color};font-size:1.3em;font-weight:bold;">{pct:.0f}%</span><br>
                            <small>{att['attended_classes']}/{att['total_classes']}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No attendance data available for this student.")

            # Previous approvals on this request
            prev_approvals = api_get(f"/approvals/{r['id']}")
            if prev_approvals:
                st.markdown("---")
                st.markdown("**Previous Approvals:**")
                for a in prev_approvals:
                    icon = "✅" if a["action"] == "approved" else "❌"
                    st.write(
                        f"  {icon} **{a['approver_role'].replace('_',' ').title()}** "
                        f"— {a['approver_name']} ({a['approved_at'][:16]})"
                    )
                    if a.get("comments"):
                        st.caption(f"    Comment: {a['comments']}")

            # Decision section
            st.markdown("---")
            st.markdown("**✍️ Your Decision:**")
            comment = st.text_area(
                "Comments (optional)",
                key=f"comment_{r['id']}",
                placeholder="Add any remarks or reasons…"
            )

            col_approve, col_reject = st.columns(2)

            with col_approve:
                if st.button(f"✅ Approve #{r['id']}", key=f"approve_{r['id']}",
                             use_container_width=True, type="primary"):
                    result, status = api_post("/approvals/action", {
                        "request_id":   r["id"],
                        "approver_id":  st.session_state.user_id,
                        "approver_role": role,
                        "action":       "approved",
                        "comments":     comment
                    })
                    if status == 200:
                        next_stage = result.get("next_stage", "done")
                        next_label = STAGE_LABELS.get(next_stage, next_stage)
                        new_status = result.get("new_status", "")
                        if new_status == "fully_approved":
                            msg = f"Request #{r['id']} is now FULLY APPROVED! QR code generated."
                        else:
                            msg = f"Request #{r['id']} approved. Next: {next_label}"
                        st.session_state.notification = {"type": "success", "msg": msg}
                        st.rerun()
                    else:
                        st.error(f"Error: {result.get('detail', 'Approval failed')}")

            with col_reject:
                if st.button(f"❌ Reject #{r['id']}", key=f"reject_{r['id']}",
                             use_container_width=True):
                    result, status = api_post("/approvals/action", {
                        "request_id":   r["id"],
                        "approver_id":  st.session_state.user_id,
                        "approver_role": role,
                        "action":       "rejected",
                        "comments":     comment
                    })
                    if status == 200:
                        st.session_state.notification = {
                            "type": "error",
                            "msg":  f"Request #{r['id']} has been rejected."
                        }
                        st.rerun()
                    else:
                        st.error(f"Error: {result.get('detail', 'Rejection failed')}")


# ============================================================
# APPROVED / REJECTED
# ============================================================
def show_approved_rejected(api_get, status_badge):
    st.markdown("### 📋 Approved & Rejected Requests")

    all_requests = api_get("/requests/all")
    if not all_requests:
        st.info("No requests found in the system.")
        return

    # Only show completed (approved or rejected)
    done = [r for r in all_requests
            if r["status"] in ("fully_approved", "rejected")]

    if not done:
        st.info("No approved or rejected requests yet.")
        return

    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "fully_approved", "rejected"],
            format_func=lambda x: {
                "All": "All",
                "fully_approved": "✅ Fully Approved",
                "rejected": "❌ Rejected"
            }.get(x, x)
        )
    with col2:
        type_filter = st.selectbox(
            "Filter by Student Type",
            ["All", "day_scholar", "hosteller"],
            format_func=lambda x: {
                "All": "All",
                "day_scholar": "Day Scholar",
                "hosteller": "Hosteller"
            }.get(x, x)
        )

    filtered = done
    if status_filter != "All":
        filtered = [r for r in filtered if r["status"] == status_filter]
    if type_filter != "All":
        filtered = [r for r in filtered if r["student_type"] == type_filter]

    st.markdown(f"Showing **{len(filtered)}** of {len(done)} completed requests")

    for r in filtered:
        stype = "Day Scholar" if r["student_type"] == "day_scholar" else "Hosteller"
        with st.expander(f"#{r['id']} | {r['student_name']} | {stype} | {status_badge(r['status'])}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Student:** {r['student_name']} ({r['student_email']})")
                st.write(f"**Dept / Sem:** {r['department']} / Sem {r['semester']}")
                st.write(f"**Reason:** {r['reason']}")
                st.write(f"**Parent Phone:** {r['parent_phone']}")
            with col2:
                st.write(f"**Type:** {stype}")
                sub = r.get("request_subtype", "") or "—"
                st.write(f"**Sub-type:** {sub}")
                st.write(f"**Out Time:** {r.get('out_time') or '—'}")
                st.write(f"**In Time:** {r.get('in_time') or '—'}")
                if r.get("out_date"):
                    st.write(f"**Departure Date:** {r['out_date']}")
                if r.get("return_date"):
                    st.write(f"**Return Date:** {r['return_date']}")
                st.write(f"**Submitted:** {r['created_at'][:16]}")

            approvals = api_get(f"/approvals/{r['id']}")
            if approvals:
                st.markdown("**Approval Chain:**")
                for a in approvals:
                    icon = "✅" if a["action"] == "approved" else "❌"
                    st.write(
                        f"  {icon} **{a['approver_role'].replace('_',' ').title()}** "
                        f"— {a['approver_name']} ({a['approved_at'][:16]})"
                    )
                    if a.get("comments"):
                        st.caption(f"    {a['comments']}")


# ============================================================
# LOGS
# ============================================================
def show_logs(api_get):
    st.markdown("### 📜 Activity Logs")

    logs = api_get("/logs?limit=100")
    if not logs:
        st.info("No logs available yet.")
        return

    icon_map = {
        "LOGIN":             "🔑",
        "REGISTER":          "📝",
        "REQUEST_CREATED":   "📋",
        "REQUEST_APPROVED":  "✅",
        "REQUEST_REJECTED":  "❌",
        "GATE_EXIT":         "🚪",
        "GATE_ENTRY":        "🏠"
    }

    for log in logs:
        icon = icon_map.get(log["action"], "📝")
        st.markdown(f"""
        <div style="background:#f8f9fa;padding:8px 12px;border-radius:6px;
                    margin:4px 0;border-left:3px solid #3949ab;font-size:0.9em;">
            {icon} <strong>{log['action']}</strong>
            — {log.get('details', '')}
            <span style="color:#888;float:right;">{str(log['logged_at'])[:16]}</span>
        </div>
        """, unsafe_allow_html=True)
