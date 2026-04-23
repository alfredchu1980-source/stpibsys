# hooks.py
"""
模組掛載點配置
用於管理所有外掛模組的開關和配置

安裝狀態檢查：
- 如果此檔案存在，表示模組已安裝
- 如果 REFERENCE_MODULE_ENABLED = True 但功能未顯示，請檢查 reference_module/ 資料夾
"""

# ============================================
# 參考表模組配置
# ============================================
REFERENCE_MODULE_ENABLED = True  # 設為 False 可完全禁用參考表功能
REFERENCE_MODULE_PATH = "./reference_module"

# 參考表檔案路徑
REFERENCE_TABLE_PATH = "./data/reference_table.csv"

# CSV 欄位配置 (索引從 0 開始)
REFERENCE_BARCODE_COLUMN = 2    # Column C = 條碼
REFERENCE_LOCATION_COLUMN = 4   # Column E = 儲位
REFERENCE_EXPIRY_COLUMN = 5     # Column F = 到期日

# 功能開關
REFERENCE_SHOW_IN_SCAN = True       # 掃描時顯示參考資料
REFERENCE_SHOW_IN_SIDEBAR = True    # 側邊欄顯示上傳按鈕
REFERENCE_SHOW_IN_OFFICE = True     # Office 管理頁面顯示

# ============================================
# 安裝狀態檢查函數
# ============================================
def check_module_installation():
    """
    檢查參考表模組是否正確安裝
    
    回傳:
        dict: 包含安裝狀態和錯誤訊息
    """
    import os
    
    result = {
        'installed': False,
        'errors': [],
        'warnings': []
    }
    
    # 檢查 hooks.py 本身
    result['hooks_exists'] = os.path.exists(__file__)
    
    # 檢查 reference_module 資料夾
    module_path = os.path.join(os.path.dirname(__file__), 'reference_module')
    result['module_folder_exists'] = os.path.exists(module_path)
    
    if not result['module_folder_exists']:
        result['errors'].append(f"找不到 reference_module/ 資料夾，請確認已正確安裝")
    else:
        # 檢查必要檔案
        required_files = ['__init__.py', 'ref_table.py', 'scanner.py', 'uploader.py']
        for file in required_files:
            file_path = os.path.join(module_path, file)
            if not os.path.exists(file_path):
                result['errors'].append(f"缺少必要檔案：reference_module/{file}")
        
        # 檢查 data 資料夾
        data_path = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(data_path):
            result['warnings'].append("data/ 資料夾不存在，系統會自動創建")
    
    # 如果沒有錯誤，標記為已安裝
    result['installed'] = len(result['errors']) == 0
    
    return result
