# client_portal.py
import streamlit as st
import pandas as pd
from datetime import datetime
from config import CONFIG
import database as db
from utils import write_audit_log
import services

def show_client_portal():
    """客戶端預報頁面 - 溫度選擇按鈕固定在底部"""
    st.title("📩 客戶端預報")
    
    pending_count = db.get_pending_count()
    if pending_count > 0:
        st.warning(f"🔴 您有 {pending_count} 筆待審核的預報")
    
    st.markdown("### 📝 建立新預報")
    
    cust_name = st.text_input("🏢 客戶名稱", key="client_cust_name").strip().upper()
    new_batch_id = st.text_input("新任務編號", placeholder="例如：JOB-001", key="client_batch_id").strip()
    
    # 溫度類型選擇（決定樓層）
    temp_type = st.radio(
        "🌡️ 儲存溫度類型",
        ["Ambient (常溫)", "Chilled or Frozen (冷凍或冷藏)"],
        key="client_temp_type",
        help="常溫→5F, 冷凍/冷藏→3F",
        horizontal=True
    )
    
    # 根據溫度類型自動分配樓層
    if "Ambient" in temp_type:
        batch_floor = "5F"
        st.info("📍 將分配至 **5F**（常溫倉）☀️")
    else:
        batch_floor = "3F"
        st.info("📍 將分配至 **3F**（冷凍/冷藏倉）🌡️")
    
    uploaded_file = st.file_uploader("上傳 Excel", type=["xlsx"], key="client_uploader")
    
    # 提交按鈕固定在頁面底部
    st.divider()
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)  # 間距
    
    col1, col2 = st.columns([3, 1])
    with col1:
        submit_btn = st.button("📤 提交預報", use_container_width=True, type="primary", key="client_submit_btn")
    with col2:
        reset_btn = st.button("🔄 重置表單", use_container_width=True, key="client_reset_btn")
    
    if reset_btn:
        st.rerun()
    
    if submit_btn:
        if not new_batch_id:
            st.error("❌ 請輸入任務編號")
        elif not uploaded_file:
            st.error("❌ 請上傳 Excel 檔案")
        else:
            success, msg = services.process_excel_upload(uploaded_file, new_batch_id, cust_name, batch_floor, "")
            if success:
                db.create_batch(new_batch_id, cust_name, status="pending", source="Client", floor=batch_floor)
                st.success(f"✅ 預報提交成功！等待 Office 審核。（樓層：{batch_floor}）")
                write_audit_log(st.session_state.username, f"提交預報：{new_batch_id}", f"Client, Floor: {batch_floor}")
                st.rerun()
            else:
                st.error(f"❌ 提交失敗：{msg}")
    
    st.divider()
    
    st.markdown("### 📋 我的預報記錄")
    all_batches = db.get_batches_by_status(["pending", "Active", "completed"])
    if all_batches.empty:
        st.info("尚無預報記錄")
    else:
        display_df = all_batches[['batch_id', 'customer_name', 'status', 'floor', 'created_at']].copy()
        display_df.columns = ['任務編號', '客戶名稱', '狀態', '樓層', '建立時間']
        st.dataframe(display_df, use_container_width=True)
