# frontend/pages/guard.py
# Gate Guard Dashboard
#
# CHANGES:
#   - New sidebar: Scan QR | Mark Exit | Mark Entry | Logout
#   - Removed is_emergency references
#   - Fixed gate action payload (guard_id is now optional)
#   - Fixed status check: uses "fully_approved" (not old values)
#   - QR always fetched fresh from DB via /gate/qr/{id}

import streamlit as st
import base64


def show_guard_dashboard(api_get, api_post):
    st.markdown("""
    <div class="main-header">
        <h1>🚪 Gate Guard Dashboard</h1>
        <p>Verify passes and mark student exit / entry</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar navigation ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 📌 Guard Menu")
        page = st.radio(
            "Navigate",
            [
                "🔍 Scan QR / Search",
                "🚶 Mark Exit",
                "🏠 Mark Entry",
            ],
            label_visibility="collapsed"
        )
        # Logout is rendered in app.py sidebar above this block

    # ── Route ─────────────────────────────────────────────────────────────────
    if page == "🔍 Scan QR / Search":
        show_scan_qr(api_get, api_post)
    elif page == "🚶 Mark Exit":
        show_mark_exit(api_get, api_post)
    elif page == "🏠 Mark Entry":
        show_mark_entry(api_get, api_post)


# ============================================================
# SCAN QR / SEARCH
# Always fetches latest status from DB via /gate/qr/{id}
# ============================================================
def show_scan_qr(api_get, api_post):
    st.markdown("### 🔍 Scan / Search Pass")
    st.info(
        "ℹ️ In production, a QR scanner would decode the Request ID automatically. "
        "Here, enter the Request ID shown on the student's QR pass."
    )

    request_id = st.number_input("Enter Request ID", min_value=1, step=1, value=1)

    if st.button("🔎 Verify Pass", use_container_width=True, type="primary"):
        _show_pass_detail(api_get, api_post, int(request_id))


def _show_pass_detail(api_get, api_post, request_id: int):
    # Always fetch fresh detail from DB
    detail = api_get(f"/requests/{request_id}")
    if not detail:
        st.error("❌ Request not found.")
        return

    status = detail["status"]

    if status != "fully_approved":
        friendly = {
            "pending":              "⏳ Pending (not yet approved)",
            "approved_by_incharge": "🔵 Partially approved (awaiting HOD)",
            "approved_by_hod":      "🔵 Partially approved (awaiting next step)",
            "approved_by_warden":   "🔵 Partially approved (awaiting Class Incharge)",
            "rejected":             "❌ Rejected",
        }.get(status, status)
        st.warning(f"⛔ This pass is NOT valid yet. Status: {friendly}")
        return

    stype = "Day Scholar" if detail["student_type"] == "day_scholar" else "Hosteller"
    sub   = detail.get("request_subtype") or "—"

    st.markdown(f"""
    <div class="info-card">
        <h4>✅ Valid Gatepass — Request #{detail['id']}</h4>
        <p>👤 <strong>{detail['student_name']}</strong>
           | {detail['department']} | Sem {detail['semester']} | {stype}</p>
        <p>📋 <strong>Reason:</strong> {detail['reason']}</p>
        <p>🏷️ <strong>Sub-type:</strong> {sub}</p>
        <p>⏰ <strong>Out:</strong> {detail.get('out_time') or '—'}
           | <strong>In:</strong> {detail.get('in_time') or '—'}</p>
        {"<p>📅 <strong>Departure:</strong> " + str(detail['out_date']) + " | <strong>Return:</strong> " + str(detail['return_date']) + "</p>" if detail.get("out_date") else ""}
        <p>📞 <strong>Parent Phone:</strong> {detail['parent_phone']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch QR fresh from DB (never stale)
    qr_resp = api_get(f"/gate/qr/{request_id}")
    if qr_resp and qr_resp.get("qr_code"):
        col1, col2 = st.columns([1, 1])
        with col1:
            img_bytes = base64.b64decode(qr_resp["qr_code"])
            st.image(img_bytes, caption="Verified QR Pass", width=200)
        with col2:
            st.markdown("**🚪 Gate Actions:**")
            exit_done  = detail.get("exit_marked", False)
            entry_done = detail.get("entry_marked", False)

            if not exit_done:
                if st.button("🚶 Mark EXIT", key=f"exit_scan_{request_id}",
                             use_container_width=True, type="primary"):
                    _do_gate_action(api_post, request_id, "exit", detail["student_name"])
            else:
                st.success(f"✅ Exited at {(detail.get('exit_time') or '')[:16] or 'N/A'}")

            if exit_done and not entry_done:
                if st.button("🏠 Mark ENTRY / Return", key=f"entry_scan_{request_id}",
                             use_container_width=True, type="primary"):
                    _do_gate_action(api_post, request_id, "entry", detail["student_name"])
            elif entry_done:
                st.success(f"✅ Returned at {(detail.get('entry_time') or '')[:16] or 'N/A'}")
            elif not exit_done:
                st.info("Mark Exit first before marking Entry.")
    else:
        st.error("QR code not available for this request.")


# ============================================================
# MARK EXIT
# Lists all fully_approved passes that have NOT been exited yet
# ============================================================
def show_mark_exit(api_get, api_post):
    st.markdown("### 🚶 Mark Exit")

    passes = api_get("/requests/pending/guard")
    if not passes:
        st.info("No fully approved passes at the moment.")
        return

    waiting_exit = [r for r in passes if not r.get("exit_marked")]

    if not waiting_exit:
        st.success("✅ All approved passes have already been exited.")
        return

    st.markdown(f"**{len(waiting_exit)} student(s) yet to exit:**")

    for r in waiting_exit:
        stype = "Day Scholar" if r["student_type"] == "day_scholar" else "Hosteller"
        with st.expander(f"#{r['id']} — {r['student_name']} | {r['department']} | {stype}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Reason:** {r['reason']}")
                st.write(f"**Out Time:** {r.get('out_time') or '—'}")
                st.write(f"**In Time:** {r.get('in_time') or '—'}")
                st.write(f"**Parent Phone:** {r['parent_phone']}")
            with col2:
                if r.get("out_date"):
                    st.write(f"**Departure Date:** {r['out_date']}")
                if r.get("return_date"):
                    st.write(f"**Return Date:** {r['return_date']}")

            if st.button(f"🚶 Mark Exit for #{r['id']}", key=f"exit_list_{r['id']}",
                         type="primary", use_container_width=True):
                _do_gate_action(api_post, r["id"], "exit", r["student_name"])


# ============================================================
# MARK ENTRY
# Lists all fully_approved passes that have exited but NOT yet returned
# ============================================================
def show_mark_entry(api_get, api_post):
    st.markdown("### 🏠 Mark Entry / Return")

    passes = api_get("/requests/pending/guard")
    if not passes:
        st.info("No fully approved passes at the moment.")
        return

    outside = [r for r in passes if r.get("exit_marked") and not r.get("entry_marked")]

    if not outside:
        st.success("✅ No students currently outside campus.")
        return

    st.markdown(f"**{len(outside)} student(s) currently outside campus:**")

    for r in outside:
        stype = "Day Scholar" if r["student_type"] == "day_scholar" else "Hosteller"
        with st.expander(
            f"#{r['id']} — {r['student_name']} | {stype} | "
            f"Exited: {(r.get('exit_time') or '')[:16] or 'N/A'}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Reason:** {r['reason']}")
                st.write(f"**Expected Return:** {r.get('in_time') or r.get('return_time') or '—'}")
                st.write(f"**Parent Phone:** {r['parent_phone']}")
            with col2:
                if r.get("return_date"):
                    st.write(f"**Return Date:** {r['return_date']}")
                st.write(f"**Department:** {r['department']} | Sem {r['semester']}")

            if st.button(f"🏠 Mark Entry for #{r['id']}", key=f"entry_list_{r['id']}",
                         type="primary", use_container_width=True):
                _do_gate_action(api_post, r["id"], "entry", r["student_name"])


# ============================================================
# SHARED HELPER: call gate action API
# guard_id is optional in the backend schema
# ============================================================
def _do_gate_action(api_post, request_id: int, action: str, student_name: str):
    payload = {
        "request_id": request_id,
        "action":     action,
        "guard_id":   st.session_state.get("user_id")  # optional
    }
    result, status = api_post("/gate/action", payload)
    if status == 200:
        word = "exit" if action == "exit" else "entry/return"
        st.session_state.notification = {
            "type": "success",
            "msg":  f"✅ Gate {word} marked for {student_name}."
        }
        st.rerun()
    else:
        st.error(f"❌ {result.get('detail', 'Gate action failed.')}")
