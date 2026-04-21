import streamlit as st
import database as db
from config import CONFIG
import pandas as pd

def show_office_admin():
    st.title("🖥️ Office 管理後台")
    
    # 獲取待審核數據
    pending_batches = db.get_batches_by_status([CONFIG["STATUS"]["CLIENT_SUBMITTED"]])
    
    if pending_batches.empty:
        st.info("目前沒有待處理的入庫申請。")
    else:
        st.subheader(f"🔔 待審核申請 ({len(pending_batches)})")
        
        for i, row in pending_batches.iterrows():
            with st.expander(f"📄 {row['batch_id']} - {row['customer_name']} (提交時間: {row['created_at']})"):
                # 顯示該批次的產品細節
                products = db.get_products_by_batch(row['batch_id'])
                st.table(products[['SKU ID', 'Barcode', '產品名稱', '預計數量', '到期日期']])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ 確認並生成工作日誌", key=f"app_{row['batch_id']}"):
                        db.update_batch_status(row['batch_id'], CONFIG["STATUS"]["OFFICE_APPROVED"])
                        st.success(f"批次 {row['batch_id']} 已發放至倉庫作業清單。")
                        st.rerun()
                with col2:
                    if st.button(f"❌ 拒絕申請", key=f"rej_{row['batch_id']}"):
                        db.delete_batch(row['batch_id'])
                        st.warning("已拒絕並刪除該申請。")
                        st.rerun()
