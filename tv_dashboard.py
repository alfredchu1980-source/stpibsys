# tv_dashboard.py
import streamlit as st
import pandas as pd
from config import CONFIG
import database as db

def show_tv_dashboard():
    """電視看板頁面"""
    st.title("📺 電視看板")
    
    # 獲取所有活躍批次
    all_active = db.get_batches_by_status(["Active", "pending"])
    
    if all_active.empty:
        st.info("目前沒有活躍的批次")
        return
    
    st.markdown("### 📊 活躍批次概覽")
    st.dataframe(all_active, use_container_width=True)
    
    st.divider()
    
    st.markdown("### 📦 各批次入庫進度")
    
    for _, batch_row in all_active.iterrows():
        batch_id = batch_row['batch_id']
        products = db.get_products_by_batch(batch_id)
        
        if not products.empty:
            # 計算進度
            total_expected = pd.to_numeric(products['expected_qty'], errors='coerce').sum()
            total_actual = pd.to_numeric(products['actual_qty'], errors='coerce').sum()
            progress = total_actual / total_expected if total_expected > 0 else 0
            
            st.markdown(f"**{batch_id}** - 客戶：{batch_row.get('customer_name', 'N/A')}")
            st.progress(progress)
            st.caption(f"預計：{int(total_expected)} | 實收：{int(total_actual)} ({progress*100:.1f}%)")
            st.divider()
