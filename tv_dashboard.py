# tv_dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config import CONFIG
import database as db

def show_tv_dashboard():
    """電視看板頁面 - 顯示所有入庫記錄狀態"""
    st.title("📺 電視看板")
    
    # 獲取所有活躍批次
    all_active = db.get_batches_by_status(["Active", "pending", "completed"])
    
    if all_active.empty:
        st.info("目前沒有活躍的批次")
        return
    
    # 計算延遲天數並標記顏色
    today = datetime.now()
    
    def calculate_delay_status(row):
        """計算延遲狀態並返回顏色和說明"""
        status = row.get('status', '')
        created_at_str = row.get('created_at', '')
        
        # 完成狀態 - 綠色
        if status == "completed":
            return {
                "bg_color": "#d4edda",
                "text_color": "#155724",
                "delay_days": 0,
                "status_text": "✅ 已完成",
                "flashing": False
            }
        
        # 計算延遲天數
        try:
            created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
            days_elapsed = (today - created_at).days
        except:
            days_elapsed = 0
        
        # 延遲 3 天以上 - 紅色閃爍
        if days_elapsed >= 3:
            return {
                "bg_color": "#f8d7da",
                "text_color": "#721c24",
                "delay_days": days_elapsed,
                "status_text": f"⚠️ 延遲 {days_elapsed} 天",
                "flashing": True
            }
        # 延遲 2 天 - 黃色
        elif days_elapsed == 2:
            return {
                "bg_color": "#fff3cd",
                "text_color": "#856404",
                "delay_days": days_elapsed,
                "status_text": f"⚠️ 延遲 {days_elapsed} 天",
                "flashing": False
            }
        # 延遲 1 天 - 藍色
        elif days_elapsed == 1:
            return {
                "bg_color": "#cce5ff",
                "text_color": "#004085",
                "delay_days": days_elapsed,
                "status_text": f"⚠️ 延遲 {days_elapsed} 天",
                "flashing": False
            }
        # 正常 - 無顏色
        else:
            return {
                "bg_color": "#ffffff",
                "text_color": "#212529",
                "delay_days": 0,
                "status_text": "🕐 進行中",
                "flashing": False
            }
    
    # 應用狀態計算
    status_info = all_active.apply(calculate_delay_status, axis=1)
    all_active['bg_color'] = status_info.apply(lambda x: x['bg_color'])
    all_active['text_color'] = status_info.apply(lambda x: x['text_color'])
    all_active['delay_days'] = status_info.apply(lambda x: x['delay_days'])
    all_active['status_text'] = status_info.apply(lambda x: x['status_text'])
    all_active['flashing'] = status_info.apply(lambda x: x['flashing'])
    
    # 顯示統計摘要
    st.markdown("### 📊 統計摘要")
    col1, col2, col3, col4 = st.columns(4)
    
    completed_count = len(all_active[all_active['status'] == 'completed'])
    delay3_count = len(all_active[all_active['delay_days'] >= 3])
    delay2_count = len(all_active[all_active['delay_days'] == 2])
    delay1_count = len(all_active[all_active['delay_days'] == 1])
    
    with col1:
        st.metric("✅ 已完成", completed_count)
    with col2:
        st.metric("⚠️ 延遲 1 天", delay1_count)
    with col3:
        st.metric("⚠️ 延遲 2 天", delay2_count)
    with col4:
        st.metric("🔴 延遲 3 天+", delay3_count)
    
    st.divider()
    
    # 顯示所有批次狀態
    st.markdown("### 📋 所有入庫記錄狀態")
    
    # 添加 CSS 樣式 - 高對比度顏色，易於閱讀
    st.markdown("""
    <style>
    @keyframes flash {
        0%, 50%, 100% { opacity: 1; }
        25%, 75% { opacity: 0.6; }
    }
    .tv-dashboard-table {
        font-size: 18px;
        font-family: Arial, sans-serif;
    }
    .tv-dashboard-table th {
        font-size: 20px;
        font-weight: bold;
        padding: 15px;
        background-color: #343a40;
        color: #ffffff;
        text-align: left;
        border: 2px solid #dee2e6;
    }
    .tv-dashboard-table td {
        font-size: 18px;
        padding: 15px;
        border: 1px solid #dee2e6;
        font-weight: 500;
    }
    .flash-row {
        animation: flash 1s infinite;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 選擇要顯示的欄位（移除來源 column）
    display_columns = ['batch_id', 'customer_name', 'status', 'floor', 'created_at', 'status_text']
    display_df = all_active[display_columns].copy()
    
    # 使用 HTML 表格顯示以支援顏色和字體大小
    html_table = '<div class="tv-dashboard-table"><table style="width: 100%; border-collapse: collapse;">'
    
    # 表頭
    column_names = {
        'batch_id': '批次編號',
        'customer_name': '客戶名稱',
        'status': '狀態',
        'floor': '樓層',
        'created_at': '建立日期',
        'status_text': '狀態說明'
    }
    
    html_table += '<thead><tr>'
    for col in display_columns:
        html_table += f'<th style="padding: 15px; text-align: left; border: 2px solid #dee2e6;">{column_names[col]}</th>'
    html_table += '</tr></thead>'
    
    # 表體
    html_table += '<tbody>'
    for idx, row in display_df.iterrows():
        bg_color = all_active.loc[idx, 'bg_color']
        text_color = all_active.loc[idx, 'text_color']
        flashing = all_active.loc[idx, 'flashing']
        
        if flashing:
            style_attr = f'background-color: {bg_color}; color: {text_color}; animation: flash 1s infinite;'
        else:
            style_attr = f'background-color: {bg_color}; color: {text_color};'
        
        html_table += f'<tr style="{style_attr}">'
        for col in display_columns:
            cell_value = row[col]
            if col == 'created_at':
                try:
                    cell_value = datetime.strptime(str(cell_value), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            html_table += f'<td style="padding: 15px; border: 1px solid #dee2e6; font-size: 18px;">{cell_value}</td>'
        html_table += '</tr>'
    
    html_table += '</tbody></table></div>'
    
    st.markdown(html_table, unsafe_allow_html=True)
    
    # 顯示顏色圖例
    st.divider()
    st.markdown("### 🎨 顏色說明")
    
    col_legend1, col_legend2, col_legend3, col_legend4 = st.columns(4)
    
    with col_legend1:
        st.markdown("""
        <div style="background-color: #d4edda; color: #155724; padding: 20px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold;">
            ✅ 已完成<br>
            <span style="font-size: 14px; font-weight: normal;">status = completed</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_legend2:
        st.markdown("""
        <div style="background-color: #cce5ff; color: #004085; padding: 20px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold;">
            ⚠️ 延遲 1 天<br>
            <span style="font-size: 14px; font-weight: normal;">created_at + 1 天</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_legend3:
        st.markdown("""
        <div style="background-color: #fff3cd; color: #856404; padding: 20px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold;">
            ⚠️ 延遲 2 天<br>
            <span style="font-size: 14px; font-weight: normal;">created_at + 2 天</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_legend4:
        st.markdown("""
        <div style="background-color: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold; animation: flash 1s infinite;">
            🔴 延遲 3 天+<br>
            <span style="font-size: 14px; font-weight: normal;">created_at + 3 天以上</span>
        </div>
        """, unsafe_allow_html=True)
