# reference_module/ref_table.py
"""
參考表核心邏輯
讀取、查詢、更新參考表 (CSV 格式)
"""

import pandas as pd
import os
from datetime import datetime

# 從 hooks.py 讀取配置
try:
    from hooks import (
        REFERENCE_TABLE_PATH,
        REFERENCE_BARCODE_COLUMN,
        REFERENCE_LOCATION_COLUMN,
        REFERENCE_EXPIRY_COLUMN
    )
except ImportError:
    # 預設配置
    REFERENCE_TABLE_PATH = "./data/reference_table.csv"
    REFERENCE_BARCODE_COLUMN = 0
    REFERENCE_LOCATION_COLUMN = 4
    REFERENCE_EXPIRY_COLUMN = 5

# 快取變數
_reference_cache = None
_cache_timestamp = None


def _ensure_data_dir():
    """確保 data 資料夾存在"""
    data_dir = os.path.dirname(REFERENCE_TABLE_PATH)
    os.makedirs(data_dir, exist_ok=True)


def _load_csv():
    """讀取 CSV 檔案（帶快取機制）"""
    global _reference_cache, _cache_timestamp
    
    # 檢查檔案是否存在
    if not os.path.exists(REFERENCE_TABLE_PATH):
        return None
    
    # 檢查檔案是否更新
    file_mtime = os.path.getmtime(REFERENCE_TABLE_PATH)
    if _reference_cache is not None and _cache_timestamp == file_mtime:
        return _reference_cache
    
    # 讀取 CSV
    try:
        # 先讀取完整 CSV 以獲取 barcode
        full_df = pd.read_csv(
            REFERENCE_TABLE_PATH,
            encoding='utf-8-sig',  # 支援中文 BOM 編碼
            header=0,  # 第一列是 header
            dtype=str  # 全部讀為文字
        )
        
        # 驗證欄位數量
        if len(full_df.columns) <= max(REFERENCE_LOCATION_COLUMN, REFERENCE_EXPIRY_COLUMN):
            print(f"警告：CSV 欄位不足，需要至少 {max(REFERENCE_LOCATION_COLUMN, REFERENCE_EXPIRY_COLUMN) + 1} 個欄位")
            return None
        
        # 清除空值
        full_df = full_df.dropna(subset=[full_df.columns[REFERENCE_BARCODE_COLUMN]])
        
        # 更新快取
        _reference_cache = full_df
        _cache_timestamp = file_mtime
        
        return full_df
    except Exception as e:
        print(f"讀取參考表失敗：{e}")
        return None


def search_by_barcode(barcode):
    """
    根據條碼搜尋參考資料
    
    參數:
        barcode: 產品條碼
    
    回傳:
        list: 包含 location 和 expiry_date 的字典列表，按到期日升序排列
    """
    df = _load_csv()
    
    if df is None or df.empty:
        return []
    
    try:
        # 獲取欄位名稱
        barcode_col = df.columns[REFERENCE_BARCODE_COLUMN]
        location_col = df.columns[REFERENCE_LOCATION_COLUMN]
        expiry_col = df.columns[REFERENCE_EXPIRY_COLUMN]
        
        # 搜尋符合條碼的記錄
        results = df[df[barcode_col].astype(str) == str(barcode)].copy()
        
        if results.empty:
            return []
        
        # 只保留 location 和 expiry_date
        results = results[[location_col, expiry_col]].copy()
        results.columns = ['location', 'expiry_date']
        
        # 將 NaN 轉換為空字串（保留記錄但顯示為空）
        results['location'] = results['location'].fillna('')
        results['expiry_date'] = results['expiry_date'].fillna('')
        
        # 按到期日升序排列（空值會排在最後）
        results = results.sort_values('expiry_date', ascending=True)
        
        # 轉換為字典列表
        return results.to_dict('records')
    
    except Exception as e:
        print(f"搜尋條碼失敗：{e}")
        return []


def get_reference_info():
    """
    獲取參考表統計資訊
    
    回傳:
        dict: 包含總記錄數、最後更新時間等資訊
    """
    if not os.path.exists(REFERENCE_TABLE_PATH):
        return None
    
    try:
        df = _load_csv()
        
        if df is None:
            return None
        
        file_mtime = os.path.getmtime(REFERENCE_TABLE_PATH)
        last_updated = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'total_records': len(df),
            'last_updated': last_updated,
            'file_path': REFERENCE_TABLE_PATH,
            'file_size_kb': round(os.path.getsize(REFERENCE_TABLE_PATH) / 1024, 2)
        }
    except Exception as e:
        print(f"獲取參考表資訊失敗：{e}")
        return None


def update_reference_table(uploaded_file):
    """
    更新參考表（上傳新 CSV 檔案）
    
    參數:
        uploaded_file: Streamlit uploaded file object
    
    回傳:
        tuple: (success: bool, message: str)
    """
    try:
        _ensure_data_dir()
        
        # 讀取上傳的 CSV
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig', dtype=str)
        
        # 驗證必要欄位（至少需要有 6 個欄位）
        required_columns = max(REFERENCE_LOCATION_COLUMN, REFERENCE_EXPIRY_COLUMN) + 1
        if len(df.columns) < required_columns:
            return False, f"❌ CSV 檔案欄位不足，需要至少 {required_columns} 個欄位 (Column A-F)"
        
        # 驗證 Column E (location) 和 F (expiry_date) 不為空
        location_col = df.columns[REFERENCE_LOCATION_COLUMN]
        expiry_col = df.columns[REFERENCE_EXPIRY_COLUMN]
        
        if df[location_col].isna().all() or df[expiry_col].isna().all():
            return False, "❌ Column E (位置) 或 Column F (到期日) 為空"
        
        # 保存新參考表
        df.to_csv(REFERENCE_TABLE_PATH, index=False, encoding='utf-8-sig')
        
        # 清除快取
        global _reference_cache, _cache_timestamp
        _reference_cache = None
        _cache_timestamp = None
        
        # 獲取新檔案資訊
        info = get_reference_info()
        
        return True, f"✅ 參考表更新成功！總記錄數：{info['total_records']:,}"
    
    except Exception as e:
        return False, f"❌ 更新失敗：{str(e)}"


def clear_cache():
    """清除快取（強制重新讀取 CSV）"""
    global _reference_cache, _cache_timestamp
    _reference_cache = None
    _cache_timestamp = None
