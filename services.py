# services.py
import pandas as pd
from datetime import datetime
import re
from config import CONFIG
import database as db
import os
import io
from utils import get_excel_formats

def is_valid_expiry_date(date_str):
    if not date_str: return True, ""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return False, "格式必須為 YYYY-MM-DD"
    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if input_date < datetime.now().date():
            return False, "日期不能早於今天"
        return True, ""
    except ValueError:
        return False, "無效日期"

def process_excel_upload(uploaded_file, batch_id, customer_name, floor, w1):
    """處理 Excel 上傳 - 加入樓層參數"""
    try:
        df_raw = pd.read_excel(uploaded_file, engine='openpyxl', header=None).fillna('')
        header_row = [str(x).strip().upper() for x in df_raw.iloc[0].tolist()]
        mapping = CONFIG["EXCEL_MAPPING"]
        col_idx = {k: next((i for i, v in enumerate(header_row) if any(a in v for a in v_list)), 0) for k, v_list in mapping.items()}
        
        # 保留客戶名稱原始大小寫（與左側面板一致）
        db.create_batch(batch_id, customer_name.strip(), status='pending', source='Client', floor=floor)
        
        for i, row in df_raw.iloc[1:].iterrows():
            product_data = (batch_id, str(i), str(row[col_idx['Barcode']]), str(row[col_idx['SKU ID']]), str(row[col_idx['產品名稱']]), str(row[col_idx['預計數量']]), "", "", "", w1, "", "", "")
            db.insert_product(product_data)
        return True, "建立成功！"
    except Exception as e:
        return False, f"處理失敗：{str(e)}"

def validate_scan_and_save(batch_id, scan_code, new_qty, new_bbd, new_loc, worker1, worker2, task_df):
    if not new_qty.replace('.', '', 1).isdigit() or not new_loc:
        return False, "❌ 請輸入有效的數量與儲位", "error"

    bbd_str = str(new_bbd).strip()
    is_valid, err_msg = is_valid_expiry_date(bbd_str)
    if not is_valid: return False, f"❌ 到期日錯誤：{err_msg}", "error"

    sku_records = task_df[task_df['barcode'].astype(str) == scan_code]
    if sku_records.empty: return False, f"❌ 找不到條碼：{scan_code}", "error"

    base_item = sku_records.iloc[0]
    input_val = float(new_qty)
    expected_total = float(pd.to_numeric(base_item['expected_qty'], errors='coerce') or 0)

    occupant = task_df[task_df['location'].str.upper() == new_loc]
    if not occupant.empty:
        occ = occupant.iloc[0]
        if str(occ['sku_id']) == str(base_item['sku_id']) and str(occ['expiry_date']) == bbd_str:
            new_total = float(occ['actual_qty'] or 0) + input_val
            success = db.update_product_qty(batch_id, occ['seq'], new_total, worker1, worker2)
            if not success:
                return False, "❌ 更新失敗，請檢查資料庫連線", "error"
        else:
            return False, f"❌ 庫位 [{new_loc}] 已被佔用！", "error"
    else:
        empty_rows = sku_records[sku_records['location'] == ""]
        target_seq = empty_rows.iloc[0]['seq'] if not empty_rows.empty else f"{base_item['seq'].split('.')[0]}.{len(sku_records)}"
        product_data = (batch_id, target_seq, scan_code, base_item['sku_id'], base_item['product_name'], 
                        base_item['expected_qty'], str(input_val), new_loc, bbd_str, worker1, worker2, 
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), base_item.get('lot', ''))
        success = db.insert_product(product_data)
        if not success:
            return False, "❌ 寫入失敗，請檢查資料庫連線", "error"

    updated_df = db.get_products_by_batch(batch_id)
    current_total = pd.to_numeric(updated_df[updated_df['sku_id'] == base_item['sku_id']]['actual_qty'], errors='coerce').sum()
    
    base_style = "padding: 15px; border-radius: 5px; margin-bottom: 10px; font-weight: bold; text-align: center; color: white;"
    if current_total > expected_total:
        bg = CONFIG["UI_COLORS"]["RED"]
        msg = f"⚠️ 超收！(預計 {int(expected_total)}, 實收 {int(current_total)})"
    elif current_total < expected_total:
        bg = CONFIG["UI_COLORS"]["BLUE"]
        msg = f"⚠️ 少收！(預計 {int(expected_total)}, 實收 {int(current_total)})"
    else:
        bg = CONFIG["UI_COLORS"]["GREEN"]
        msg = f"✅ 數量正確 (實收 {int(current_total)})"
    
    return True, f'<div style="{base_style} background-color: {bg};">{msg}</div>', "success"

def get_reports_for_download(batch_id):
    try:
        batch_info = db.get_batch_info(batch_id)
        df = db.get_products_by_batch(batch_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        ivr_data = _generate_ivr_excel_bytes(batch_id, batch_info, df)
        std_data = _generate_std_excel_bytes(batch_id, batch_info, df)
        return {"ivr": {"filename": f"IVR_{batch_id}_{timestamp}.xlsx", "data": ivr_data}, "std": {"filename": f"Inbound_{batch_id}_{timestamp}.xlsx", "data": std_data}}
    except: return None

def export_reports_to_files(batch_id):
    try:
        reports = get_reports_for_download(batch_id)
        if not reports: return False, "生成失敗"
        save_dir = CONFIG["PATHS"]["EXPORT_DIR"]
        if not os.path.exists(save_dir): os.makedirs(save_dir, exist_ok=True)
        for key in ["ivr", "std"]:
            path = os.path.join(save_dir, reports[key]["filename"])
            with open(path, "wb") as f: f.write(reports[key]["data"])
        return True, f"報告已自動存至 {save_dir}"
    except Exception as e:
        return False, str(e)

def _generate_ivr_excel_bytes(batch_id, batch_info, df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('IVR_Report')
        fmts = get_excel_formats(workbook)
        worksheet.merge_range('A1:H1', '入庫差異報告', fmts['title'])
        inbound_date = batch_info['created_at'].split(' ')[0] if batch_info and batch_info['created_at'] else "N/A"
        worksheet.write('A2', f"客戶名稱：{batch_info['customer_name'] if batch_info else 'N/A'}", fmts['info'])
        worksheet.write('A3', f"入庫日期：{inbound_date}", fmts['info'])
        worksheet.write('A4', f"文件編號：{batch_id}", fmts['info'])
        headers = ['次序', 'SKU ID', 'Barcode', '預報數量', '實收數量', '差異數量', '批次號', '產品到期日']
        for col, text in enumerate(headers): worksheet.write(5, col, text, fmts['header'])
        for i, row in df.iterrows():
            exp = float(row['expected_qty'] or 0)
            act = float(row['actual_qty'] or 0)
            diff = exp - act
            worksheet.write(6 + i, 0, i + 1, fmts['cell'])
            worksheet.write(6 + i, 1, row['sku_id'], fmts['cell'])
            worksheet.write(6 + i, 2, row['barcode'], fmts['cell'])
            worksheet.write(6 + i, 3, int(exp), fmts['cell'])
            worksheet.write(6 + i, 4, int(act), fmts['cell'])
            worksheet.write(6 + i, 5, f"+{int(diff)}" if diff > 0 else str(int(diff)), fmts['cell'])
            worksheet.write(6 + i, 6, row.get('lot', ''), fmts['cell'])
            worksheet.write(6 + i, 7, row['expiry_date'], fmts['cell'])
        worksheet.set_column('A:A', 8); worksheet.set_column('B:C', 20)
        worksheet.set_column('D:F', 12); worksheet.set_column('G:H', 20)
    return output.getvalue()

def _generate_std_excel_bytes(batch_id, batch_info, df):
    """生成標準入庫報告 - 按照指定格式排列"""
    output = io.BytesIO()
    
    # 獲取客戶名稱
    customer_name = batch_info['customer_name'] if batch_info else 'N/A'
    
    # 預期到貨日期 = today()
    expected_arrival_date = datetime.now().strftime('%Y-%m-%d')
    
    # 倉庫名稱 = KC
    warehouse_name = 'KC'
    
    # 基本單位 = Units
    unit = 'Units'
    
    # 批次號邏輯：COBOLIFE/LINBERG 用 LOT，其他用 YYMMDDUD
    today_str = datetime.now().strftime('%y%m%d') + 'UD'
    
    # 貨位前綴
    location_prefix = 'ZONE/5/F/'
    
    # 建立新格式的 DataFrame
    formatted_data = []
    
    # 只選取有入庫數據的記錄
    df_with_data = df[pd.to_numeric(df['actual_qty'], errors='coerce').fillna(0) > 0].copy()
    
    for _, row in df_with_data.iterrows():
        # 批次號邏輯
        lot = row.get('lot', '')
        if lot and ('COBOLIFE' in customer_name or 'LINBERG' in customer_name):
            batch_no = lot
        else:
            batch_no = today_str
        
        # 貨位加上前綴
        location = location_prefix + row['location'] if row['location'] else ''
        
        formatted_data.append({
            '客戶名稱': customer_name,
            '預期到貨日期': expected_arrival_date,
            '倉庫名稱': warehouse_name,
            'SKU ID': row['sku_id'],
            '預期數量': int(float(row['expected_qty'] or 0)),
            '基本單位': unit,
            '到期日期': row['expiry_date'],
            '批次號': batch_no,
            '貨位': location
        })
    
    formatted_df = pd.DataFrame(formatted_data)
    
    # 按照指定順序排列欄位
    column_order = ['客戶名稱', '預期到貨日期', '倉庫名稱', 'SKU ID', '預期數量', '基本單位', '到期日期', '批次號', '貨位']
    formatted_df = formatted_df[column_order]
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        formatted_df.to_excel(writer, index=False, sheet_name='Inbound_Report')
        workbook = writer.book
        worksheet = writer.sheets['Inbound_Report']
        
        # 設置欄位寬度
        worksheet.set_column('A:A', 15)  # 客戶名稱
        worksheet.set_column('B:B', 12)  # 預期到貨日期
        worksheet.set_column('C:C', 10)  # 倉庫名稱
        worksheet.set_column('D:D', 15)  # SKU ID
        worksheet.set_column('E:E', 10)  # 預期數量
        worksheet.set_column('F:F', 10)  # 基本單位
        worksheet.set_column('G:G', 12)  # 到期日期
        worksheet.set_column('H:H', 12)  # 批次號
        worksheet.set_column('I:I', 15)  # 貨位
    
    return output.getvalue()
