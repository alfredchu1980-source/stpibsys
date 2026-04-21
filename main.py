# main.py
import streamlit as st
import database as db
from config import CONFIG
from ui_components import show_login
from warehouse_v70 import show_warehouse_tab
from client_portal import show_client_portal
from office_admin import show_office_admin
from tv_dashboard import show_tv_dashboard

# 1. 頁面配置
st.set_page_config(page_title=CONFIG["SYSTEM_NAME"], layout="wide")

# 2. 強制護眼模式 (Dark Mode)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    .stTextInput>div>div>input { background-color: #262730 !important; color: white !important; border: 1px solid #4a4a4a !important; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: #0e1117; }
    .stTabs [data-baseweb="tab"] { color: #a0aec0; }
    .stTabs [aria-selected="true"] { color: #63b3ed !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 初始化數據庫
db.init_database()

# 4. 初始化 Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'ui_mode' not in st.session_state: st.session_state.ui_mode = "電腦模式"

if not st.session_state.logged_in:
    show_login()
else:
    # 5. 側邊欄導航
    with st.sidebar:
        st.title(f"🏢 {CONFIG['SYSTEM_NAME']}")
        st.caption(CONFIG["VERSION"])
        st.success(f"👤 登入：{st.session_state.username}")
        
        # 佈局切換按鈕
        st.session_state.ui_mode = st.radio("🖥️ 介面佈局", ["電腦模式", "手機模式"], index=0 if st.session_state.ui_mode == "電腦模式" else 1)
        
        st.divider()
        
        # 功能菜單
        pending_count = db.get_pending_count()
        badge = f"🔴 {pending_count}" if pending_count > 0 else ""
        
        menu = st.radio("功能菜單", [
            "📦 倉庫端 (V70 核心)", 
            f"📩 客戶端預報 {badge}", 
            "🖥️ Office 管理", 
            "📺 電視看板"
        ], label_visibility="collapsed")
        
        st.divider()
        
        if st.button("🚪 登出系統", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # 6. 執行對應模組
    if menu == "📦 倉庫端 (V70 核心)":
        show_warehouse_tab()
    elif menu == f"📩 客戶端預報 {badge}":
        show_client_portal()
    elif menu == "🖥️ Office 管理":
        show_office_admin()
    elif menu == "📺 電視看板":
        show_tv_dashboard()
