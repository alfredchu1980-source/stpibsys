# backup_inbound_files.py
"""
Backup Inbound System Files
1. Export Excel files (IVR, STD reports) from temp_exports
2. Working logs from Supabase audit_logs
Backup to C:\IB_DB_BK organized by date
"""

import pandas as pd
from datetime import datetime
import os
import shutil
import sys

# Backup destination
BACKUP_ROOT = r"C:\IB_DB_BK"

# Source paths
TEMP_EXPORTS_DIR = "./temp_exports"

# Try to import from backup_config
try:
    from backup_config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    SUPABASE_URL = "https://gewkdkjcssonimoxieum.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdld2tka2pjc3Nvbmltb3hpZXVtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3MzY1MTUsImV4cCI6MjA5MjMxMjUxNX0.BI5iiemtYKTJRcxXOWlJ2mbBQ3y7WAY7a0dScBftxfs"

def get_backup_path():
    """Get today's backup directory"""
    today = datetime.now().strftime("%Y-%m-%d")
    backup_path = os.path.join(BACKUP_ROOT, today)
    
    if not os.path.exists(backup_path):
        os.makedirs(backup_path, exist_ok=True)
    
    return backup_path

def backup_export_files():
    """Backup Excel files from temp_exports directory"""
    print("=" * 60)
    print("📊 Backing up Inbound Excel Files")
    print("=" * 60)
    print()
    
    backup_path = get_backup_path()
    excel_backup_path = os.path.join(backup_path, "excel_reports")
    
    if not os.path.exists(excel_backup_path):
        os.makedirs(excel_backup_path, exist_ok=True)
    
    # Check if temp_exports exists
    if not os.path.exists(TEMP_EXPORTS_DIR):
        print(f"⚠️  {TEMP_EXPORTS_DIR} directory not found")
        print("   (This is normal if no reports have been exported yet)")
        print()
        return 0, 0
    
    # Copy all Excel files
    success_count = 0
    fail_count = 0
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for filename in os.listdir(TEMP_EXPORTS_DIR):
        if filename.endswith(('.xlsx', '.xls')):
            src_path = os.path.join(TEMP_EXPORTS_DIR, filename)
            
            # Add timestamp to avoid overwriting
            name, ext = os.path.splitext(filename)
            new_filename = f"{name}_{timestamp}{ext}"
            dst_path = os.path.join(excel_backup_path, new_filename)
            
            try:
                shutil.copy2(src_path, dst_path)
                print(f"  ✅ {filename} → {new_filename}")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {filename} failed: {e}")
                fail_count += 1
    
    if success_count == 0 and fail_count == 0:
        print("  ⚠️  No Excel files found in temp_exports")
    
    print()
    print(f"  Success: {success_count} files")
    print(f"  Failed: {fail_count} files")
    print(f"  Location: {excel_backup_path}")
    print()
    
    return success_count, fail_count

def backup_working_logs():
    """Backup working logs from Supabase audit_logs table"""
    print("=" * 60)
    print("📋 Backing up Working Logs (CSV)")
    print("=" * 60)
    print()
    
    backup_path = get_backup_path()
    log_backup_path = os.path.join(backup_path, "working_logs")
    
    if not os.path.exists(log_backup_path):
        os.makedirs(log_backup_path, exist_ok=True)
    
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"  ❌ Cannot connect to Supabase: {e}")
        return 0, 1
    
    try:
        print("  Fetching audit_logs from Supabase...")
        response = supabase.table("audit_logs").select("*").order("timestamp", desc=True).execute()
        
        if not response.data:
            print("  ⚠️  No audit logs found")
            print()
            return 0, 0
        
        df = pd.DataFrame(response.data)
        
        # Save as CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"audit_logs_{timestamp}.csv"
        csv_path = os.path.join(log_backup_path, csv_filename)
        
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        
        print(f"  ✅ Working logs backed up")
        print(f"     Records: {len(df)}")
        print(f"     File: {csv_filename}")
        print(f"     Location: {log_backup_path}")
        print()
        
        return 1, 0
        
    except Exception as e:
        print(f"  ❌ Failed to backup working logs: {e}")
        print("     (audit_logs table may not exist)")
        print()
        return 0, 1

def backup_all():
    """Run all backups"""
    print()
    print("=" * 60)
    print("   Inbound System File Backup Tool")
    print("=" * 60)
    print()
    print(f"Backup Root: {BACKUP_ROOT}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Backup Excel files
    excel_success, excel_fail = backup_export_files()
    
    # Backup working logs
    log_success, log_fail = backup_working_logs()
    
    # Summary
    print("=" * 60)
    print("📊 Backup Summary")
    print("=" * 60)
    print()
    print(f"  Excel Files:  {excel_success} success, {excel_fail} failed")
    print(f"  Working Logs: {log_success} success, {log_fail} failed")
    print()
    
    total_success = excel_success + log_success
    total_fail = excel_fail + log_fail
    
    if total_fail == 0:
        print("✅ All backups completed successfully!")
    else:
        print(f"⚠️  {total_fail} backup(s) failed")
    
    print()
    print(f"📂 Backup Location: {get_backup_path()}")
    print()
    
    return total_fail == 0

if __name__ == "__main__":
    success = backup_all()
    
    if not success:
        sys.exit(1)
    
    print("💡 Tip: Check C:\\IB_DB_BK for today's backup")
    print()
