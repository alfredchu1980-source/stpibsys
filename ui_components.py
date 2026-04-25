# ui_components.py
import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from config import CONFIG
from utils import write_audit_log, play_audio, style_rows
import database as db
import services

def show_login():
    st.markdown("<h1 style='text-align: center;'>🔐 Shoptoplus 系統登入</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            user_input = st.text_input("用戶名稱 (Name)", key="login_username").strip().upper()
            pass_input = st.text_input("密碼 (Password)", type="password", key="login_password").strip()
            submit = st.form_submit_button("登入", use_container_width=True)
            if submit:
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
                        st.session_state.login_time = datetime.now()
                        write_audit_log(user_input, "用戶登入", "N/A")
                        st.rerun()
                    else:
                        st.error(f"❌ 登入失敗：{result}")

def render_sidebar_controls():
    user_role = st.session_state.role
    current_user = st.session_state.username
    
    user_floor = None
    if current_user in CONFIG["ROLES"].get("STAFF_3F", []):
        user_floor = "3F"
    elif current_user in CONFIG["ROLES"].get("STAFF_5F", []):
        user_floor = "5F"
    
    if user_role in ["Admin", "Staff"]:
        with st.expander("🚀 建立新任務", expanded=False):
            cust_name = st.text_input("🏢 客戶名稱", value="預設客戶", key="sidebar_cust_name")
            new_batch_id = st.text_input("新任務編號", placeholder="例如：JOB-001", key="sidebar_batch_id")
            uploaded_file = st.file_uploader("上傳 Excel", type=["xlsx"], key="sidebar_uploader")
            
            if user_role == "Admin":
                batch_floor = st.selectbox("作業樓層", ["3F", "5F"], key="sidebar_floor")
            else:
                batch_floor = user_floor if user_floor else "3F"
            
            if st.button("建立任務", use_container_width=True, key="sidebar_create_btn") and new_batch_id and uploaded_file:
                success, msg = services.process_excel_upload(uploaded_file, new_batch_id, cust_name, batch_floor, "")
                if success: 
                    st.success(msg)
                    st.rerun()
                else: 
                    st.error(msg)
        
        st.divider()
    
    if user_role in ["Admin", "Staff"]:
        all_batches = db.get_all_batches()
        
        if user_floor and user_role != "Admin":
            batches = db.get_batches_by_floor(user_floor)
            st.caption(f"📍 樓層過濾：{user_floor}")
        else:
            batches = all_batches
        
        current_batch = st.selectbox("📦 選擇作業批次", ["請選擇"] + batches, key="sidebar_batch_select")
        
        if user_role == "Admin" and current_batch != "請選擇":
            if st.button("🗑️ 刪除此任務", use_container_width=True, key="sidebar_delete_btn"):
                if db.delete_batch(current_batch): 
                    st.rerun()
        
        return current_batch
    else:
        return None

def render_user_management():
    user_role = st.session_state.role
    
    if user_role == "Admin":
        with st.expander("👥 建立客戶帳號", expanded=False):
            st.markdown("**建立新的客戶登入帳號**")
            new_username = st.text_input("客戶用戶名稱", key="admin_new_username").strip().upper()
            new_password = st.text_input("初始密碼", type="password", key="admin_new_password").strip()
            
            if new_password:
                if len(new_password) < 6:
                    st.error("❌ 密碼長度必須至少 6 個字元")
                elif len(new_password) < 8:
                    st.warning("⚠️ 建議密碼長度至少 8 個字元")
                else:
                    st.success("✅ 密碼強度足夠")
            
            if st.button("建立客戶帳號", use_container_width=True, key="admin_create_customer_btn"):
                if new_username and new_password:
                    if len(new_password) < 6:
                        st.error("❌ 密碼長度必須至少 6 個字元")
                    else:
                        success, msg = db.create_user(new_username, new_password, "Customer")
                        if success:
                            st.success(f"✅ 客戶帳號 {new_username} 建立成功！")
                            st.info(f"📝 請告知客戶：\n\n用戶名：{new_username}\n密碼：{new_password}")
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.error("請填寫用戶名稱和密碼")
            
            st.divider()
            st.markdown("**所有用戶列表**")
            users_df = db.get_all_users()
            if not users_df.empty:
                customer_users = users_df[users_df['role'] == 'Customer']
                if not customer_users.empty:
                    st.dataframe(customer_users[['username', 'role', 'created_at']], use_container_width=True)
                else:
                    st.info("尚無客戶帳號")
            else:
                st.info("尚無用戶數據")
        
        st.divider()
    
    with st.expander("🔑 修改我的密碼", expanded=False):
        current_username = st.session_state.username
        st.caption(f"當前用戶：{current_username}")
        new_pwd = st.text_input("新密碼", type="password", key="new_pwd").strip()
        confirm_pwd = st.text_input("確認新密碼", type="password", key="confirm_pwd").strip()
        
        if new_pwd:
            if len(new_pwd) < 6:
                st.error("❌ 密碼長度必須至少 6 個字元")
            elif len(new_pwd) < 8:
                st.warning("⚠️ 建議密碼長度至少 8 個字元")
            else:
                st.success("✅ 密碼強度足夠")
        
        if st.button("更新密碼", use_container_width=True, key="update_pwd_btn"):
            if new_pwd and confirm_pwd:
                if len(new_pwd) < 6:
                    st.error("❌ 密碼長度必須至少 6 個字元")
                elif new_pwd == confirm_pwd:
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

def show_work_tab(current_batch):
    if current_batch is None:
        st.info("👈 請在左側選擇任務開始工作。")
        return
    
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
    w1 = w_col1.text_input("工作人員 1", value=first_p["worker1"] if first_p is not None else "", disabled=is_locked).strip().upper()
    w2 = w_col2.text_input("工作人員 2", value=first_p["worker2"] if first_p is not None else "", disabled=is_locked).strip().upper()
    return w1, w2

def _render_work_core(current_batch, task_df, is_locked, worker1, worker2):
    if 'last_signal' in st.session_state:
        st.markdown(st.session_state.last_signal, unsafe_allow_html=True)
    _render_scan_section(current_batch, task_df, is_locked, worker1, worker2)

def _render_scan_section(current_batch, task_df, is_locked, worker1, worker2):
    def on_scan():
        # 新掃描開始時，清除舊的掃描記錄和狀態信號，避免混淆
        st.session_state.active_barcode = st.session_state.barcode_scan_input
        st.session_state.barcode_scan_input = ""
        # 清除舊的狀態信號，確保只显示當前掃描的結果
        if 'last_signal' in st.session_state:
            del st.session_state.last_signal
    
    st.text_input("🔍 掃描產品 Barcode", key="barcode_scan_input", on_change=on_scan, disabled=is_locked, placeholder="請掃描...")
    active_barcode = st.session_state.get('active_barcode', "")
    if not active_barcode: return
    scan_code = active_barcode.strip()
    sku_records = task_df[task_df['barcode'].astype(str) == scan_code] if not task_df.empty else pd.DataFrame()
    if sku_records.empty:
        st.error(f"❌ 找不到條碼：{scan_code}"); play_audio("error"); return
    base_item = sku_records.iloc[0]
    _render_product_status_card(base_item, sku_records)
    
    # 🔍 參考表模組掛載點（Option B+）
    try:
        from hooks import REFERENCE_MODULE_ENABLED, REFERENCE_SHOW_IN_SCAN
        if REFERENCE_MODULE_ENABLED and REFERENCE_SHOW_IN_SCAN:
            from reference_module import render_reference_scanner
            render_reference_scanner(scan_code)
    except ImportError:
        pass  # 模組未安裝時不影響原有功能
    except Exception as e:
        # 其他錯誤，顯示警告（僅 Admin 可見）
        try:
            if st.session_state.role == "Admin":
                st.warning(f"⚠️ 參考表功能異常：{e}")
        except:
            pass
    
    if not is_locked:
        _render_input_form(current_batch, scan_code, base_item, sku_records, task_df, worker1, worker2)

def _render_product_status_card(base_item, sku_records):
    val_exp = pd.to_numeric(base_item['expected_qty'], errors='coerce')
    expected_num = 0 if pd.isna(val_exp) else val_exp
    current_total = pd.to_numeric(sku_records['actual_qty'], errors='coerce').sum()
    
    if current_total == expected_num:
        status_color = "#28a745"
        status_text = "✅ 數量正確"
    elif current_total > expected_num:
        status_color = "#dc3545"
        status_text = "⚠️ 超收"
    else:
        status_color = "#007bff"
        status_text = "⚠️ 少收"
    
    st.markdown(f"""
        <div style="background-color: #000000; color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-bottom: 15px; border-left: 5px solid {status_color};">
            <h3 style="margin:0; color: {status_color};">📦 {base_item['product_name']}</h3>
            <p style="margin:10px 0; font-size: 18px;">SKU ID: {base_item['sku_id']} | 批次：{base_item.get('lot', 'N/A')}</p>
            <div style="display: flex; justify-content: space-between; font-weight: bold; border-top: 1px solid #333; padding-top: 10px; margin-top: 10px;">
                <span>總預計：{int(expected_num)}</span>
                <span style="color: {status_color};">{status_text} - 目前累計已收：{int(current_total)}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def _render_input_form(current_batch, scan_code, base_item, sku_records, task_df, worker1, worker2):
    with st.form("input_form", clear_on_submit=False):
        new_qty = st.text_input("1. 入庫數量", value=str(int(float(base_item['expected_qty'] or 0))))
        new_bbd = st.text_input("2. 到期日期 (YYYY-MM-DD)", value=base_item.get('expiry_date', ''))
        new_loc = st.text_input("3. 存放位置").strip().upper()
        submit = st.form_submit_button("💾 確認儲存", use_container_width=True)
        if submit:
            success, signal, sound = services.validate_scan_and_save(current_batch, scan_code, new_qty, new_bbd, new_loc, worker1, worker2, task_df)
            if success: 
                st.session_state.last_signal = signal
                play_audio(sound)
                # 清除 active_barcode 讓焦點回到掃描框
                st.session_state.active_barcode = ""
                st.rerun()
            else: 
                st.error(signal)
                play_audio(sound)

def _render_inventory_list(current_batch, task_df, is_locked):
    """入庫清單表格 - 核心顏色邏輯（使用 HTML 顯示顏色）"""
    st.subheader("📋 入庫清單")
    if task_df.empty:
        st.info("尚無資料")
        return
    
    # 複製數據並按 barcode 和 seq 排序，確保相同條碼的物品相鄰顯示
    display_df = task_df[['seq', 'barcode', 'sku_id', 'actual_qty', 'location', 'expiry_date', 'expected_qty']].copy()
    
    # 排序：先按 barcode 排序，再按 seq 排序（確保 #1, #1.1, #1.2 相鄰）
    display_df = display_df.sort_values(['barcode', 'seq'], ascending=[True, True]).reset_index(drop=True)
    
    # 轉換 expected_qty 為數字
    display_df['exp_val'] = pd.to_numeric(display_df['expected_qty'], errors='coerce').fillna(0)
    
    # 計算每個 barcode 的總實際入庫數量（用於判斷是否超收）
    def calc_barcode_total(barcode):
        barcode_rows = display_df[display_df['barcode'] == barcode]
        total = 0
        for _, row in barcode_rows.iterrows():
            raw_qty = row['actual_qty']
            if pd.notna(raw_qty) and str(raw_qty).strip() != "" and str(raw_qty).strip().lower() != "nan":
                try:
                    total += float(str(raw_qty).strip())
                except:
                    pass
        return total
    
    # 為每個 barcode 計算總入庫數量
    barcode_totals = {}
    for barcode in display_df['barcode'].unique():
        barcode_totals[barcode] = calc_barcode_total(barcode)
    
    # 為每個 barcode 計算總預計數量
    barcode_expected = {}
    for barcode in display_df['barcode'].unique():
        exp_val = display_df[display_df['barcode'] == barcode]['exp_val'].iloc[0]
        barcode_expected[barcode] = exp_val
    
    # 核心顏色邏輯：為每行添加顏色和狀態
    def get_row_style(row):
        barcode = row['barcode']
        raw_qty = row['actual_qty']
        
        # 檢查是否未掃描：空值、None、NaN、空字符串、或只是 "0"
        is_unscanned = (
            pd.isna(raw_qty) or 
            str(raw_qty).strip() == "" or 
            str(raw_qty).strip().lower() == "nan" or
            str(raw_qty).strip() == "0"
        )
        
        if is_unscanned:
            return None  # 尚未入庫，不 highlight（透明）
        
        # 已掃描，獲取該 barcode 的總入庫數量和總預計數量
        total_received = barcode_totals.get(barcode, 0)
        total_expected = barcode_expected.get(barcode, 0)
        
        location = str(row['location']).strip() if pd.notna(row['location']) else ""
        expiry = str(row['expiry_date']).strip() if pd.notna(row['expiry_date']) else ""
        
        # 紅色：該 barcode 的總入庫數量 > 總預計數量（超收）- 所有記錄都顯示紅色
        if total_received > total_expected:
            return '#dc3545'  # RED - 超收（所有該 barcode 的記錄）
        
        # 綠色：總數量正確 + 有儲位 + 有到期日（表示已完整掃描）
        elif total_received == total_expected and total_expected > 0 and location and expiry:
            return '#28a745'  # GREEN - 已完成入庫
        
        # 藍色：少收
        else:
            return '#007bff'  # BLUE - 少收
    
    display_df['row_color'] = display_df.apply(get_row_style, axis=1)
    
    # 重新命名為中文顯示
    display_df = display_df.rename(columns={
        'seq': '#',
        'barcode': '條碼',
        'sku_id': 'SKU',
        'actual_qty': '入庫',
        'location': '位置',
        'expiry_date': '到期日',
        'expected_qty': '預計'
    })
    
    # 使用 HTML 自定義表格顯示顏色 - 調整欄位寬度（不顯示名稱）
    html_table = '<div style="height: 500px; overflow-y: auto;"><table style="width: 100%; border-collapse: collapse;">'
    html_table += '<thead style="position: sticky; top: 0; background: #1e1e1e;"><tr>'
    html_table += '<th style="border: 1px solid #444; padding: 8px; color: white; width: 30px;">#</th>'
    html_table += '<th style="border: 1px solid #444; padding: 8px; color: white; width: 120px;">條碼</th>'
    html_table += '<th style="border: 1px solid #444; padding: 8px; color: white; width: 100px;">SKU</th>'
    html_table += '<th style="border: 1px solid #444; padding: 8px; color: white; width: 50px;">入庫</th>'
    html_table += '<th style="border: 1px solid #444; padding: 8px; color: white; width: 120px;">位置</th>'
    html_table += '<th style="border: 1px solid #444; padding: 8px; color: white; width: 100px;">到期日</th>'
    html_table += '<th style="border: 1px solid #444; padding: 8px; color: white; width: 50px;">預計</th>'
    html_table += '</tr></thead><tbody>'
    
    for _, row in display_df.iterrows():
        color = row['row_color']
        if color is None:
            html_table += f'<tr style="background-color: #2d333b; color: #c9d1d9;">'
        else:
            html_table += f'<tr style="background-color: {color}; color: white;">'
        
        html_table += f'<td style="border: 1px solid #444; padding: 8px;">{row["#"]}</td>'
        html_table += f'<td style="border: 1px solid #444; padding: 8px;">{row["條碼"]}</td>'
        html_table += f'<td style="border: 1px solid #444; padding: 8px;">{row["SKU"]}</td>'
        html_table += f'<td style="border: 1px solid #444; padding: 8px; text-align: center;">{row["入庫"]}</td>'
        html_table += f'<td style="border: 1px solid #444; padding: 8px;">{row["位置"]}</td>'
        html_table += f'<td style="border: 1px solid #444; padding: 8px;">{row["到期日"]}</td>'
        html_table += f'<td style="border: 1px solid #444; padding: 8px; text-align: center;">{row["預計"]}</td>'
        html_table += '</tr>'
    
    html_table += '</tbody></table></div>'
    
    st.markdown(html_table, unsafe_allow_html=True)
    
    # 顯示顏色圖例
    st.caption("📊 顏色說明：⚪ 正常 = 尚未入庫 | 🟢 綠色 = 已完成（數量正確 + 有儲位 + 有到期日） | 🔴 紅色 = 超收（該條碼總入庫 > 總預計） | 🔵 藍色 = 少收")
    
    # 刪除錯誤記錄功能（放在顏色說明之下）
    if not is_locked:
        st.divider()
        st.subheader("🗑️ 清除錯誤記錄")
        
        # 獲取所有已有入庫數據的記錄（highlight 的記錄）- 使用原始 task_df
        task_df_with_data = task_df[pd.to_numeric(task_df['actual_qty'], errors='coerce').fillna(0) > 0].copy()
        
        if task_df_with_data.empty:
            st.info("目前沒有已入庫的記錄")
        else:
            options = []
            for _, row in task_df_with_data.iterrows():
                options.append(f"{row['seq']} - {row['barcode']} ({row['sku_id']}) - 入庫：{row['actual_qty']}")
            
            selected = st.selectbox("選擇要清除的記錄", ["請選擇"] + options, key="delete_selector")
            
            if selected != "請選擇":
                # 解析選中的記錄
                target_seq = selected.split(" - ")[0]
                st.warning(f"準備清除：序號 {target_seq}")
                
                col_del1, col_del2 = st.columns([3, 1])
                with col_del1:
                    st.caption("此操作將清除該記錄的入庫數據，恢復為尚未入庫狀態")
                with col_del2:
                    if st.button("🗑️ 確認清除", use_container_width=True, type="primary"):
                        try:
                            # 清除該記錄的入庫數據
                            supabase = db.get_supabase_client()
                            supabase.table("products").update({
                                "actual_qty": "",
                                "location": "",
                                "expiry_date": "",
                                "worker1": "",
                                "worker2": "",
                                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }).eq("batch_id", current_batch).eq("seq", target_seq).execute()
                            st.success("✅ 已清除記錄")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 清除失敗：{str(e)}")

def show_report_tab(current_batch):
    df = db.get_products_by_batch(current_batch)
    st.markdown(f"### 📊 {current_batch} 數據統計")
    st.dataframe(df, use_container_width=True)
    st.divider()
    reports = services.get_reports_for_download(current_batch)
    if reports:
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 下載 IVR 差異報告", data=reports["ivr"]["data"], file_name=reports["ivr"]["filename"], use_container_width=True)
        with c2:
            st.download_button("📥 下載 STD 總結報告", data=reports["std"]["data"], file_name=reports["std"]["filename"], use_container_width=True)

def add_auto_focus():
    """自動聚焦掃描輸入框"""
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
