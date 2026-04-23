# reference_module/scanner.py
"""
掃描時顯示參考表 UI
"""

import streamlit as st
import pandas as pd

try:
    from hooks import REFERENCE_SHOW_IN_SCAN
except ImportError:
    REFERENCE_SHOW_IN_SCAN = True


def render_reference_scanner(barcode):
    """
    顯示參考表查詢結果（表格形式，不顯示條碼）
    
    參數:
        barcode: 已掃描的條碼
    """
    if not REFERENCE_SHOW_IN_SCAN:
        return
    
    try:
        from .ref_table import search_by_barcode
        results = search_by_barcode(barcode)
        
        if results:
            st.divider()
            st.info(f"📚 參考資料（找到 {len(results)} 筆記錄）")
            
            # 轉換為 DataFrame 並顯示表格（不顯示條碼欄位）
            ref_df = pd.DataFrame(results)
            
            # 只顯示 location 和 expiry_date 欄位
            display_df = ref_df[['location', 'expiry_date']].copy()
            display_df.columns = ['📍 儲位', '📅 到期日']
            
            # 將空值顯示為「N/A」
            display_df['📍 儲位'] = display_df['📍 儲位'].replace('', 'N/A')
            display_df['📅 到期日'] = display_df['📅 到期日'].replace('', 'N/A')
            
            # 自訂 CSS - 放大表格字體（22px）
            st.markdown("""
                <style>
                /* 參考表表格字體大小 - 22px */
                .reference-table-22 .dataframe {
                    font-size: 22px !important;
                }
                .reference-table-22 .dataframe td {
                    font-size: 22px !important;
                    padding: 14px !important;
                }
                .reference-table-22 .dataframe th {
                    font-size: 22px !important;
                    font-weight: bold !important;
                    padding: 14px !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # 使用表格顯示（22px 大字體）
            table_html = f"""
            <div class="reference-table-22">
                {display_df.to_html(index=False, classes='dataframe', border=0)}
            </div>
            """
            st.markdown(table_html, unsafe_allow_html=True)
            
            # 如果有空值，顯示提示
            has_empty = (display_df['📍 儲位'] == 'N/A').any() or (display_df['📅 到期日'] == 'N/A').any()
            if has_empty:
                st.warning("⚠️ 部分記錄的儲位或到期日為空，請參考其他資料來源")
            else:
                st.caption("💡 提示：已按到期日升序排列")
    except Exception as e:
        # 參考表不存在或錯誤時不顯示任何內容（不影響正常使用）
        pass
