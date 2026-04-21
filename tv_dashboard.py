import streamlit as st
import database as db
from config import CONFIG
import pandas as pd
from datetime import datetime

def show_tv_dashboard():
    st.title("📺 倉庫入庫看板 (60 吋電視專用)")
    
    # 獲取所有未完成的批次 (包含 V70 原有的 pending 狀態)
    all_active = db.get_batches_by_status([
        CONFIG["STATUS"]["OFFICE_APPROVED"], 
        CONFIG["STATUS"]["CLIENT_SUBMITTED"],
        CONFIG["STATUS"]["PENDING"]
    ])
    
    if all_active.empty:
        st.info("目前沒有待處理的入庫任務。")
    else:
        # 準備看板數據
        dashboard_data = []
        for i, row in all_active.iterrows():
            # 計算天數 (Aging)
            try:
                created_at = datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S")
                days_diff = (datetime.now() - created_at).days
            except:
                days_diff = 0
            
            # 獲取項目數和總件數
            products = db.get_products_by_batch(row['batch_id'])
            sku_count = len(products)
            total_qty = pd.to_numeric(products['預計數量'], errors='coerce').sum()
            
            # 顏色邏輯
            color = "white"
            is_flashing = False
            
            if row['status'] == CONFIG["STATUS"]["COMPLETED"]:
                color = "green"
            elif days_diff >= CONFIG["AGING"]["FLASH"]:
                color = "red"
                is_flashing = True
            elif days_diff >= CONFIG["AGING"]["RED"]:
                color = "red"
            elif days_diff >= CONFIG["AGING"]["YELLOW"]:
                color = "yellow"
            
            dashboard_data.append({
                "客戶名稱": row['customer_name'],
                "入庫日期": row['created_at'].split(' ')[0] if row['created_at'] else "N/A",
                "項目數": sku_count,
                "總件數": int(total_qty),
                "狀態": row['status'],
                "天數": days_diff,
                "color": color,
                "is_flashing": is_flashing
            })
            
        # 顯示看板表格 (帶有 CSS 樣式)
        st.markdown("""
            <style>
            .dashboard-table { width: 100%; border-collapse: collapse; font-size: 24px; }
            .dashboard-table th { background-color: #333; color: white; padding: 15px; }
            .dashboard-table td { padding: 15px; border-bottom: 1px solid #ddd; }
            .color-green { background-color: #2d5a27; color: white; }
            .color-yellow { background-color: #f1c40f; color: black; }
            .color-red { background-color: #e74c3c; color: white; }
            .flashing { animation: blinker 1s linear infinite; }
            @keyframes blinker { 50% { opacity: 0; } }
            </style>
        """, unsafe_allow_html=True)
        
        html = '<table class="dashboard-table"><tr><th>客戶名稱</th><th>入庫日期</th><th>項目數</th><th>總件數</th><th>狀態</th></tr>'
        for d in dashboard_data:
            flash_class = "flashing" if d['is_flashing'] else ""
            html += f'<tr class="color-{d["color"]} {flash_class}">'
            html += f'<td>{d["客戶名稱"]}</td><td>{d["入庫日期"]}</td><td>{d["項目數"]}</td><td>{d["總件數"]}</td><td>{d["狀態"]}</td></tr>'
        html += '</table>'
        
        st.markdown(html, unsafe_allow_html=True)
