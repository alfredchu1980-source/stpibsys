# config.py

CONFIG = {
    "SYSTEM_NAME": "Shoptoplus 入庫系統",
    "VERSION": "V70 雲端版",
    
    # 角色定義（新增 Customer 角色）
    "ROLES": {
        "ADMIN": ["EVA", "JENNIFER", "ALFRED", "BUN", "JACKY", "FAI", "CAT", "HONG"],
        "ACC": ["GIBSON"],
        "STAFF_3F": ["HIM", "WAI", "HENRY", "BON"],
        "STAFF_5F": ["CHING", "LUN", "MAX", "KEN", "ADRIAN", "CRYSTAL", "GIAN"],
        "CUSTOMER": ["TEST_CUSTOMER", "CLIENT01", "CLIENT02"]  # 新增 Customer 角色
    },
    
    # 狀態定義
    "STATUS": {
        "PENDING": "pending",
        "ACTIVE": "Active",
        "COMPLETED": "completed",
        "CLIENT_SUBMITTED": "pending"  # 客戶提交後的状态
    },
    
    # Excel 欄位映射
    "EXCEL_MAPPING": {
        "Barcode": ["BARCODE", "條碼", "SCAN"],
        "SKU ID": ["SKU", "貨號", "SKU ID"],
        "產品名稱": ["PRODUCT", "產品", "名稱", "PRODUCT NAME"],
        "預計數量": ["QTY", "數量", "預計", "EXPECTED"]
    },
    
    # UI 顏色
    "UI_COLORS": {
        "GREEN": "#28a745",
        "BLUE": "#007bff",
        "RED": "#dc3545",
        "ORANGE": "#fd7e14"
    },
    
    # 路徑配置
    "PATHS": {
        "EXPORT_DIR": "temp_exports"
    },
    
    # 安全性設定
    "SECURITY": {
        "SESSION_TIMEOUT_MINUTES": 30,  # 工作階段逾時時間（分鐘）
        "MIN_PASSWORD_LENGTH": 6,  # 最小密碼長度
        "MAX_LOGIN_ATTEMPTS": 10,  # 最大登入嘗試次數
        "PASSWORD_EXPIRY_DAYS": 90  # 密碼過期天數（可選）
    },
    
    # Supabase 配置（從 Secrets 讀取）
    "SUPABASE_URL": "",
    "SUPABASE_KEY": ""
}
