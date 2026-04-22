# utils.py
import streamlit as st
from datetime import datetime
import pandas as pd

def write_audit_log(username, action, details):
    """寫入審核日誌到 Supabase"""
    try:
        from database import supabase
        data = {
            "username": username,
            "action": action,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_address": "Unknown"
        }
        supabase.table("audit_logs").insert(data).execute()
    except Exception as e:
        pass

def play_audio(sound_type):
    """播放音效"""
    pass

def style_rows(row):
    """表格樣式 - 修復類型比較錯誤"""
    styles = []
    for col in row.index:
        if col == '入庫':
            try:
                # 轉換為數字再比較
                val = pd.to_numeric(row[col], errors='coerce')
                if val > 0:
                    styles.append('background-color: #28a745; color: white')
                else:
                    styles.append('')
            except:
                styles.append('')
        else:
            styles.append('')
    return styles

def get_excel_formats(workbook):
    """Excel 格式設定"""
    return {
        'title': workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'}),
        'info': workbook.add_format({'font_size': 11}),
        'header': workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'border': 1}),
        'cell': workbook.add_format({'border': 1})
    }
