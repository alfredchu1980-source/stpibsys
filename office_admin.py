# office_admin.py
"""
秘書台管理頁面
功能：
1. 已完成批次列表
2. 未完成批次列表
3. 用戶賬戶管理（建立賬戶、設置密碼和角色）
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from config import CONFIG
import database as db
from utils import write_audit_log

def show_office_admin():
    """秘書台管理頁面"""
    st.title("📋 秘書台")
    
    if st.session_state.role != "Admin":
        st.error("❌ 只有 Admin 可以訪問此頁面")
        return
    
    # ============================================
    # 1. 已完成批次列表
    # ============================================
    st.markdown("### ✅ 已完成批次")
    
    completed_batches = db.get_batches_by_status(["completed"])
    
    if completed_batches.empty:
        st.info("目前沒有已完成批次")
    else:
        # 按照指定順序顯示欄位：batch_id / customer_name / created_at / done_at / floor / status
        display_completed = completed_batches.copy()
        
        # 確保欄位存在（done_at 可能不存在，需要處理）
        if 'done_at' not in display_completed.columns:
            display_completed['done_at'] = 'N/A'
        
        # 選擇並排序欄位
        display_cols = ['batch_id', 'customer_name', 'created_at', 'done_at', 'floor', 'status']
        available_cols = [col for col in display_cols if col in display_completed.columns]
        
        # 重命名欄位以顯示中文
        column_names = {
            'batch_id': '批次編號',
            'customer_name': '客戶名稱',
            'created_at': '建立時間',
            'done_at': '完成時間',
            'floor': '樓層',
            'status': '狀態'
        }
        
        display_df = display_completed[available_cols].copy()
        display_df.columns = [column_names.get(col, col) for col in display_df.columns]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # ============================================
    # 2. 未完成批次列表
    # ============================================
    st.markdown("### 🔄 未完成批次")
    
    # 未完成 = Active + pending
    incomplete_batches = db.get_batches_by_status(["Active", "pending"])
    
    if incomplete_batches.empty:
        st.info("目前沒有未完成批次")
    else:
        # 按照指定順序顯示欄位：batch_id / customer_name / created_at / done_at / floor / status
        display_incomplete = incomplete_batches.copy()
        
        # 確保欄位存在（done_at 可能不存在，需要處理）
        if 'done_at' not in display_incomplete.columns:
            display_incomplete['done_at'] = '進行中'
        
        # 選擇並排序欄位
        display_cols = ['batch_id', 'customer_name', 'created_at', 'done_at', 'floor', 'status']
        available_cols = [col for col in display_cols if col in display_incomplete.columns]
        
        # 重命名欄位以顯示中文
        column_names = {
            'batch_id': '批次編號',
            'customer_name': '客戶名稱',
            'created_at': '建立時間',
            'done_at': '完成時間',
            'floor': '樓層',
            'status': '狀態'
        }
        
        display_df = display_incomplete[available_cols].copy()
        display_df.columns = [column_names.get(col, col) for col in display_df.columns]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # ============================================
    # 3. 用戶賬戶管理
    # ============================================
    st.markdown("### 👥 用戶賬戶管理")
    
    # 3.1 建立新用戶
    with st.expander("➕ 建立新用戶賬戶", expanded=False):
        st.markdown("**建立新的系統用戶**")
        
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("用戶名稱", key="new_username").strip().upper()
        with col2:
            new_password = st.text_input("初始密碼", type="password", key="new_password").strip()
        
        new_role = st.selectbox(
            "設置角色",
            options=["Admin", "Staff", "Customer"],
            format_func=lambda x: {
                "Admin": "👑 Admin（系統管理員）",
                "Staff": "👤 Staff（員工）",
                "Customer": "🏢 Customer（客戶）"
            }.get(x, x),
            key="new_role"
        )
        
        if new_password:
            if len(new_password) < 6:
                st.error("❌ 密碼長度必須至少 6 個字元")
            elif len(new_password) < 8:
                st.warning("⚠️ 建議密碼長度至少 8 個字元")
            else:
                st.success("✅ 密碼強度足夠")
        
        if st.button("建立用戶賬戶", use_container_width=True, key="create_user_btn"):
            if new_username and new_password:
                if len(new_password) < 6:
                    st.error("❌ 密碼長度必須至少 6 個字元")
                else:
                    success, msg = db.create_user(new_username, new_password, new_role)
                    if success:
                        st.success(f"✅ 用戶賬戶 {new_username} 建立成功！")
                        st.info(f"📝 請告知用戶以下登入資訊：\n\n**用戶名**: `{new_username}`\n**密碼**: `{new_password}`\n**角色**: `{new_role}`")
                        write_audit_log(st.session_state.username, f"建立用戶：{new_username}", f"角色：{new_role}")
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.error("請填寫用戶名稱和密碼")
        
        st.divider()
        st.markdown("**角色說明：**")
        st.markdown("""
        - **👑 Admin**：系統管理員，可訪問所有功能（建立任務、審核預報、管理用戶等）
        - **👤 Staff**：員工，可訪問倉庫端作業功能（掃描入庫、查看批次等）
        - **🏢 Customer**：客戶，可訪問客戶端預報功能（提交預報、查看自己的批次）
        """)
    
    st.divider()
    
    # 3.2 所有用戶列表
    with st.expander("📋 所有用戶列表", expanded=False):
        users_df = db.get_all_users()
        
        if not users_df.empty:
            # 選擇並排序欄位
            display_cols = ['username', 'role', 'created_at']
            available_cols = [col for col in display_cols if col in users_df.columns]
            
            # 重命名欄位
            column_names = {
                'username': '用戶名稱',
                'role': '角色',
                'created_at': '建立時間'
            }
            
            display_df = users_df[available_cols].copy()
            display_df.columns = [column_names.get(col, col) for col in display_df.columns]
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("尚無用戶數據")
    
    st.divider()
    
    # ============================================
    # 4. 參考表模組掛載點（Option B+）
    # ============================================
    try:
        from hooks import REFERENCE_MODULE_ENABLED, REFERENCE_SHOW_IN_OFFICE, check_module_installation
        
        if REFERENCE_MODULE_ENABLED and REFERENCE_SHOW_IN_OFFICE:
            # 檢查模組安裝狀態
            install_status = check_module_installation()
            
            if install_status['installed']:
                from reference_module import render_reference_uploader
                render_reference_uploader(location="office")
            else:
                # 模組未正確安裝，顯示警告和安裝說明
                st.markdown("### 📚 參考表管理")
                st.error("📚 參考表模組未正確安裝")
                
                for error in install_status['errors']:
                    st.error(f"❌ {error}")
                for warning in install_status['warnings']:
                    st.warning(f"⚠️ {warning}")
                
                st.divider()
                st.markdown("**📖 安裝步驟：**")
                st.code("""
1. 確認 hooks.py 已放到 C:\\PT_IB\\ 目錄
2. 確認 reference_module/ 資料夾已創建
3. 確認 reference_module/ 內有以下檔案：
   - __init__.py
   - ref_table.py
   - scanner.py
   - uploader.py
4. 刪除 C:\\PT_IB\\__pycache__ 資料夾
5. 重新啟動系統
                """)
                
    except ImportError as e:
        # hooks.py 不存在
        st.markdown("### 📚 參考表管理")
        st.error(f"📚 hooks.py 未找到：{e}")
        st.caption("💡 請聯繫系統管理員安裝參考表模組")
