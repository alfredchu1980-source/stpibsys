# backup_supabase.py
"""
Supabase 資料備份工具
將資料庫資料匯出至本地硬碟
"""

import pandas as pd
from datetime import datetime
import os
import sys

# 嘗試從 backup_config 讀取配置
try:
    from backup_config import SUPABASE_URL, SUPABASE_KEY, BACKUP_DIR
except ImportError:
    # 預設配置
    SUPABASE_URL = "https://gewkdkjcssonimoxieum.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdld2tka2pjc3Nvbmltb3hpZXVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3MzY1MTUsImV4cCI6MjA5MjMxMjUxNX0.BI5iiemtYKTJRcxXOWlJ2mbBQ3y7WAY7a0dScBftxfs"
    BACKUP_DIR = r"C:\IB_DB_BK"

def check_backup_directory():
    """檢查備份目錄狀態"""
    print("=" * 60)
    print("📁 檢查備份目錄")
    print("=" * 60)
    print()
    print(f"配置的備份路徑：{BACKUP_DIR}")
    print()
    
    print("[1] 檢查 C: 磁碟機...")
    if not os.path.exists("C:\\"):
        print("    ❌ C: 磁碟機不存在")
        return False
    print("    ✅ C: 磁碟機可訪問")
    print()
    
    print("[2] 檢查備份目錄...")
    if not os.path.exists(BACKUP_DIR):
        print(f"    ⚠️ 目錄不存在：{BACKUP_DIR}")
        print("    嘗試建立目錄...")
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            print(f"    ✅ 已建立目錄：{BACKUP_DIR}")
        except Exception as e:
            print(f"    ❌ 無法建立目錄：{e}")
            return False
    else:
        print(f"    ✅ 目錄已存在：{BACKUP_DIR}")
    print()
    
    print("[3] 測試寫入權限...")
    test_file = os.path.join(BACKUP_DIR, "test_write.txt")
    try:
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Test write permission\n")
        print("    ✅ 寫入權限正常")
        os.remove(test_file)
        print("    ✅ 測試檔案已刪除")
    except Exception as e:
        print(f"    ❌ 寫入權限測試失敗：{e}")
        return False
    print()
    
    print("[4] 現有備份內容...")
    try:
        items = os.listdir(BACKUP_DIR)
        if items:
            print(f"    找到 {len(items)} 個項目:")
            for item in items[:10]:
                item_path = os.path.join(BACKUP_DIR, item)
                if os.path.isdir(item_path):
                    print(f"      📁 {item}/")
                else:
                    print(f"      📄 {item}")
            if len(items) > 10:
                print(f"      ... 及其他 {len(items) - 10} 個項目")
        else:
            print("    ⚠️ 目錄為空（這是正常的，如果是第一次備份）")
    except Exception as e:
        print(f"    ❌ 無法列出目錄內容：{e}")
    print()
    
    print("=" * 60)
    print("✅ 備份目錄檢查完成")
    print("=" * 60)
    print()
    
    return True

def get_supabase_client():
    """建立 Supabase 客戶端"""
    try:
        if not SUPABASE_URL or SUPABASE_URL == "YOUR_SUPABASE_URL":
            print("❌ Supabase URL 未設定！")
            return None
        
        if not SUPABASE_KEY or SUPABASE_KEY == "YOUR_SUPABASE_KEY":
            print("❌ Supabase Key 未設定！")
            return None
        
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"❌ 連接失敗：{e}")
        return None

def create_backup_directory():
    """建立備份目錄"""
    today = datetime.now().strftime("%Y-%m-%d")
    backup_path = os.path.join(BACKUP_DIR, today)
    
    print(f"📁 檢查備份路徑：{BACKUP_DIR}")
    
    if not os.path.exists(BACKUP_DIR):
        print(f"⚠️ 備份目錄不存在，嘗試建立：{BACKUP_DIR}")
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            print(f"✅ 已建立目錄：{BACKUP_DIR}")
        except Exception as e:
            print(f"❌ 無法建立目錄：{e}")
            return None
    
    if not os.path.exists(backup_path):
        print(f"⚠️ 今日備份目錄不存在，嘗試建立：{backup_path}")
        try:
            os.makedirs(backup_path, exist_ok=True)
            print(f"✅ 已建立目錄：{backup_path}")
        except Exception as e:
            print(f"❌ 無法建立目錄：{e}")
            return None
    
    return backup_path

def table_exists(supabase, table_name):
    """檢查資料表是否存在"""
    try:
        response = supabase.table(table_name).select("*").limit(1).execute()
        return True
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "PGRST205" in error_msg:
            return False
        return False

def backup_table(supabase, table_name, backup_path):
    """備份單一資料表"""
    try:
        print(f"📊 正在備份 {table_name}...")
        
        # 先檢查表是否存在
        if not table_exists(supabase, table_name):
            print(f"  ⚠️ {table_name} 不存在，跳過")
            return None  # 返回 None 表示跳過，不算失敗
        
        response = supabase.table(table_name).select("*").execute()
        
        if not response.data:
            print(f"  ⚠️ {table_name} 無資料")
            return False
        
        df = pd.DataFrame(response.data)
        
        csv_path = os.path.join(backup_path, f"{table_name}.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        
        xlsx_path = os.path.join(backup_path, f"{table_name}.xlsx")
        df.to_excel(xlsx_path, index=False, engine="openpyxl")
        
        print(f"  ✅ {table_name} 備份完成 ({len(df)} 筆記錄)")
        print(f"     CSV: {csv_path}")
        print(f"     XLSX: {xlsx_path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ {table_name} 備份失敗：{e}")
        return False

def backup_all_tables():
    """備份所有資料表"""
    print()
    print("=" * 60)
    print("🔄 Supabase 資料備份工具")
    print("=" * 60)
    print()
    
    print("【步驟 1】檢查備份目錄...")
    if not check_backup_directory():
        print("❌ 備份目錄檢查失敗")
        return False
    print()
    
    print("【步驟 2】檢查 Supabase 連線...")
    supabase = get_supabase_client()
    if not supabase:
        print("❌ 無法連接 Supabase")
        print("   請檢查 backup_config.py 中的配置")
        return False
    print(f"✅ Supabase 連線成功")
    print()
    
    print("【步驟 3】建立備份目錄...")
    backup_path = create_backup_directory()
    if not backup_path:
        print("❌ 無法建立備份目錄")
        return False
    
    print(f"📁 備份位置：{backup_path}")
    print()
    print("=" * 60)
    print("【步驟 4】開始備份資料表...")
    print("=" * 60)
    print()
    
    # 要備份的資料表
    tables = [
        "batches",
        "products",
        "users",
        "audit_logs"
    ]
    
    # 備份統計
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    # 開始備份
    for table in tables:
        try:
            result = backup_table(supabase, table, backup_path)
            if result is None:
                skip_count += 1  # 表不存在，跳過
            elif result:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  ❌ {table} 發生錯誤：{e}")
            fail_count += 1
    
    print()
    
    # 建立備份報告
    report_path = os.path.join(backup_path, "backup_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Supabase 備份報告\n")
        f.write(f"=" * 60 + "\n")
        f.write(f"備份時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"備份目錄：{backup_path}\n")
        f.write(f"成功：{success_count} 表\n")
        f.write(f"失敗：{fail_count} 表\n")
        f.write(f"跳過：{skip_count} 表 (不存在)\n")
        f.write(f"=" * 60 + "\n")
        f.write(f"\n備份的資料表:\n")
        for table in tables:
            f.write(f"  - {table}\n")
    
    print("=" * 60)
    print(f"✅ 備份完成！")
    print(f"   成功：{success_count} 表")
    print(f"   失敗：{fail_count} 表")
    print(f"   跳過：{skip_count} 表 (不存在)")
    print(f"   報告：{report_path}")
    print("=" * 60)
    print()
    print("📂 備份檔案位置:")
    print(f"   {backup_path}")
    print()
    
    return True

def backup_single_batch(batch_id):
    """備份單一批次資料"""
    print(f"📦 備份批次：{batch_id}")
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    backup_path = create_backup_directory()
    if not backup_path:
        return False
    
    batch_backup_path = os.path.join(backup_path, f"batch_{batch_id}")
    
    if not os.path.exists(batch_backup_path):
        os.makedirs(batch_backup_path)
    
    try:
        batch_info = supabase.table("batches").select("*").eq("batch_id", batch_id).execute()
        if batch_info.data:
            df_batch = pd.DataFrame(batch_info.data)
            df_batch.to_csv(os.path.join(batch_backup_path, "batch_info.csv"), index=False, encoding="utf-8-sig")
            df_batch.to_excel(os.path.join(batch_backup_path, "batch_info.xlsx"), index=False)
            print(f"  ✅ 批次資訊備份完成")
        
        products = supabase.table("products").select("*").eq("batch_id", batch_id).execute()
        if products.data:
            df_products = pd.DataFrame(products.data)
            df_products.to_csv(os.path.join(batch_backup_path, "products.csv"), index=False, encoding="utf-8-sig")
            df_products.to_excel(os.path.join(batch_backup_path, "products.xlsx"), index=False)
            print(f"  ✅ 產品資料備份完成 ({len(df_products)} 筆記錄)")
        
        print(f"  📁 備份位置：{batch_backup_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ 備份失敗：{e}")
        return False

def list_backups():
    """列出所有備份"""
    print("=" * 60)
    print("📋 現有備份列表")
    print("=" * 60)
    
    if not os.path.exists(BACKUP_DIR):
        print("⚠️ 備份目錄不存在")
        return
    
    for date_folder in sorted(os.listdir(BACKUP_DIR)):
        date_path = os.path.join(BACKUP_DIR, date_folder)
        if os.path.isdir(date_path):
            files = os.listdir(date_path)
            print(f"📁 {date_folder}/ ({len(files)} 個檔案)")
            for file in files[:5]:
                print(f"   - {file}")
            if len(files) > 5:
                print(f"   ... 及其他 {len(files) - 5} 個檔案")
    
    print("=" * 60)

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("   Supabase 資料備份工具 v1.0")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "backup":
            backup_all_tables()
            
        elif command == "batch" and len(sys.argv) > 2:
            batch_id = sys.argv[2]
            backup_single_batch(batch_id)
            
        elif command == "list":
            list_backups()
            
        elif command == "check":
            check_backup_directory()
            
        else:
            print("❌ 未知命令")
            print("\n使用方式:")
            print("  python backup_supabase.py backup        # 完整備份")
            print("  python backup_supabase.py batch JOB-001 # 備份單一批次")
            print("  python backup_supabase.py list          # 列出備份")
            print("  python backup_supabase.py check         # 檢查備份目錄")
    else:
        backup_all_tables()
        
        print()
        print("💡 使用說明:")
        print("  python backup_supabase.py backup        # 完整備份")
        print("  python backup_supabase.py batch JOB-001 # 備份單一批次")
        print("  python backup_supabase.py list          # 列出備份")
        print("  python backup_supabase.py check         # 檢查備份目錄")
        print()
