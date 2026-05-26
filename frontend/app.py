# frontend/app.py
# Smart Gatepass System – Streamlit Frontend v2
# Run with: streamlit run app.py

import streamlit as st
import requests as http_requests

# ============================================================
# PAGE CONFIG  (must be first Streamlit call)
# ============================================================
st.set_page_config(
    page_title="Smart Gatepass System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# HIDE STREAMLIT DEFAULT SIDEBAR PAGES
# ============================================================
st.markdown("""
<style>
    /* Page Animation */
    .main {
            animation: fadeIn 0.6s ease-in-out;
    }
   
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);

        }
        to {
            opacity: 1;
            transform: translateY(0);
        
        }
    }

    /* App Background */
    .stApp {
        background: linear-gradient(135deg, #16213e, #3949ab);
    }

    /* Reduce Top Padding */
    .block-container {
        padding-top: 1rem;
    }

    /* Hide automatic Streamlit page navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Modern Header */
    .main-header {
            background: linear-gradient(135deg, #16213e, #3949ab);
            color: white;
            padding: 25px;
            border-radius: 18px;
            margin-bottom: 25px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .main-header h1 {
            margin: 0;
            font-size: 2.6em;
            font-weight: 700;
            letter-spacing: 1px;
            color: #fff8e7 !important;   /* soft cream */
            text-shadow: 2px 2px 10px rgba(0,0,0,0.35);
    }

    .main-header p  {
            margin: 5px 0 0;
            font-size: 1.05em;
            color: #ffe8d6 !important;   /* peach */
            opacity: 1;

    }
    /* =========================================================
            GLOBAL TEXT VISIBILITY FIX
    ========================================================= */
    /* Main headings */
    h1, h2, h3 {
            color: #fff8e7 !important;
    }
            
    /* Dashboard student info */
    h4, h5, h6 {
            color: #ffe8d6 !important;
    }
            
    .stMarkdown strong {
            color: #fff8e7 !important;
    }
            
    /* Normal text */
    label {
            color: #fff8e7;
    }
            
    /* Streamlit markdown text */
    .stMarkdown,
    .stMarkdown p,
    .stMarkdown span,
    .stMarkdown div {
            color: #fff8e7 !important;
    }
            
    /* Login / Signup tabs */
    button[data-baseweb="tab"] {
            color: #ffe8d6 !important;
            font-weight: 600;
    }
            
    /* Form labels */
    label {
            color: #fff0f5 !important;
            font-weight: 500;
    }
    
    /* Radio buttons */
    .stRadio label {
            color: #fff8e7 !important;
    }
            
    /* Selectbox styling */
    .stSelectbox div[data-baseweb="select"] {
            background: white !important;
            border-radius: 10px;
    }
            
    .stSelectbox div[data-baseweb="select"] * {
            color: #1a1a1a !important;
    }
            
    /* Expander headers */
    .streamlit-expanderHeader {
            color: #1a1a1a !important;
            background: #fff8e7 !important;
            border-radius: 10px;
            font-weight: 600;
    }
            
    /* White cards text */
    .info-card,
    .info-card p,
    .info-card span,
    .info-card div {
            color: #1a1a1a !important;
    }
            
    /* Request cards */
    [data-testid="stExpander"] {
            background: rgba(255,255,255,0.96);
            border-radius: 14px;
            border: 1px solid #e0e0e0;
            margin-bottom: 10px;
    }
            
    /* Request details text */
    [data-testid="stExpander"] * {
            color: #1a1a1a !important;
    }
            
    /* Request values visibility */
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stExpander"] div,
    [data-testid="stExpander"] strong {
            color: #1a1a1a !important;
    }
            
    /* Attendance section */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
            color: #fff8e7 !important;
    }
            
    /* Success / warning / info text */
    .alert-success,
    .alert-warning,
    .alert-danger,
    .alert-info {
            font-weight: 500;
    }
            
    /* Sidebar menu text */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
            color: white !important;
    }
        
    /* Fix dark invisible text on white backgrounds */
    div[data-testid="stForm"] p,
    div[data-testid="stForm"] span,
    div[data-testid="stForm"] label {
            color: #1a1a1a !important;
    }
            
    /* Login helper text */
    small {
            color: #ffe8d6 !important;
    }
            
    /* QR section */
    img + div {
            color: #fff8e7 !important;
    }
            

    /* Form Card */
    div[data-testid="stForm"] {
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 18px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            border: 1px solid #f0f0f0;
    }
    /* Buttons */
    .stButton > button {
            background: linear-gradient(135deg, #3949ab, #5c6bc0);
            color: #fff8e7 !important;
            border: none;
            border-radius: 10px;
            height: 50px;
            font-size: 16px;
            font-weight: 600;
            transition: 0.3s ease;
    }
    
    /* Button Hover Animation */
    .stButton > button:hover {
            transform: translateY(-2px);
            background: linear-gradient(135deg, #283593, #3949ab);
            box-shadow: 0 6px 20px rgba(57,73,171,0.4);
    }
    
    /* Input Fields */
    .stTextInput input {
            border-radius: 12px;
            border: 1px solid #dcdcdc;
            padding: 12px;
            color: #1a1a1a !important;
            background: #f9fbff;
            transition: 0.3s ease;
            color: #1e1e1e !important;
    }
    
    /* Input Hover Effect */
    .stTextInput input:hover {
            border: 1px solid #5c6bc0;
    }
            
    .stTextInput input:focus {
            border: 1px solid #3949ab;
            box-shadow: 0 0 8px rgba(57,73,171,0.3);
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e, #16213e);
            border-right: 1px solid rgba(255,255,255,0.08);
    }
            
    /* Sidebar Text */
    section[data-testid="stSidebar"] * {
            color: white !important;
    }
        
    /* Sidebar Radio */
    .stRadio label {
            color: white !important;
            font-size: 15px;
            font-weight: 500;
    }
 
    /* Status badges */
    .badge-pending {
        background:#fff3cd;
        color:#856404;
        padding:3px 10px;
        border-radius:20px;
        font-size:0.8em;
        font-weight:600;
    }

    .badge-approved {
        background:#d4edda;
        color:#155724;
        padding:3px 10px;
        border-radius:20px;
        font-size:0.8em;
        font-weight:600;
    }

    .badge-rejected {
        background:#f8d7da;
        color:#721c24;
        padding:3px 10px;
        border-radius:20px;
        font-size:0.8em;
        font-weight:600;
    }

    .badge-inprogress {
        background:#cce5ff;
        color:#004085;
        padding:3px 10px;
        border-radius:20px;
        font-size:0.8em;
        font-weight:600;
    }

    /* Info cards */
    .info-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-left: 4px solid #3949ab;
            padding: 15px 20px;
            border-radius: 12px;
            margin: 8px 0;
            transition: 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
            
    .info-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    
    /* Stat Boxes */
    .stat-box {
            background: linear-gradient(135deg, #3949ab, #5c6bc0);
            color: white;
            padding: 22px;
            border-radius: 18px;
            text-align: center;
            transition: 0.3s ease;
            box-shadow: 0 10px 30px rgba(0,0,0,0.12);
    }
    
    .stat-box:hover {
            transform: translateY(-5px);
    }

    .stat-box h2 {
        font-size: 2.5em;
        margin: 0;
    }

    .stat-box p {
        margin: 5px 0 0;
        opacity: 0.9;
    }

    /* Alert boxes */
    .alert-success {
        background:#d4edda;
        border:1px solid #c3e6cb;
        color:#155724;
        padding:10px 15px;
        border-radius:8px;
        margin:8px 0;
    }

    .alert-warning {
        background:#fff3cd;
        border:1px solid #ffeeba;
        color:#856404;
        padding:10px 15px;
        border-radius:8px;
        margin:8px 0;
    }

    .alert-danger {
        background:#f8d7da;
        border:1px solid #f5c6cb;
        color:#721c24;
        padding:10px 15px;
        border-radius:8px;
        margin:8px 0;
    }

    .alert-info {
        background:#d1ecf1;
        border:1px solid #bee5eb;
        color:#0c5460;
        padding:10px 15px;
        border-radius:8px;
        margin:8px 0;
    }
        
    /* Streamlit success/info/warning/error messages */
    .stSuccess,
    .stInfo,
    .stWarning,
    .stError {
            color: #1a1a1a !important;
            font-weight: 600;
    }
    .stSuccess * ,
    .stInfo * ,
    .stWarning * ,
    .stError * {
            color: #1a1a1a !important;
    }
    
    /* Activity logs */
    [data-testid="stVerticalBlock"] p,
    [data-testid="stVerticalBlock"] span,
    [data-testid="stVerticalBlock"] li {
            color: #fff8e7 !important;
    }
            
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
            width: 8px;
    }
            
    ::-webkit-scrollbar-track {
            background: #f1f1f1;
    }
            
    ::-webkit-scrollbar-thumb {
            background: #5c6bc0;
            border-radius: 10px;
    }
            
    ::-webkit-scrollbar-thumb:hover {
            background: #3949ab;
    }

</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INIT
# All keys used anywhere in the app are initialised here.
# ============================================================
_defaults = {
    "logged_in":    False,
    "user_id":      None,
    "user_name":    "",
    "user_role":    "",
    "user_email":   "",
    "token":        "",
    "notification": None,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ============================================================
# API BASE URL
# ============================================================
API_URL = "http://localhost:8000"


def api_get(endpoint: str):
    """GET request to backend. Returns parsed JSON or None on error."""
    try:
        r = http_requests.get(f"{API_URL}{endpoint}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def api_post(endpoint: str, data: dict):
    """POST request to backend. Returns (parsed_json, status_code)."""
    try:
        r = http_requests.post(f"{API_URL}{endpoint}", json=data, timeout=5)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500


# ============================================================
# STATUS DISPLAY HELPERS
# Updated for new status values (no is_emergency references)
# ============================================================
STATUS_LABELS = {
    "pending":               "⏳ Pending",
    "approved_by_incharge":  "🔵 Approved by Class Incharge",
    "approved_by_hod":       "🔵 Approved by HOD",
    "approved_by_warden":    "🔵 Approved by Warden",
    "fully_approved":        "✅ Fully Approved",
    "rejected":              "❌ Rejected"
}

STATUS_COLORS = {
    "pending":               "🟡",
    "approved_by_incharge":  "🔵",
    "approved_by_hod":       "🔵",
    "approved_by_warden":    "🔵",
    "fully_approved":        "🟢",
    "rejected":              "🔴"
}


def status_badge(status: str) -> str:
    label = STATUS_LABELS.get(status, status)
    color = STATUS_COLORS.get(status, "⚪")
    return f"{color} {label}"



# ============================================================
# NOTIFICATION DISPLAY (shown once then cleared)
# ============================================================
def show_notification():
    notif = st.session_state.notification
    if notif:
        t = notif["type"]
        m = notif["msg"]
        if t == "success":
            st.markdown(f'<div class="alert-success">✅ {m}</div>', unsafe_allow_html=True)
        elif t == "warning":
            st.markdown(f'<div class="alert-warning">⚠️ {m}</div>', unsafe_allow_html=True)
        elif t == "error":
            st.markdown(f'<div class="alert-danger">❌ {m}</div>', unsafe_allow_html=True)
        elif t == "info":
            st.markdown(f'<div class="alert-info">ℹ️ {m}</div>', unsafe_allow_html=True)
        st.session_state.notification = None


# ============================================================
# IMPORT PAGE MODULES
# ============================================================
from pages.login   import show_login
from pages.student import show_student_dashboard
from pages.teacher import show_teacher_dashboard
from pages.guard   import show_guard_dashboard


# ============================================================
# MAIN ROUTING
# ============================================================
if not st.session_state.logged_in:
    # Show login / signup page (no sidebar needed)
    show_login(api_post)

else:
    # ── Sidebar: user info + logout ───────────────────────────────────────────
    # Each role's page renders its own navigation inside the sidebar BELOW this.
    with st.sidebar:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a237e,#3949ab);
                    color:white;padding:15px;border-radius:10px;margin-bottom:10px;">
            <h4 style="margin:0;">👤 {st.session_state.user_name}</h4>
            <p style="margin:3px 0;opacity:0.8;font-size:0.85em;">
                {st.session_state.user_role.replace('_',' ').title()}
            </p>
            <p style="margin:3px 0;opacity:0.7;font-size:0.78em;">
                {st.session_state.user_email}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")

    # ── Show notification ─────────────────────────────────────────────────────
    show_notification()

    # ── Route to correct dashboard based on role ──────────────────────────────
    role = st.session_state.user_role

    if role == "student":
     show_student_dashboard(api_get, api_post, status_badge)

    elif role in ("incharge", "hod", "warden"):
     show_teacher_dashboard(api_get, api_post, status_badge, role)

    elif role == "guard":
     show_guard_dashboard(api_get, api_post)

    else:
     st.error(f"Unknown role '{role}'. Please contact admin.")
