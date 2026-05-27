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
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #312e81 100%);
    }

    /* Reduce Top Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* Hide automatic Streamlit page navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }

    /* Modern Header */
    .main-header {
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(10px);
            color: white;
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 25px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.18);
            border: 1px solid rgba(255,255,255,0.08);
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

/* Small headings */
h4, h5, h6 {
    color: #ffe8d6 !important;
}

/* Normal markdown on dark background */
.stMarkdown,
.stMarkdown p,
.stMarkdown span,
.stMarkdown div {
    color: #f8fafc !important;
}

/* Strong text on dark sections */
.stMarkdown strong {
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

/* =========================================================
        WHITE CARD TEXT FIX
========================================================= */

/* White info cards */
.info-card {
    color: #1f2937 !important;
}

/* All normal text inside white cards */
.info-card p,
.info-card span,
.info-card div {
    color: #1f2937 !important;
}

/* Headings inside white cards */
.info-card strong,
.info-card b {
    color: #111827 !important;
    font-weight: 700 !important;
}

/* Guard section headings fix */
.info-card strong {
    color: #111827 !important;
}

/* =========================================================
        SUBMITTING AS FIX
========================================================= */

/* Alert info box */
.alert-info {
    color: #0f172a !important;
    font-weight: 600;
}

/* Text inside alert info */
.alert-info p,
.alert-info span,
.alert-info div {
    color: #0f172a !important;
}

/* Important text like student name + hosteller */
.alert-info strong,
.alert-info b {
    color: #083344 !important;
    font-weight: 700 !important;
}

/* =========================================================
        REQUEST / EXPANDER CARDS
========================================================= */

[data-testid="stExpander"] {
    background: #ffffff !important;
    border-radius: 14px;
    border: none;
    margin-bottom: 14px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

/* Expander content text */
[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] div,
[data-testid="stExpander"] strong {
    color: #1a1a1a !important;
}

/* Expander header */
.streamlit-expanderHeader {
    background: #ffffff !important;
    color: #111827 !important;
    font-weight: 600;
    border-radius: 14px;
    padding: 12px 16px;
}

/* =========================================================
        ACTIVITY LOGS FIX
========================================================= */

.log-entry {
    background: rgba(255,255,255,0.08);
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;

    color: #f8fafc !important;
    font-weight: 500;
}

/* LOGIN heading visible */
.log-entry strong,
.log-entry b {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Remaining log text */
.log-entry span,
.log-entry div,
.log-entry p {
    color: #f8fafc !important;
}

/* =========================================================
        ATTENDANCE FIX
========================================================= */

/* Subject names */
div[data-testid="stVerticalBlock"] strong {
    color: #fff8e7 !important;
}

/* 35/40 classes text */
div[data-testid="stVerticalBlock"] p,
div[data-testid="stVerticalBlock"] span {
    color: #f8fafc !important;
}

/* Attendance metric labels */
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #fff8e7 !important;
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
 

/* Light text on dark/blue sections */
.main-header *,
.stat-box *,
section[data-testid="stSidebar"] *,
[data-testid="stAlert"] * {
    color: #fff8e7 !important;
}

         
    /* Selectbox styling */
    .stSelectbox div[data-baseweb="select"] {
            background: #ffffff !important;
            border-radius: 12px;
            border: 1px solid #d1d5db;
            color: #1e293b !important;
        }
            
    .stSelectbox div[data-baseweb="select"] * {
            color: #1e293b !important;
    }
    /* Radio button text */
    .stRadio > div {
            background: rgba(255,255,255,0.06);
            padding: 10px;
            border-radius: 12px;
    }

    .stRadio label,
    .stRadio p,
    .stRadio span {
            color: #ffffff !important;
            font-weight: 500;
    }
    /* Expander headers */
    .streamlit-expanderHeader {
            background: #ffffff !important;
            color: #1e293b !important;
            font-weight: 600;
            border-radius: 14px;
            padding: 12px 16px;
        }
        /* Expander title text fix */
        .streamlit-expanderHeader p,
        .streamlit-expanderHeader span,
        .streamlit-expanderHeader div {
            color: #111827 !important;
            font-weight: 600;
        }
 /* White cards text */
.info-card,
.info-card p,
.info-card span,
.info-card div,
.info-card label {
    color: #1f2937 !important;
}

/* White card headings */
.info-card strong,
.info-card b {
    color: #111827 !important;
    font-weight: 700 !important;
}

/* Alert info box text */
.alert-info,
.alert-info p,
.alert-info span,
.alert-info div {
    color: #0c5460 !important;
}

/* "Submitting as" heading */
.alert-info strong,
.alert-info b {
    color: #083344 !important;
    font-weight: 700 !important;
}
  /* Activity logs */
.log-entry {
    background: rgba(255,255,255,0.08);
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;

    color: #f8fafc !important;
    font-weight: 500;
}

/* LOGIN heading visibility */
.log-entry strong,
.log-entry b {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Remaining activity text */
.log-entry span,
.log-entry div,
.log-entry p {
    color: #f8fafc !important;
}

/* Teacher/HOD/Warden activity log cards */
.activity-log-item {
    background: #ffffff !important;
    border-left: 3px solid #3949ab !important;
    border-radius: 6px;
    margin: 4px 0;
    padding: 8px 12px;
    font-size: 0.9em;
    color: #1f2937 !important;
}

.activity-log-item,
.activity-log-item p,
.activity-log-item span,
.activity-log-item div {
    color: #1f2937 !important;
}

.activity-log-item strong,
.activity-log-item b {
    color: #111827 !important;
    font-weight: 700 !important;
}

.activity-log-item .log-time {
    color: #6b7280 !important;
    float: right;
}
    /* Request cards */
    [data-testid="stExpander"] {
            background: #ffffff !important;
            border-radius: 14px;
            border: none;
            margin-bottom: 14px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
            
    /* Request details text */
    [data-testid="stExpander"] * {
            color: #1e293b !important;
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
            /* Attendance classes visibility */
.stProgress + div,
.stProgress + div p,
.stProgress + div span,
.stProgress + div strong {
    color: #ffffff !important;
    font-weight: 500 !important;
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
            /* Tables */
table {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* Table text */
table th {
    background: rgba(255,255,255,0.12) !important;
    color: #fff8e7 !important;
    font-weight: 700 !important;
}

table td {
    color: #f8fafc !important;
    font-weight: 500 !important;
}



/* Subject names */
div[data-testid="stVerticalBlock"] strong {
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
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            color: white !important;
            border: none;
            border-radius: 12px;
            height: 48px;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
    
    /* Button Hover Animation */
    .stButton > button:hover {
            transform: translateY(-2px);
            background: linear-gradient(135deg, #1d4ed8, #2563eb);
            box-shadow: 0 6px 20px rgba(37,99,235,0.35);
    }
    
    /* Input Fields */
    .stTextInput input {
            border-radius: 12px;
            border: 1px solid #d1d5db;
            padding: 12px;
            color: #1e293b !important;
            background: #ffffff;
            transition: 0.3s ease;
            font-weight: 500;
        }
            
        textarea,
        input {
            color: #1e293b !important;
            font-weight: 500;
        }

        textarea::placeholder,
        input::placeholder {
            color: #6b7280 !important;
        }
        
        /* Textarea styling */
        textarea {
            border-radius: 12px !important;
            border: 1px solid #d1d5db !important;
            background: white !important;
            color: #111827 !important;
            padding: 12px !important;
        }

        textarea:focus {
            border: 1px solid #2563eb !important;
            box-shadow: 0 0 8px rgba(37,99,235,0.3) !important;
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
            background: linear-gradient(
            180deg,
            rgba(15,23,42,0.98),
            rgba(30,58,138,0.95));
            backdrop-filter: blur(14px);
            border-right: 1px solid rgba(255,255,255,0.08);
            box-shadow: 4px 0 20px rgba(0,0,0,0.25);
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
        opacity: 1;
            color: #ffffff !important;
            font-weight: 500;
    }
    /* Demo Accounts / Streamlit Info Box */
    [data-testid="stAlert"] {
            background: rgba(37,99,235,0.18) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 16px !important;
            padding: 16px !important;
            backdrop-filter: blur(10px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    }
    /* Demo box text */
    [data-testid="stAlert"] * {
            color: #ffffff !important;
            font-weight: 500 !important;
    }

    /* Info icon color */
    [data-testid="stAlert"] svg {
            fill: #ffffff !important;
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
    /* Info messages text */
    .alert-info,
    .alert-info * {
            color: #0f172a !important;
            font-weight: 600;
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

    /* =========================================================
       TEXT VISIBILITY OVERRIDES – FINAL (light surface fixes)
    ========================================================= */

    /* ── Expander headers (Request #9, #11 | Ruby | ... ✅ Fully Approved) ── */
    [data-testid="stExpander"] details > summary,
    [data-testid="stExpander"] details > summary *,
    .stMarkdown [data-testid="stExpander"] details > summary,
    .stMarkdown [data-testid="stExpander"] details > summary * {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* ── Expander body text ── */
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] div,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] strong,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] label,
    [data-testid="stExpander"] [data-testid="stVerticalBlock"] p,
    [data-testid="stExpander"] [data-testid="stVerticalBlock"] span,
    [data-testid="stExpander"] [data-testid="stVerticalBlock"] strong,
    [data-testid="stExpander"] [data-testid="stVerticalBlock"] label {
        color: #1a1a1a !important;
        -webkit-text-fill-color: #1a1a1a !important;
    }

    /* ── White info cards (.info-card) ── */
    div.info-card,
    div.info-card p,
    div.info-card span,
    div.info-card div,
    div.info-card strong,
    div.info-card b,
    div.info-card h4,
    div.info-card h5 {
        color: #1f2937 !important;
        -webkit-text-fill-color: #1f2937 !important;
    }

    /* ── Alert success (Welcome back / No pending) ── */
    div.alert-success,
    div.alert-success p,
    div.alert-success span,
    div.alert-success div,
    div.alert-success strong,
    div.alert-success b {
        color: #155724 !important;
        -webkit-text-fill-color: #155724 !important;
    }

    /* ── Alert warning (You have N request(s) waiting) ── */
    div.alert-warning,
    div.alert-warning p,
    div.alert-warning span,
    div.alert-warning div,
    div.alert-warning strong,
    div.alert-warning b {
        color: #856404 !important;
        -webkit-text-fill-color: #856404 !important;
    }

    /* ── Alert info (Submitting as / No pending for you) ── */
    div.alert-info, 
    div.alert-info p,
    div.alert-info span,
    div.alert-info div,
    div.alert-info strong,
    div.alert-info b {
        color: #0c5460 !important;
        -webkit-text-fill-color: #0c5460 !important;
    }

    /* ── Alert danger ── */
    div.alert-danger,
    div.alert-danger p,
    div.alert-danger span,
    div.alert-danger div,
    div.alert-danger strong,
    div.alert-danger b {
        color: #721c24 !important;
        -webkit-text-fill-color: #721c24 !important;
    }

    /* ── Activity log cards (.activity-log-item class) ── */
    div.activity-log-item,
    div.activity-log-item p,
    div.activity-log-item span,
    div.activity-log-item div {
        color: #1f2937 !important;
        -webkit-text-fill-color: #1f2937 !important;
    }
    div.activity-log-item strong,
    div.activity-log-item b {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 700 !important;
    }
    div.activity-log-item span.log-time {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
    }

    /* ── Activity log cards (inline style – background:#f8f9fa) ── */
    div[style*="background:#f8f9fa"],
    div[style*="background: #f8f9fa"] {
        color: #1f2937 !important;
        -webkit-text-fill-color: #1f2937 !important;
    }
    div[style*="background:#f8f9fa"] strong,
    div[style*="background: #f8f9fa"] strong,
    div[style*="background:#f8f9fa"] b,
    div[style*="background: #f8f9fa"] b {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 700 !important;
    }
    div[style*="background:#f8f9fa"] span,
    div[style*="background: #f8f9fa"] span {
        color: #374151 !important;
        -webkit-text-fill-color: #374151 !important;
    }

    /* ── Activity logs: stronger selectors (force against global .stMarkdown text) ── */
    .stMarkdown div[style*="background:#f8f9fa"],
    .stMarkdown div[style*="background: #f8f9fa"],
    .stMarkdown div[style*="border-left:3px solid #3949ab"],
    .stMarkdown div[style*="border-left: 3px solid #3949ab"] {
        color: #1f2937 !important;
        -webkit-text-fill-color: #1f2937 !important;
    }

    .stMarkdown div[style*="background:#f8f9fa"] strong,
    .stMarkdown div[style*="background: #f8f9fa"] strong,
    .stMarkdown div[style*="border-left:3px solid #3949ab"] strong,
    .stMarkdown div[style*="border-left: 3px solid #3949ab"] strong,
    .stMarkdown div[style*="background:#f8f9fa"] b,
    .stMarkdown div[style*="background: #f8f9fa"] b {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 700 !important;
    }

    .stMarkdown div[style*="background:#f8f9fa"] span,
    .stMarkdown div[style*="background: #f8f9fa"] span,
    .stMarkdown div[style*="border-left:3px solid #3949ab"] span,
    .stMarkdown div[style*="border-left: 3px solid #3949ab"] span {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
    }

    /* ===== Strongest final override (activity logs only) ===== */
    /* Defeat: .stMarkdown div { color: #f8fafc !important; } */
    .stMarkdown div.activity-log-item,
    .stMarkdown div.activity-log-item *,
    .stMarkdown div[style*="background:#f8f9fa"],
    .stMarkdown div[style*="background:#f8f9fa"] *,
    .stMarkdown div[style*="background: #f8f9fa"],
    .stMarkdown div[style*="background: #f8f9fa"] * {
        color: #1f2937 !important;
        -webkit-text-fill-color: #1f2937 !important;
    }

    .stMarkdown div.activity-log-item strong,
    .stMarkdown div.activity-log-item b,
    .stMarkdown div[style*="background:#f8f9fa"] strong,
    .stMarkdown div[style*="background:#f8f9fa"] b,
    .stMarkdown div[style*="background: #f8f9fa"] strong,
    .stMarkdown div[style*="background: #f8f9fa"] b {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 700 !important;
    }

    .stMarkdown div.activity-log-item span,
    .stMarkdown div[style*="background:#f8f9fa"] span,
    .stMarkdown div[style*="background: #f8f9fa"] span {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
    }

    /* ===== Activity logs fallback: match by inline-style patterns ===== */
    /* Matches current teacher logs markup even if background hex changes */
    .stMarkdown div[style*="border-left"],
    .stMarkdown div[style*="border-left"] *,
    .stMarkdown div[style*="font-size:0.9em"],
    .stMarkdown div[style*="font-size:0.9em"] *,
    .stMarkdown div[style*="padding:8px 12px"],
    .stMarkdown div[style*="padding:8px 12px"] * {
        color: #1f2937 !important;
        -webkit-text-fill-color: #1f2937 !important;
    }

    .stMarkdown div[style*="border-left"] strong,
    .stMarkdown div[style*="font-size:0.9em"] strong,
    .stMarkdown div[style*="padding:8px 12px"] strong,
    .stMarkdown div[style*="border-left"] b,
    .stMarkdown div[style*="font-size:0.9em"] b,
    .stMarkdown div[style*="padding:8px 12px"] b {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 700 !important;
    }

    .stMarkdown div[style*="border-left"] span,
    .stMarkdown div[style*="font-size:0.9em"] span,
    .stMarkdown div[style*="padding:8px 12px"] span {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
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
