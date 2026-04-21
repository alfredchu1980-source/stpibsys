import streamlit as st
import pandas as pd
from datetime import datetime
import io
from config import CONFIG
import database as db
import services # 引入 services 以使用日期校驗

def generate_template_excel():
    """生成包含標準標題行的 Excel 範本"""
    output = io.BytesIO()
    headers = CONFIG["EXCEL_TEMPLATE"]["REQUIRED_HEADERS"]
    # 建立一個空的 DataFrame，只包含標題
    df = pd.DataFrame(columns=headers)
    # 加入一行範例數據
    example_row = {
        "SKU_ID": "SKU001",
        "BARCODE": "4891234567890",
        "PRODUCT_NAME": "範例產品 A",
        "EXPECTED_QTY": 100,
        "EXPIRY_DATE": "2026-12-31"
    }
    df = pd.concat([df, pd.DataFrame([example_row])], ignore_index=True)
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Template')
        # 可以在這裡加入一些格式化，讓標題更明顯
        workbook = writer.book
        worksheet = writer.sheets['Template']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)
            
    return output.getvalue()

def show_client_portal():
    st.title("📦 客戶自助入庫預報")
    st.info("請下載標準範本填寫後上傳。")
    
    # 1. 下載範本按鈕 (生成真實的 Excel 檔案)
    template_data = generate_template_excel()
    st.download_button(
        label="📥 下載標準入庫範本.xlsx",
        data=template_data,
        file_name="Inbound_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    # 2. 客戶填寫基本資料
    cust_name = st.text_input("🏢 客戶名稱")
    uploaded_file = st.file_uploader("📤 上傳預報 Excel", type=["xlsx"])
    
    if uploaded_file and cust_name:
        try:
            df = pd.read_excel(uploaded_file).fillna('')
            
            # --- 嚴格校驗邏輯 ---
            # A. 標題行檢查
            required = CONFIG["EXCEL_TEMPLATE"]["REQUIRED_HEADERS"]
            current_headers = [str(h).upper() for h in df.columns]
            missing = [h for h in required if h not in current_headers]
            
            if missing:
                st.error(f"❌ 格式錯誤：找不到欄位 {missing}，請使用標準範本。")
                return

            # B. 必填項檢查 (SKU_ID, BARCODE, EXPECTED_QTY)
            if df['SKU_ID'].astype(str).str.strip().eq('').any() or \
               df['BARCODE'].astype(str).str.strip().eq('').any() or \
               df['EXPECTED_QTY'].astype(str).str.strip().eq('').any():
                st.error("❌ 必填項檢查失敗：SKU_ID, BARCODE, EXPECTED_QTY 不能為空。")
                return

            # C. 數據格式檢查 (數量必須是數字)
            if not pd.to_numeric(df['EXPECTED_QTY'], errors='coerce').notnull().all():
                st.error("❌ 數據格式錯誤：'EXPECTED_QTY' 欄位只能填寫數字。")
                return

            # D. 嚴格到期日校驗 (Excel 每一行)
            for i, row in df.iterrows():
                bbd_val = str(row['EXPIRY_DATE']).strip()
                is_valid, err_msg = services.is_valid_expiry_date(bbd_val)
                if not is_valid:
                    st.error(f"❌ 第 {i+2} 行到期日錯誤: {err_msg}")
                    return

            # E. 重複條碼檢查
            duplicates = df[df.duplicated(['BARCODE'], keep=False)]
            if not duplicates.empty:
                st.warning("⚠️ 發現重複條碼，請確認是否正確？")
                st.dataframe(duplicates)
                if not st.button("✅ 確認無誤，繼續提交"):
                    return

            # --- 寫入緩衝區 ---
            if st.button("🚀 提交入庫申請"):
                batch_id = f"REQ{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # 寫入 batches 表 (狀態為 Client_Submitted)
                if db.create_batch(batch_id, cust_name, status=CONFIG["STATUS"]["CLIENT_SUBMITTED"], source="Client"):
                    # 寫入 products 表
                    for i, row in df.iterrows():
                        product_data = (
                            batch_id, str(i+1), str(row['BARCODE']), str(row['SKU_ID']), 
                            str(row['PRODUCT_NAME']), str(row['EXPECTED_QTY']), "", "", 
                            str(row['EXPIRY_DATE']), "", "", "", ""
                        )
                        db.insert_product(product_data)
                    
                    st.success(f"✅ 提交成功！您的申請編號為：{batch_id}")
                    st.balloons()
                
        except Exception as e:
            st.error(f"❌ 處理失敗: {str(e)}")
