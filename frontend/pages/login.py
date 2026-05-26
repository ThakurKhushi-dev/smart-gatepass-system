# frontend/pages/login.py
# Login + Sign Up page

import streamlit as st


def show_login(api_post):

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Smart Gatepass System</h1>
        <p>College Campus Exit &amp; Entry Management</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        # ── Tabs ─────────────────────────────────────────────────────────────
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

        # ══════════════════════════════════════════════════════════════════════
        # LOGIN TAB
        # ══════════════════════════════════════════════════════════════════════
        with tab_login:

            st.markdown("#### Login to Your Account")

            st.caption(
                "Students: use your registered email. "
                "Authorities: use demo credentials below."
            )

            # ── Login Form ────────────────────────────────────────────────
            with st.form("login_form"):

                email = st.text_input(
                    "📧 Email Address",
                    placeholder="Enter your email"
                )

                password = st.text_input(
                    "🔒 Password",
                    type="password",
                    placeholder="Enter your password"
                )

                submitted = st.form_submit_button(
                    "Login →",
                    use_container_width=True,
                    type="primary"
                )

                if submitted:

                    if not email or not password:
                        st.error("Please enter both email and password.")

                    else:

                        result, status = api_post(
                            "/auth/login",
                            {
                                "email": email,
                                "password": password
                            }
                        )

                        if status == 200:

                            st.session_state.logged_in = True
                            st.session_state.user_id = result["user_id"]
                            st.session_state.user_name = result["name"]
                            st.session_state.user_role = result["role"]
                            st.session_state.user_email = result["email"]
                            st.session_state.token = result["token"]

                            st.session_state.notification = {
                                "type": "success",
                                "msg": f"Welcome back, {result['name']}!"
                            }

                            st.rerun()

                        else:
                            st.error(
                                f"❌ {result.get('detail', 'Login failed. Please check your credentials.')}"
                            )

            # ── Demo Authority Accounts ─────────────────────────────────
            st.markdown("---")
            st.markdown("### 🛡️ Demo Authority Accounts")

            col_a, col_b = st.columns(2)

            with col_a:

                st.info("""
👨‍🏫 **Class Incharge**  
📧 incharge@gatepass.com  
🔑 123456
""")

                st.info("""
🏢 **HOD**  
📧 hod@gatepass.com  
🔑 123456
""")

            with col_b:

                st.info("""
🏠 **Warden**  
📧 warden@gatepass.com  
🔑 123456
""")

                st.info("""
🚔 **Guard**  
📧 guard@gatepass.com  
🔑 123456
""")

        # ══════════════════════════════════════════════════════════════════════
        # SIGN UP TAB
        # ══════════════════════════════════════════════════════════════════════
        with tab_signup:

            st.markdown("#### Student Registration")

            st.caption(
                "Only students can self-register. "
                "Authority accounts are managed by admin."
            )

            with st.form("signup_form", clear_on_submit=False):

                # ── Basic Info ────────────────────────────────────────────
                su_name = st.text_input(
                    "👤 Full Name *",
                    placeholder="e.g. Rahul Sharma"
                )

                su_email = st.text_input(
                    "📧 Email Address *",
                    placeholder="e.g. rahul@student.com"
                )

                col_pw1, col_pw2 = st.columns(2)

                with col_pw1:
                    su_password = st.text_input(
                        "🔒 Password *",
                        type="password",
                        placeholder="Min 6 characters"
                    )

                with col_pw2:
                    su_confirm = st.text_input(
                        "🔒 Confirm Password *",
                        type="password",
                        placeholder="Repeat password"
                    )

                st.markdown("---")

                # ── Academic Info ────────────────────────────────────────
                col_d, col_s = st.columns(2)

                with col_d:

                    su_department = st.selectbox(
                        "🏢 Department *",
                        [
                            "Computer Science",
                            "Information Technology",
                            "Electronics",
                            "Electrical",
                            "Mechanical",
                            "Civil",
                            "Other"
                        ]
                    )

                with col_s:

                    su_semester = st.selectbox(
                        "📚 Semester *",
                        [1, 2, 3, 4, 5, 6, 7, 8],
                        format_func=lambda x: f"Semester {x}"
                    )

                su_type = st.radio(
                    "🏠 Student Type *",
                    ["Day Scholar", "Hosteller"],
                    horizontal=True
                )

                su_phone = st.text_input(
                    "📞 Phone Number (optional)",
                    placeholder="+91 XXXXXXXXXX"
                )

                st.markdown("---")

                signup_submitted = st.form_submit_button(
                    "Create Account →",
                    use_container_width=True,
                    type="primary"
                )

                if signup_submitted:

                    errors = []

                    if not su_name.strip():
                        errors.append("Full Name is required")

                    if not su_email.strip():
                        errors.append("Email is required")

                    if not su_password:
                        errors.append("Password is required")

                    elif len(su_password) < 6:
                        errors.append("Password must be at least 6 characters")

                    if su_password != su_confirm:
                        errors.append("Passwords do not match")

                    if errors:

                        for e in errors:
                            st.error(f"❌ {e}")

                    else:

                        type_map = {
                            "Day Scholar": "day_scholar",
                            "Hosteller": "hosteller"
                        }

                        payload = {
                            "name": su_name.strip(),
                            "email": su_email.strip(),
                            "password": su_password,
                            "role": "student",
                            "department": su_department,
                            "semester": int(su_semester),
                            "student_type": type_map[su_type],
                            "phone": su_phone.strip() if su_phone.strip() else None
                        }

                        result, status = api_post(
                            "/auth/register",
                            payload
                        )

                        if status == 200:

                            st.session_state.logged_in = True
                            st.session_state.user_id = result["id"]
                            st.session_state.user_name = result["name"]
                            st.session_state.user_role = result["role"]
                            st.session_state.user_email = result["email"]

                            # Auto login after signup
                            login_result, login_status = api_post(
                                "/auth/login",
                                {
                                    "email": su_email.strip(),
                                    "password": su_password
                                }
                            )

                            if login_status == 200:
                                st.session_state.token = login_result["token"]

                            st.session_state.notification = {
                                "type": "success",
                                "msg": f"Account created! Welcome, {result['name']}!"
                            }

                            st.rerun()

                        else:
                            st.error(
                                f"❌ {result.get('detail', 'Registration failed. Please try again.')}"
                            )