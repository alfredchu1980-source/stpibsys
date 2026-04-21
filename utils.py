# utils.py
import pandas as pd
import requests
import os
from datetime import datetime
import streamlit as st
from config import CONFIG

def write_audit_log(staff, action, batch_id, details=""):
    """記錄操作日誌到本地"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_dir = CONFIG["PATHS"]["LOG_DIR"]
    if not os.path.exists(log_dir): os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, "operation_log.csv")
    log_df = pd.DataFrame([{"時間": now, "人員": staff, "動作": action, "批次編號": batch_id, "詳細資訊": details}])
    try:
        header = not os.path.isfile(log_path)
        log_df.to_csv(log_path, mode='a', index=False, header=header, encoding="utf-8-sig")
    except: pass

def play_audio(sound_type):
    """播放提示音"""
    sound_url = CONFIG["SOUNDS"].get(sound_type)
    if sound_url:
        st.components.v1.html(f'<audio autoplay><source src="{sound_url}" type="audio/ogg"></audio>', height=0)

def style_rows(row):
    """表格高亮邏輯"""
    colors = CONFIG["UI_COLORS"]
    try:
        actual = float(row['入庫']) if '入庫' in row and row['入庫'] else 0
        expected = float(row['exp_val']) if 'exp_val' in row else 0
    except: actual, expected = 0, 0

    if '位置' in row and row['位置']:
        if "." in str(row['#']): return [f'background-color: {colors["ORANGE"]}; color: white;'] * len(row)
        if actual == expected: return [f'background-color: {colors["GREEN"]}; color: white;'] * len(row)
        if actual > expected: return [f'background-color: {colors["RED"]}; color: white;'] * len(row)
        else: return [f'background-color: {colors["BLUE"]}; color: white;'] * len(row)
    return [f'color: {colors["GREY"]};'] * len(row)

def get_excel_formats(workbook):
    """Excel 樣式"""
    return {
        'title': workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'}),
        'header': workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#D9D9D9', 'align': 'center'}),
        'cell': workbook.add_format({'border': 1, 'align': 'center'}),
        'info': workbook.add_format({'bold': True})
    }
