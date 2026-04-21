# warehouse_v70.py
import streamlit as st
from ui_components import render_sidebar_controls, show_work_tab, show_report_tab, add_auto_focus

def show_warehouse_tab():
    """
    倉庫端 V70 核心功能
    側邊欄顯示：建立新任務、選擇作業批次、登出系統
    主頁面顯示：入庫作業、數據報表
    """
    # 1. 在側邊欄渲染控制項（建立新任務、選擇批次）
    with st.sidebar:
        current_batch = render_sidebar_controls()
        
        st.divider()
        
        # 登出按鈕（放在選擇作業批次之下）
        if st.button("🚪 登出系統", use_container_width=True, key="warehouse_logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    # 2. 主頁面內容
    if current_batch == "請選擇":
        st.info("👈 請在左側選擇任務開始工作。")
    else:
        # 顯示兩個核心分頁
        tab_work, tab_report = st.tabs(["🚀 入庫作業", "📊 數據報表"])
        
        with tab_work:
            show_work_tab(current_batch)
            
        with tab_report:
            show_report_tab(current_batch)
            
    # 3. 保持自動回焦功能
    add_auto_focus()
