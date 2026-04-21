# ui_components.py
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
import streamlit.components.v1 as components
from config import CONFIG
from utils import write_audit_log, play_audio, style_rows, get_excel_formats
import database as db
import services

# --- 1. 登入組件 ---

def show_login():
    st.markdown("<h1 style='text-align: center;'>🔐 Shoptoplus 系統登入</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        user_input = st.text_input("用戶名稱 (Name)", key="login_username").strip().upper()
        pass_input = st.text_input("密碼 (Password)", type="password", key="login_password").strip()
        
        if st.button("登入", use_container_width=True, key="login_button"):
            if not user_input:
                st.error("❌ 請輸入用戶名稱")
            elif not pass_input:
                st.error("❌ 請輸入密碼")
            else:
                success, result = db.verify_user(user_input, pass_input)
                if success:
                    st.session_state.role = result
                    st.session_state.logged_in = True
                    st.session_state.username = user_input.upper()
                    write_audit_log(user_input, "用戶登入", "N/A")
                    st.rerun()
                else:
                    st.error(f"❌ 登入失敗：{result}")

# --- 2. 側邊欄組件 (V70 核心結構) ---

def render_sidebar_controls():
    """
    在側邊欄渲染控制項：建立新任務、選擇作業批次
    必須在 st.sidebar 區塊內調用
    """
    user_role = st.session_state.role
    
    # 建立新任務 (Admin 和 Staff 可用)
    if user_role in ["Admin", "Staff"]:
        with st.expander("🚀 建立新任務", expanded=False):
            cust_name = st.text_input("🏢 客戶名稱", value="預設客戶", key="sidebar_cust_name")
            new_batch_id = st.text_input("新任務編號", placeholder="例如：JOB-001", key="sidebar_batch_id")
            uploaded_file = st.file_uploader("上傳 Excel", type=["xlsx"], key="sidebar_uploader")
            
            if st.button("建立任務", use_container_width=True, key="sidebar_create_btn") and new_batch_id and uploaded_file:
                success, msg = services.process_excel_upload(uploaded_file, new_batch_id, cust_name, "", "")
                if success: 
                    st.success(msg)
                    st.rerun()
                else: 
                    st.error(msg)
        
        st.divider()
    
    # 選擇作業批次
    batches = db.get_all_batches()
    current_batch = st.selectbox("📦 選擇作業批次", ["請選擇"] + batches, key="sidebar_batch_select")
    
    if user_role == "Admin" and current_batch != "請選擇":
        if st.button("🗑️ 刪除此任務", use_container_width=True, key="sidebar_delete_btn"):
            if db.delete_batch(current_batch): 
                st.rerun()
    
    return current_batch

def render_user_management():
    """用戶管理功能（所有用戶只能修改自己的密碼）"""
    with st.expander("🔑 修改我的密碼", expanded=False):
        current_username = st.session_state.username
        st.caption(f"當前用戶：{current_username}")
        
        new_pwd = st.text_input("新密碼", type="password", key="new_pwd").strip()
        confirm_pwd = st.text_input("確認新密碼", type="password", key="confirm_pwd").strip()
        
        if st.button("更新密碼", use_container_width=True, key="update_pwd_btn"):
            if new_pwd and confirm_pwd:
                if new_pwd == confirm_pwd:
                    success, msg = db.update_user_password(current_username, new_pwd)
                    if success:
                        st.success(msg)
                        st.info("✅ 密碼已更新，請使用新密碼重新登入")
                        st.session_state.logged_in = False
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("兩次輸入的密碼不一致")
            else:
                st.error("請填寫密碼")

# --- 3. 入庫作業分頁 ---

def show_work_tab(current_batch):
    """入庫作業主頁面"""
    batch_info = db.get_batch_info(current_batch)
    is_locked = batch_info["status"] == "completed" if batch_info else False
    task_df = db.get_products_by_batch(current_batch)
    
    worker1, worker2 = _render_worker_info(task_df, is_locked)
    st.divider()

    ui_mode = st.session_state.get('ui_mode', "電腦模式")
    
    if ui_mode == "電腦模式":
        col_scan, col_list = st.columns([1, 1.3])
        with col_scan:
            _render_work_core(current_batch, task_df, is_locked, worker1, worker2)
        with col_list:
            _render_inventory_list(current_batch, task_df, is_locked)
    else:
        _render_work_core(current_batch, task_df, is_locked, worker1, worker2)
        st.divider()
        _render_inventory_list(current_batch, task_df, is_locked)

    if not is_locked and st.session_state.role in ["Admin", "Staff"]:
        st.divider()
        if st.button("✅ 正式完成入庫並鎖定", type="primary", use_container_width=True):
            if db.update_batch_status(current_batch, 'completed'):
                services.export_reports_to_files(current_batch)
                st.success("✅ 結案成功！報告已生成。")
                st.rerun()

def _render_worker_info(task_df, is_locked):
    st.markdown("### 👷 實際作業人員記錄")
    w_col1, w_col2 = st.columns(2)
    first_p = task_df.iloc[0] if not task_df.empty else None
    w1 = w_col1.text_input("工作人員 1", value=first_p["worker1"] if first_p is not None else "",
                           disabled=is_locked).strip().upper()
    w2 = w_col2.text_input("工作人員 2", value=first_p["worker2"] if first_p is not None else "",
                           disabled=is_locked).strip().upper()
    return w1, w2

def _render_work_core(current_batch, task_df, is_locked, worker1, worker2):
    if 'last_signal' in st.session_state:
        st.markdown(st.session_state.last_signal, unsafe_allow_html=True)
    _render_scan_section(current_batch, task_df, is_locked, worker1, worker2)

def _render_scan_section(current_batch, task_df, is_locked, worker1, worker2):
    def on_scan():
        st.session_state.active_barcode = st.session_state.barcode_scan_input
        st.session_state.barcode_scan_input = ""

    st.text_input("🔍 掃描產品 Barcode", key="barcode_scan_input", 
                  on_change=on_scan, disabled=is_locked, placeholder="請掃描...")
    
    active_barcode = st.session_state.get('active_barcode', "")
    if not active_barcode: return

    scan_code = active_barcode.strip()
    sku_records = task_df[task_df['barcode'].astype(str) == scan_code] if not task_df.empty else pd.DataFrame()
    
    if sku_records.empty:
        st.error(f"❌ 找不到條碼：{scan_code}"); play_audio("error"); return

    base_item = sku_records.iloc[0]
    _render_product_status_card(base_item, sku_records)

    if not is_locked:
        _render_input_form(current_batch, scan_code, base_item, sku_records, task_df, worker1, worker2)

def _render_product_status_card(base_item, sku_records):
    val_exp = pd.to_numeric(base_item['expected_qty'], errors='coerce')
    expected_num = 0 if pd.isna(val_exp) else val_exp
    current_total = pd.to_numeric(sku_records['actual_qty'], errors='coerce').sum()
    
    st.markdown(f"""
        <div style="background-color: #000000; color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 15px;">
            <h3 style="margin:0; color: #63b3ed;">📦 {base_item['product_name']}</h3>
            <p style="margin:10px 0; font-size: 18px;">SKU ID: {base_item['sku_id']} | 批次：{base_item.get('lot', 'N/A')}</p>
            <div style="display: flex; justify-content: space-between; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; margin-top: 10px;">
                <span>總預計：{int(expected_num)}</span>
                <span style="color: #63b3ed;">目前累計已收：{int(current_total)}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def _render_input_form(current_batch, scan_code, base_item, sku_records, task_df, worker1, worker2):
    with st.form("input_form", clear_on_submit=True):
        new_qty = st.text_input("1. 入庫數量", value=str(int(float(base_item['expected_qty'] or 0))))
        new_bbd = st.text_input("2. 到期日期 (YYYY-MM-DD)", value=base_item.get('expiry_date', ''))
        new_loc = st.text_input("3. 存放位置").strip().upper()
        submit = st.form_submit_button("💾 確認儲存", use_container_width=True)
        
        if submit:
            success, signal, sound = services.validate_scan_and_save(
                current_batch, scan_code, new_qty, new_bbd, new_loc, worker1, worker2, task_df
            )
            if success: 
                st.session_state.last_signal = signal
                play_audio(sound)
                st.rerun()
            else: 
                st.error(signal)
                play_audio(sound)

def _render_inventory_list(current_batch, task_df, is_locked):
    st.subheader("📋 入庫清單")
    if task_df.empty:
        st.info("尚無資料")
        return
    display_df = task_df[['seq', 'barcode', 'sku_id', 'product_name', 'actual_qty', 'location', 'expiry_date', 'expected_qty']].copy()
    display_df['exp_val'] = pd.to_numeric(display_df['expected_qty'], errors='coerce').fillna(0)
    display_df.columns = ['#', '條碼', 'SKU', '名稱', '入庫', '位置', '到期日', '預計', 'exp_val']
    st.dataframe(display_df.style.apply(style_rows, axis=1), 
                 column_config={"exp_val": None, "預計": None}, use_container_width=True, height=500)

# --- 4. 數據報表分頁 ---

def show_report_tab(current_batch):
    df = db.get_products_by_batch(current_batch)
    st.markdown(f"### 📊 {current_batch} 數據統計")
    st.dataframe(df, use_container_width=True)
    
    st.divider()
    
    reports = services.get_reports_for_download(current_batch)
    if reports:
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 下載 IVR 差異報告", data=reports["ivr"]["data"], 
                               file_name=reports["ivr"]["filename"], use_container_width=True)
        with c2:
            st.download_button("📥 下載標準入庫清單", data=reports["std"]["data"], 
                               file_name=reports["std"]["filename"], use_container_width=True)

def add_auto_focus():
    components.html("""<script>
        function smartFocus() {
            const activeEl = window.parent.document.activeElement;
            const isTyping = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA');
            if (isTyping) return;
            const inputs = window.parent.document.querySelectorAll('input');
            for (let i = 0; i < inputs.length; i++) {
                if (inputs[i].placeholder === "請掃描...") {
                    inputs[i].focus(); break;
                }
            }
        }
        setInterval(smartFocus, 2000);
    </script>""", height=0)
