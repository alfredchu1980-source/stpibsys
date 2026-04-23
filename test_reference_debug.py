# test_reference_debug.py
"""
參考表功能測試與除錯腳本

使用方法：
    python test_reference_debug.py
"""

import os
import sys

print("=" * 60)
print("🔍 參考表功能測試與除錯")
print("=" * 60)

# 測試 1：檢查 CSV 檔案
print("\n📁 測試 1：檢查 CSV 檔案")
print("-" * 60)

try:
    from reference_module.debug import check_csv_file
    
    csv_check = check_csv_file()
    
    if csv_check['exists']:
        print(f"✅ 檔案存在")
        print(f"📊 檔案大小：{csv_check['info'].get('file_size_kb', 'N/A')} KB")
        print(f"📈 總記錄數：{csv_check['info'].get('total_records', 'N/A')}")
        print(f"📈 有效記錄數：{csv_check['info'].get('valid_records', 'N/A')}")
        print(f"📋 欄位數量：{csv_check['info'].get('column_count', 'N/A')}")
        
        if 'sample_data' in csv_check['info']:
            print("\n📄 前 5 筆資料範例:")
            cols = csv_check['info'].get('columns', [])
            for i, row in enumerate(csv_check['info']['sample_data'], 1):
                if len(cols) >= 6:
                    print(f"  {i}. Barcode: {row.get(cols[0], 'N/A')}")
                    print(f"     Location: {row.get(cols[4], 'N/A')}")
                    print(f"     Expiry: {row.get(cols[5], 'N/A')}")
    else:
        print("❌ 檔案不存在")
        print("💡 請先上傳參考表 CSV 檔案")
    
    if csv_check['errors']:
        print("\n❌ 錯誤列表:")
        for error in csv_check['errors']:
            print(f"  {error}")
    
    if csv_check['valid']:
        print("\n✅ CSV 檔案格式正確！")
    else:
        print("\n❌ CSV 檔案格式有問題，請檢查錯誤列表")
        
except Exception as e:
    print(f"❌ 檢查失敗：{e}")

# 測試 2：測試條碼搜尋
print("\n" + "=" * 60)
print("🔍 測試 2：測試條碼搜尋")
print("-" * 60)

if csv_check['valid']:
    test_barcode = input("\n請輸入要測試的條碼 (或直接按 Enter 使用第一個條碼): ").strip()
    
    if not test_barcode and 'sample_data' in csv_check['info']:
        cols = csv_check['info'].get('columns', [])
        if len(csv_check['info']['sample_data']) > 0 and len(cols) >= 1:
            test_barcode = csv_check['info']['sample_data'][0].get(cols[0], '')
            print(f"💡 使用第一個條碼：{test_barcode}")
    
    if test_barcode:
        try:
            from reference_module import test_barcode_search
            
            result = test_barcode_search(test_barcode)
            
            if result['found']:
                print(f"\n✅ 找到 {result['count']} 筆記錄:")
                for i, rec in enumerate(result['results'], 1):
                    print(f"  {i}. 📍 儲位：{rec.get('location', 'N/A')}")
                    print(f"     📅 到期日：{rec.get('expiry_date', 'N/A')}")
            else:
                print(f"\n❌ 找不到條碼：{test_barcode}")
                if result['errors']:
                    print("\n可能原因:")
                    for error in result['errors']:
                        print(f"  {error}")
        except Exception as e:
            print(f"❌ 搜尋失敗：{e}")
else:
    print("⚠️  跳過（CSV 檔案無效）")

# 測試 3：模組狀態
print("\n" + "=" * 60)
print("🔧 測試 3：模組狀態檢查")
print("-" * 60)

try:
    from reference_module import MODULE_LOADED
    
    if MODULE_LOADED:
        print("✅ 模組載入成功")
    else:
        print("❌ 模組載入失敗")
        from reference_module import MODULE_ERROR
        print(f"錯誤：{MODULE_ERROR}")
except Exception as e:
    print(f"❌ 檢查失敗：{e}")

print("\n" + "=" * 60)
print("測試完成")
print("=" * 60)
