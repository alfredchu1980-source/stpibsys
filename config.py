# config.py
import os

# 獲取啟動時的預設樓層 (從環境變數讀取)
DEFAULT_FLOOR = os.getenv("SHOPTO_FLOOR", "5F").upper()

CONFIG = {
    "FLOOR": DEFAULT_FLOOR,
    "VERSION": "Web Version 1.0 - Supabase Cloud 版",
    "SYSTEM_NAME": "Shoptoplus 雲端入庫系統",
    
    # --- 資料庫配置 (Supabase) ---
    # 這些資訊請在 Streamlit Cloud 的 Secrets 中設定，或在本地測試時填入
    "SUPABASE_URL": "", # 例如: https://xyz.supabase.co
    "SUPABASE_KEY": "", # 您的 Anon Key 或 Service Role Key
    
    # --- 路徑配置 (已移除內網硬編碼) ---
    "PATHS": {
        "EXPORT_DIR": "./temp_exports", # 自動改存到專案資料夾下
        "LOG_DIR": "./temp_logs"
    },
    
    "ROLES": {
        "ADMIN": ["EVA", "JENNIFER", "ALFRED", "BUN", "JACKY", "FAI", "CAT", "HONG"],
        "ACC": ["GIBSON"],
        "STAFF_3F": ["員工A", "員工B"],
        "STAFF_5F": ["HIM", "WAI", "HENRY", "BON", "CHING", "LUN", "MAX", "KEN", "ADRIAN", "CRYSTAL", "GIAN"]
    },
    
    "SPECIAL_CUSTOMERS": ["COBOLIFE", "LINBERG"],
    
    "UI_COLORS": {
        "ORANGE": "#855a1e",
        "GREEN": "#2d5a27",
        "RED": "#b71c1c",
        "BLUE": "#1565c0",
        "GREY": "#a0a0a0"
    },
    
    "EXCEL_MAPPING": {
        "Barcode": ["BARCODE", "條碼"],
        "SKU ID": ["SKU ID", "貨號"],
        "產品名稱": ["產品名稱", "品名"],
        "預計數量": ["預計數量", "數量", "QTY"]
    },
    
    "SOUNDS": {
        "success": "https://actions.google.com/sounds/v1/actions/check_out.ogg",
        "error": "https://actions.google.com/sounds/v1/alerts/mistery_error_chime.ogg"
    },
    
    "EXCEL_TEMPLATE": {
        "REQUIRED_HEADERS": ["SKU_ID", "BARCODE", "PRODUCT_NAME", "EXPECTED_QTY", "EXPIRY_DATE"],
        "NUMERIC_FIELDS": ["EXPECTED_QTY"],
        "DATE_FIELDS": ["EXPIRY_DATE"]
    },
    
    "STATUS": {
        "PENDING": "pending",
        "CLIENT_SUBMITTED": "Client_Submitted",
        "OFFICE_APPROVED": "Active",
        "COMPLETED": "completed"
    },
    
    "AGING": {
        "YELLOW": 2,
        "RED": 3,
        "FLASH": 4
    }
}
