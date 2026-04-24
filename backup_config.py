# backup_config.py
"""
備份工具配置文件
請填入您的 Supabase 憑證
"""

# Supabase 配置
SUPABASE_URL = "https://gewkdkjcssonimoxieum.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdld2tka2pjc3Nvbmltb3hpZXVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3MzY1MTUsImV4cCI6MjA5MjMxMjUxNX0.BI5iiemtYKTJRcxXOWlJ2mbBQ3y7WAY7a0dScBftxfs"

# 備份目錄
BACKUP_DIR = r"C:\IB_DB_BK"

# 備份設定
BACKUP_FORMATS = ["csv", "xlsx"]  # 備份格式
AUTO_CLEAN_OLD_BACKUPS = True     # 是否自動清理舊備份
KEEP_DAYS = 30                    # 保留天數

# 要備份的資料表
TABLES_TO_BACKUP = [
    "batches",      # 批次資料
    "products",     # 產品資料
    "users",        # 用戶資料
    "audit_logs"    # 審核日誌
]
