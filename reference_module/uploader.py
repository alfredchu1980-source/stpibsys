# reference_module/uploader.py
"""
參考表上傳 UI 元件
"""

import streamlit as st

try:
    from hooks import REFERENCE_SHOW_IN_SIDEBAR, REFERENCE_SHOW_IN_OFFICE
except ImportError:
    REFERENCE_SHOW_IN_SIDEBAR = True
    REFERENCE_SHOW_IN_OFFICE = True


def render_reference_uploader(location="sidebar"):
    """
    渲染參考表上傳元件
    
    參數:
        location: "sidebar" 或 "office"
    """
    # 根據位置檢查是否顯示
    if location == "sidebar" and not REFERENCE_SHOW_IN_SIDEBAR:
        return
    if location == "office" and not REFERENCE_SHOW_IN_OFFICE:
        return
    
    # 根據位置選擇不同的 UI 樣式
    if location == "sidebar":
        _render_sidebar_uploader()
    elif location == "office":
        _render_office_uploader()


def _render_sidebar_uploader():
    """側邊欄快速上傳（簡化版）"""
    with st.expander("📚 參考表管理", expanded=False):
        # 顯示上傳成功訊息（使用 session state 保持顯示）
        if 'ref_upload_success' in st.session_state and st.session_state.ref_upload_success:
            st.success(f"✅ {st.session_state.ref_upload_message}")
            st.info("💡 參考表已更新，掃描條碼時會自動顯示參考資料")
            # 清除成功訊息（避免重複顯示）
            st.session_state.ref_upload_success = False
            st.session_state.ref_upload_message = ""
        
        ref_info = None
        try:
            from .ref_table import get_reference_info
            ref_info = get_reference_info()
        except:
            pass
        
        if ref_info:
            st.caption(f"📊 記錄數：{ref_info['total_records']:,}")
            st.caption(f"🕐 更新：{ref_info['last_updated']}")
        else:
            st.caption("📄 尚未建立參考表")
        
        st.divider()
        
        uploaded_file = st.file_uploader(
            "上傳 CSV",
            type=["csv"],
            key="sidebar_ref_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.info(f"📄 已選擇：`{uploaded_file.name}`")
            try:
                from .ref_table import update_reference_table
                if st.button("📤 上傳", use_container_width=True, key="sidebar_upload_btn"):
                    with st.spinner("⏳ 上傳處理中..."):
                        success, message = update_reference_table(uploaded_file)
                        if success:
                            # 儲存成功訊息到 session state
                            st.session_state.ref_upload_success = True
                            st.session_state.ref_upload_message = message
                            # 寫入審計日誌
                            try:
                                from utils import write_audit_log
                                write_audit_log(st.session_state.username, "更新參考表", uploaded_file.name)
                            except:
                                pass
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
            except Exception as e:
                st.error(f"❌ 上傳失敗：{str(e)}")


def _render_office_uploader():
    """Office 管理頁面完整上傳（詳細版）"""
    st.markdown("### 📚 參考表管理")
    
    # 顯示上傳成功訊息（使用 session state 保持顯示）
    if 'ref_upload_success' in st.session_state and st.session_state.ref_upload_success:
        st.success(f"✅ {st.session_state.ref_upload_message}")
        st.info("💡 參考表已更新，掃描條碼時會自動顯示參考資料")
        # 清除成功訊息（避免重複顯示）
        st.session_state.ref_upload_success = False
        st.session_state.ref_upload_message = ""
    
    # 顯示當前參考表資訊
    try:
        from .ref_table import get_reference_info
        ref_info = get_reference_info()
        
        if ref_info:
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("📊 總記錄數", f"{ref_info['total_records']:,}")
            with col_info2:
                st.metric("📁 檔案大小", f"{ref_info['file_size_kb']} KB")
            with col_info3:
                st.metric("🕐 最後更新", ref_info['last_updated'])
            
            # 顯示參考表已就緒訊息
            st.success("✅ 參考表已就緒，掃描條碼時會自動顯示參考資料")
        else:
            st.info("📄 尚未建立參考表，請上傳 CSV 檔案")
    except Exception as e:
        st.error(f"讀取參考表失敗：{e}")
    
    st.divider()
    
    # 上傳參考表
    st.markdown("#### 📤 上傳參考表 (CSV)")
    st.caption("格式：CSV (UTF-8 編碼) | Column E = 儲位 | Column F = 到期日 | 第一列為欄位名稱")
    
    uploaded_file = st.file_uploader("選擇 CSV 檔案", type=["csv"], key="office_ref_uploader")
    
    if uploaded_file:
        st.info(f"📄 已選擇：`{uploaded_file.name}`")
        col_upload1, col_upload2 = st.columns([3, 1])
        with col_upload1:
            st.caption("💡 上傳後會立即生效，無需重新啟動系統")
        with col_upload2:
            if st.button("📤 上傳參考表", use_container_width=True, key="office_upload_btn"):
                with st.spinner("⏳ 上傳處理中..."):
                    try:
                        from .ref_table import update_reference_table
                        success, message = update_reference_table(uploaded_file)
                        
                        if success:
                            # 儲存成功訊息到 session state
                            st.session_state.ref_upload_success = True
                            st.session_state.ref_upload_message = message
                            # 寫入審計日誌
                            try:
                                from utils import write_audit_log
                                write_audit_log(st.session_state.username, "更新參考表", uploaded_file.name)
                            except:
                                pass
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    except Exception as e:
                        st.error(f"❌ 上傳失敗：{str(e)}")
    
    # 使用說明
    with st.expander("📖 參考表使用說明", expanded=False):
        st.markdown("""
        **參考表用途：**
        - 掃描條碼時，自動顯示該條碼對應的儲位和到期日
        - 協助倉庫人員快速找到正確的儲位
        
        **CSV 格式規範：**
        - 檔案格式：CSV (UTF-8 編碼)
        - 第一列：欄位名稱（header）
        - Column A-D：其他資料（系統會忽略）
        - Column E：儲位（location）- 必填
        - Column F：到期日（expiry_date）- 必填，格式：YYYY-MM-DD
        
        **CSV 範例：**
        ```csv
        barcode,product_name,sku_id,qty,location,expiry_date
        ABC123,產品 A,SKU001,100,A01-01-001,2025-12-31
        DEF456,產品 B,SKU002,200,B02-02-002,2026-03-15
        ```
        
        **更新方式：**
        1. 準備新的 CSV 檔案
        2. 點擊「選擇 CSV 檔案」按鈕
        3. 選擇檔案後點擊「📤 上傳參考表」
        4. 系統會自動替換舊的參考表
        
        **注意事項：**
        - 只有 Admin 可以上傳參考表
        - 上傳後會立即生效，無需重新啟動系統
        - 舊參考表不會備份，請自行保留備份檔案
        """)
