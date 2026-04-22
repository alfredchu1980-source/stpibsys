# main.py
import streamlit as st
import database as db
from config import CONFIG
from ui_components import show_login
from warehouse_v70 import show_warehouse_tab
from client_portal import show_client_portal
from office_admin import show_office_admin
from tv_dashboard import show_tv_dashboard
from datetime import datetime, timedelta

st.set_page_config(page_title=CONFIG["SYSTEM_NAME"], layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    .stTextInput>div>div>input { background-color: #262730 !important; color: white !important; border: 1px solid #4a4a4a !important; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    </style>
    """, unsafe_allow_html=True)

db.init_database()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'ui_mode' not in st.session_state: st.session_state.ui_mode = "電腦模式"
if 'login_time' not in st.session_state: st.session_state.login_time = None

if st.session_state.logged_in and st.session_state.login_time:
    elapsed = datetime.now() - st.session_state.login_time
    if elapsed > timedelta(minutes=30):
        st.warning("⚠️ 登入已逾時，請重新登入")
        st.session_state.logged_in = False
        st.session_state.login_time = None
        st.rerun()

if not st.session_state.logged_in:
    show_login()
else:
    with st.sidebar:
        st.title(f"🏢 {CONFIG['SYSTEM_NAME']}")
        st.caption(CONFIG["VERSION"])
        st.success(f"👤 登入：{st.session_state.username}")
        
        if st.session_state.login_time:
            st.caption(f"登入時間：{st.session_state.login_time.strftime('%H:%M:%S')}")
        
        st.divider()
        
        user_role = st.session_state.role
        
        if user_role == "Admin":
            pending_count = db.get_pending_count()
            badge = f"🔴 {pending_count}" if pending_count > 0 else ""
            menu = st.radio("功能菜單", [
                "📦 倉庫端 (V70 核心)", 
                f"📩 客戶端預報 {badge}", 
                "🖥️ Office 管理", 
                "📺 電視看板"
            ], label_visibility="collapsed")
        elif user_role == "Customer":
            pending_count = db.get_pending_count()
            badge = f"🔴 {pending_count}" if pending_count > 0 else ""
            menu = st.radio("功能菜單", [
                f"📩 客戶端預報 {badge}"
            ], label_visibility="collapsed")
        else:
            menu = st.radio("功能菜單", [
                "📦 倉庫端 (V70 核心)"
            ], label_visibility="collapsed")
        
        st.divider()
        
        st.session_state.ui_mode = st.radio("🖥️ 介面佈局", ["電腦模式", "手機模式"], index=0 if st.session_state.ui_mode == "電腦模式" else 1)
        
        st.divider()
        
        from ui_components import render_user_management
        render_user_management()
        
        # 注意：登出按鈕已移至 warehouse_v70.py（僅倉庫端需要）

    if menu == "📦 倉庫端 (V70 核心)":
        show_warehouse_tab()
    elif menu == f"📩 客戶端預報 {badge}":
        show_client_portal()
    elif menu == "🖥️ Office 管理":
        show_office_admin()
    elif menu == "📺 電視看板":
        show_tv_dashboard()
