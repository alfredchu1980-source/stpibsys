# office_admin.py
import streamlit as st
import pandas as pd
from config import CONFIG
import database as db
from utils import write_audit_log

def show_office_admin():
    """Office 管理頁面 - 加入批准/退回功能"""
    st.title("🖥️ Office 管理")
    
    if st.session_state.role != "Admin":
        st.error("❌ 只有 Admin 可以訪問此頁面")
        return
    
    st.markdown("### 📊 待審核預報（pending）")
    
    pending_batches = db.get_batches_by_status(["pending"])
    
    if pending_batches.empty:
        st.info("✅ 目前沒有待審核的預報")
    else:
        for _, batch in pending_batches.iterrows():
            floor = batch.get('floor', '3F')
            temp_icon = "🌡️" if floor == "3F" else "☀️"
            floor_name = "3F（冷凍/冷藏）" if floor == "3F" else "5F（常溫）"
            
            with st.expander(f"{temp_icon} {batch['batch_id']} - {batch['customer_name']}（提交時間：{batch['created_at']}）", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**來源**: {batch.get('source', 'N/A')}")
                    st.write(f"**樓層**: {floor_name}")
                    st.write(f"**狀態**: {batch['status']}")
                
                products = db.get_products_by_batch(batch['batch_id'])
                if not products.empty:
                    st.write(f"**產品數量**: {len(products)} 項")
                    display_cols = ['sku_id', 'barcode', 'product_name', 'expected_qty']
                    available_cols = [col for col in display_cols if col in products.columns]
                    st.dataframe(products[available_cols], use_container_width=True)
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("✅ 批准", key=f"approve_{batch['batch_id']}", use_container_width=True):
                        if db.update_batch_status(batch['batch_id'], 'Active'):
                            st.success("✅ 已批准並轉移到倉庫！")
                            write_audit_log(st.session_state.username, f"批准預報：{batch['batch_id']}", "轉移到倉庫")
                            st.rerun()
                    if st.button("❌ 退回", key=f"reject_{batch['batch_id']}", use_container_width=True):
                        if db.delete_batch(batch['batch_id']):
                            st.success("❌ 已退回")
                            st.rerun()
    
    st.divider()
    
    st.markdown("### 📊 所有批次列表")
    all_batches = db.get_batches_by_status(["pending", "Active", "completed"])
    if all_batches.empty:
        st.info("尚無批次數據")
        return
    st.dataframe(all_batches, use_container_width=True)
    
    st.divider()
    st.markdown("### 📦 選擇批次查看詳情")
    batch_list = all_batches['batch_id'].tolist()
    selected_batch = st.selectbox("選擇批次", batch_list)
    if selected_batch:
        products = db.get_products_by_batch(selected_batch)
        if not products.empty:
            st.markdown(f"#### {selected_batch} 產品清單")
            display_cols = ['sku_id', 'barcode', 'product_name', 'expected_qty', 'expiry_date', 'actual_qty', 'location']
            available_cols = [col for col in display_cols if col in products.columns]
            st.dataframe(products[available_cols], use_container_width=True)
        else:
            st.info("該批次尚無產品數據")
