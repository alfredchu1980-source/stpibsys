# reference_module/debug.py
"""
參考表除錯工具
用於檢查 CSV 格式和測試條碼搜尋
"""

import pandas as pd
import os

try:
    from hooks import REFERENCE_TABLE_PATH
except ImportError:
    REFERENCE_TABLE_PATH = "./data/reference_table.csv"


def check_csv_file():
    """
    檢查 CSV 檔案是否存在及格式是否正確
    
    回傳:
        dict: 檢查結果
    """
    result = {
        'exists': False,
        'valid': False,
        'errors': [],
        'info': {}
    }
    
    # 檢查檔案是否存在
    if not os.path.exists(REFERENCE_TABLE_PATH):
        result['errors'].append(f"❌ 參考表檔案不存在：{REFERENCE_TABLE_PATH}")
        return result
    
    result['exists'] = True
    result['info']['file_path'] = REFERENCE_TABLE_PATH
    result['info']['file_size_kb'] = round(os.path.getsize(REFERENCE_TABLE_PATH) / 1024, 2)
    
    # 嘗試讀取 CSV
    try:
        df = pd.read_csv(REFERENCE_TABLE_PATH, encoding='utf-8-sig', dtype=str)
        
        result['info']['total_records'] = len(df)
        result['info']['columns'] = list(df.columns)
        result['info']['column_count'] = len(df.columns)
        
        # 檢查欄位數量
        if len(df.columns) < 6:
            result['errors'].append(f"❌ CSV 欄位不足：需要至少 6 個欄位，目前只有 {len(df.columns)} 個")
        else:
            result['info']['barcode_column'] = df.columns[0]
            result['info']['location_column'] = df.columns[4]
            result['info']['expiry_column'] = df.columns[5]
            
            # 檢查必要欄位是否為空
            if df[df.columns[4]].isna().all():
                result['errors'].append("❌ Column E (location) 全部為空")
            elif df[df.columns[5]].isna().all():
                result['errors'].append("❌ Column F (expiry_date) 全部為空")
            else:
                # 檢查有幾筆有效記錄
                valid_records = df.dropna(subset=[df.columns[4], df.columns[5]])
                result['info']['valid_records'] = len(valid_records)
                
                if len(valid_records) == 0:
                    result['errors'].append("❌ 沒有有效記錄（location 和 expiry_date 都不能為空）")
                else:
                    result['valid'] = True
        
        # 顯示前 5 筆資料範例
        if len(df) > 0:
            result['info']['sample_data'] = df.head(5).to_dict('records')
        
    except Exception as e:
        result['errors'].append(f"❌ 讀取 CSV 失敗：{str(e)}")
    
    return result


def test_barcode_search(barcode):
    """
    測試條碼搜尋功能
    
    參數:
        barcode: 要搜尋的條碼
    
    回傳:
        dict: 搜尋結果
    """
    result = {
        'found': False,
        'count': 0,
        'results': [],
        'errors': []
    }
    
    try:
        from .ref_table import search_by_barcode
        
        results = search_by_barcode(barcode)
        
        if results:
            result['found'] = True
            result['count'] = len(results)
            result['results'] = results
        else:
            result['errors'].append(f"⚠️ 找不到條碼：{barcode}")
            result['errors'].append("💡 請確認：")
            result['errors'].append("   1. 條碼在 CSV 中存在")
            result['errors'].append("   2. CSV 格式正確（Column A = barcode）")
            result['errors'].append("   3. 條碼完全匹配（包含大小寫和空格）")
    
    except Exception as e:
        result['errors'].append(f"❌ 搜尋失敗：{str(e)}")
    
    return result


def show_debug_info():
    """
    顯示完整除錯資訊
    
    回傳:
        str: 除錯資訊文字
    """
    output = []
    output.append("=" * 60)
    output.append("🔍 參考表除錯資訊")
    output.append("=" * 60)
    
    # 檢查 CSV 檔案
    output.append("\n📁 CSV 檔案檢查")
    output.append("-" * 60)
    csv_check = check_csv_file()
    
    if csv_check['exists']:
        output.append(f"✅ 檔案存在：{csv_check['info'].get('file_path')}")
        output.append(f"📊 檔案大小：{csv_check['info'].get('file_size_kb')} KB")
        output.append(f"📈 總記錄數：{csv_check['info'].get('total_records')}")
        output.append(f"📈 有效記錄數：{csv_check['info'].get('valid_records', 'N/A')}")
        output.append(f"📋 欄位數量：{csv_check['info'].get('column_count')}")
        
        if 'sample_data' in csv_check['info']:
            output.append("\n📄 前 5 筆資料範例:")
            for i, row in enumerate(csv_check['info']['sample_data'], 1):
                cols = csv_check['info'].get('columns', [])
                if len(cols) >= 6:
                    output.append(f"  {i}. Barcode: {row.get(cols[0], 'N/A')}")
                    output.append(f"     Location: {row.get(cols[4], 'N/A')}")
                    output.append(f"     Expiry: {row.get(cols[5], 'N/A')}")
    else:
        output.append("❌ 檔案不存在")
    
    # 顯示錯誤
    if csv_check['errors']:
        output.append("\n❌ 錯誤列表:")
        for error in csv_check['errors']:
            output.append(f"  {error}")
    
    output.append("")
    output.append("=" * 60)
    
    return "\n".join(output), csv_check['valid']
