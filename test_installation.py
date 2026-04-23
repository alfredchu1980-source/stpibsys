# test_installation.py
"""
參考表模組安裝測試腳本

使用方法：
    python test_installation.py

如果所有測試通過，表示模組已正確安裝。
"""

import os
import sys

print("=" * 60)
print("🔍 參考表模組安裝測試")
print("=" * 60)

# 測試結果
tests_passed = 0
tests_failed = 0
tests_warnings = 0

def test(name, condition, error_msg=None):
    """執行測試"""
    global tests_passed, tests_failed, tests_warnings
    
    if condition:
        print(f"✅ {name}")
        tests_passed += 1
        return True
    else:
        print(f"❌ {name}")
        if error_msg:
            print(f"   錯誤：{error_msg}")
        tests_failed += 1
        return False

def test_warning(name, condition, warning_msg=None):
    """執行測試（警告等級）"""
    global tests_passed, tests_warnings
    
    if condition:
        print(f"✅ {name}")
        tests_passed += 1
        return True
    else:
        print(f"⚠️  {name}")
        if warning_msg:
            print(f"   警告：{warning_msg}")
        tests_warnings += 1
        return True  # 警告不算失敗

# 測試 1：hooks.py 是否存在
print("\n📁 測試 1：檢查 hooks.py")
print("-" * 60)
test("hooks.py 存在", os.path.exists("hooks.py"), "請將 hooks.py 放到 C:\\PT_IB\\ 目錄")

# 測試 2：reference_module 資料夾是否存在
print("\n📁 測試 2：檢查 reference_module/ 資料夾")
print("-" * 60)
test("reference_module/ 資料夾存在", 
     os.path.exists("reference_module"), 
     "請創建 reference_module/ 資料夾")

# 測試 3：檢查必要檔案
print("\n📄 測試 3：檢查必要檔案")
print("-" * 60)
required_files = [
    "reference_module/__init__.py",
    "reference_module/ref_table.py",
    "reference_module/scanner.py",
    "reference_module/uploader.py",
]

for file in required_files:
    test(f"{file} 存在", os.path.exists(file), f"請將 {file} 放到正確位置")

# 測試 4：檢查 data 資料夾（警告等級）
print("\n📁 測試 4：檢查 data/ 資料夾（警告等級）")
print("-" * 60)
test_warning("data/ 資料夾存在", 
             os.path.exists("data"), 
             "系統會自動創建，或請手動創建 data/ 資料夾")

# 測試 5：嘗試導入 hooks 模組
print("\n🔧 測試 5：測試導入 hooks 模組")
print("-" * 60)
try:
    from hooks import REFERENCE_MODULE_ENABLED, check_module_installation
    test("hooks 模組導入成功", True)
    
    # 測試 6：檢查模組安裝狀態
    print("\n🔍 測試 6：檢查模組安裝狀態")
    print("-" * 60)
    status = check_module_installation()
    test("模組已正確安裝", status['installed'])
    
    if status['errors']:
        print("\n錯誤列表:")
        for error in status['errors']:
            print(f"  ❌ {error}")
    
    if status['warnings']:
        print("\n警告列表:")
        for warning in status['warnings']:
            print(f"  ⚠️  {warning}")
    
except ImportError as e:
    test("hooks 模組導入成功", False, f"導入失敗：{e}")

# 測試 7：嘗試導入 reference_module
print("\n🔧 測試 7：測試導入 reference_module")
print("-" * 60)
try:
    from reference_module import MODULE_LOADED
    test("reference_module 模組導入成功", MODULE_LOADED)
except ImportError as e:
    test("reference_module 模組導入成功", False, f"導入失敗：{e}")
except Exception as e:
    test("reference_module 模組導入成功", False, f"錯誤：{e}")

# 總結
print("\n" + "=" * 60)
print("📊 測試結果總結")
print("=" * 60)
print(f"✅ 通過：{tests_passed}")
print(f"❌ 失敗：{tests_failed}")
print(f"⚠️  警告：{tests_warnings}")
print("=" * 60)

if tests_failed == 0:
    if tests_warnings == 0:
        print("\n🎉 所有測試通過！模組已正確安裝。")
    else:
        print(f"\n✅ 所有必要測試通過！有 {tests_warnings} 個警告，不影響使用。")
        print("   建議處理警告以提升系統完整性。")
else:
    print(f"\n❌ 有 {tests_failed} 個測試失敗，請按照錯誤訊息修復。")
    sys.exit(1)

print("\n" + "=" * 60)
