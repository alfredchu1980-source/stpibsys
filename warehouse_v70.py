# warehouse_v70.py
import streamlit as st
from ui_components import render_sidebar_controls, show_work_tab, show_report_tab, add_auto_focus

def show_warehouse_tab():
    """倉庫端 V70 核心功能 - 登出按鈕在選擇作業批次之下"""
    with st.sidebar:
        current_batch = render_sidebar_controls()
        
        # 登出按鈕 - 直接在選擇作業批次之下
        st.divider()
        if st.button("🚪 登出系統", use_container_width=True, key="warehouse_logout"):
            st.session_state.logged_in = False
            st.session_state.login_time = None
            st.rerun()
    
    if current_batch == "請選擇":
        st.info("👈 請在左側選擇任務開始工作。")
    else:
        tab_work, tab_report = st.tabs(["🚀 入庫作業", "📊 數據報表"])
        with tab_work:
            show_work_tab(current_batch)
        with tab_report:
            show_report_tab(current_batch)
    add_auto_focus()
