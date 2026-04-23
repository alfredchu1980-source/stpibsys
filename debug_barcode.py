# debug_barcode.py
"""
診斷特定條碼問題
檢查 CSV 中 837328000050 的實際內容和格式
"""

import pandas as pd
import os

REFERENCE_TABLE_PATH = "./data/reference_table.csv"
TEST_BARCODE = "837328000050"

print("=" * 60)
print(f"🔍 診斷條碼：{TEST_BARCODE}")
print("=" * 60)

# 檢查檔案是否存在
if not os.path.exists(REFERENCE_TABLE_PATH):
    print(f"\n❌ 參考表檔案不存在：{REFERENCE_TABLE_PATH}")
    print("💡 請先上傳參考表 CSV 檔案")
    exit()

print(f"\n✅ 檔案存在：{REFERENCE_TABLE_PATH}")
print(f"📊 檔案大小：{os.path.getsize(REFERENCE_TABLE_PATH) / 1024:.2f} KB")

# 讀取 CSV
print("\n" + "=" * 60)
print("📄 讀取 CSV 檔案")
print("=" * 60)

try:
    df = pd.read_csv(REFERENCE_TABLE_PATH, encoding='utf-8-sig', dtype=str)
    print(f"✅ 成功讀取 CSV")
    print(f"📊 總記錄數：{len(df)}")
    print(f"📋 欄位數量：{len(df.columns)}")
    print(f"📋 欄位名稱：{list(df.columns)}")
except Exception as e:
    print(f"❌ 讀取失敗：{e}")
    exit()

# 顯示 Column C (barcode) 的前 10 筆資料
print("\n" + "=" * 60)
print("📄 Column C (barcode) 前 10 筆資料")
print("=" * 60)

if len(df.columns) > 2:
    barcode_col = df.columns[2]  # Column C (索引 2)
    print(f"欄位名稱：{barcode_col}")
    print("\n前 10 筆資料:")
    for i in range(min(10, len(df))):
        barcode_val = df.iloc[i][barcode_col]
        print(f"  {i+1}. '{barcode_val}' (長度：{len(str(barcode_val)) if barcode_val else 0})")
else:
    print("❌ CSV 欄位不足，需要至少 3 個欄位 (Column C)")
    exit()

# 搜尋目標條碼
print("\n" + "=" * 60)
print(f"🔍 搜尋條碼：{TEST_BARCODE}")
print("=" * 60)

# 方法 1：直接比對
print("\n方法 1：直接字串比對")
matches = df[df[barcode_col] == TEST_BARCODE]
print(f"  找到 {len(matches)} 筆完全匹配的記錄")

# 方法 2：去除空格後比對
print("\n方法 2：去除空格後比對")
df_trimmed = df.copy()
df_trimmed[barcode_col] = df_trimmed[barcode_col].str.strip()
matches_trimmed = df_trimmed[df_trimmed[barcode_col] == TEST_BARCODE]
print(f"  找到 {len(matches_trimmed)} 筆匹配的記錄")

# 方法 3：模糊搜尋（包含測試條碼）
print("\n方法 3：模糊搜尋（包含測試條碼）")
matches_partial = df[df[barcode_col].str.contains(TEST_BARCODE, na=False)]
print(f"  找到 {len(matches_partial)} 筆包含 '{TEST_BARCODE}' 的記錄")

# 方法 4：數字比對（如果 CSV 中是數字格式）
print("\n方法 4：數字格式比對")
try:
    df_numeric = df.copy()
    df_numeric[barcode_col] = pd.to_numeric(df_numeric[barcode_col], errors='coerce')
    matches_numeric = df_numeric[df_numeric[barcode_col] == float(TEST_BARCODE)]
    print(f"  找到 {len(matches_numeric)} 筆數字匹配的記錄")
except:
    print("  ❌ 無法轉換為數字格式")

# 顯示所有相似的條碼
print("\n" + "=" * 60)
print("🔍 所有相似的條碼（包含 '837328' 或 '000050'）")
print("=" * 60)

similar_1 = df[df[barcode_col].str.contains('837328', na=False)]
similar_2 = df[df[barcode_col].str.contains('000050', na=False)]

if len(similar_1) > 0:
    print(f"\n包含 '837328' 的條碼 ({len(similar_1)} 筆):")
    for i in range(min(5, len(similar_1))):
        val = similar_1.iloc[i][barcode_col]
        print(f"  - '{val}' (長度：{len(str(val)) if val else 0})")
    if len(similar_1) > 5:
        print(f"  ... 還有 {len(similar_1) - 5} 筆")

if len(similar_2) > 0:
    print(f"\n包含 '000050' 的條碼 ({len(similar_2)} 筆):")
    for i in range(min(5, len(similar_2))):
        val = similar_2.iloc[i][barcode_col]
        print(f"  - '{val}' (長度：{len(str(val)) if val else 0})")
    if len(similar_2) > 5:
        print(f"  ... 還有 {len(similar_2) - 5} 筆")

# 檢查測試條碼的實際內容
print("\n" + "=" * 60)
print("🔬 測試條碼格式分析")
print("=" * 60)

print(f"\n目標條碼：'{TEST_BARCODE}'")
print(f"長度：{len(TEST_BARCODE)}")
print(f"類型：{type(TEST_BARCODE)}")
print(f"Byte 表示：{TEST_BARCODE.encode('utf-8')}")

# 如果找到匹配，顯示詳細資訊
if len(matches_trimmed) > 0:
    print("\n" + "=" * 60)
    print("✅ 找到匹配記錄！")
    print("=" * 60)
    
    for idx, row in matches_trimmed.iterrows():
        print(f"\n記錄 {idx + 1}:")
        if len(df.columns) > 4:
            print(f"  Column C (Barcode): {row[barcode_col]}")
            print(f"  Column E (Location): {row[df.columns[4]]}")
            print(f"  Column F (Expiry): {row[df.columns[5]]}")
else:
    print("\n" + "=" * 60)
    print("❌ 找不到匹配的條碼")
    print("=" * 60)
    print("\n可能原因:")
    print("  1. CSV 中的條碼有空格或特殊字元")
    print("  2. CSV 中的條碼是數字格式，系統搜尋的是字串格式")
    print("  3. CSV 編碼問題")
    print("  4. Column 索引配置錯誤")
    print("\n建議:")
    print("  1. 打開 CSV 檔案，複製 837328000050 這格內容")
    print("  2. 貼到文字編輯器檢查是否有隱藏字元")
    print("  3. 確認 CSV 的 Column C 確實是條碼欄位")

print("\n" + "=" * 60)
print("診斷完成")
print("=" * 60)
