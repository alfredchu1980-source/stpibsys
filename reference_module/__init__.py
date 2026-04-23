# reference_module/__init__.py
"""
參考表管理模組
功能：掃描時顯示參考儲位和到期日

版本：1.0.0
作者：System
最後更新：2026-04-23
"""

__version__ = "1.0.0"
__author__ = "System"

try:
    from .ref_table import search_by_barcode, get_reference_info, update_reference_table
    from .scanner import render_reference_scanner
    from .uploader import render_reference_uploader
    from .debug import check_csv_file, test_barcode_search, show_debug_info
    
    __all__ = [
        'search_by_barcode',
        'get_reference_info',
        'update_reference_table',
        'render_reference_scanner',
        'render_reference_uploader',
        'check_csv_file',
        'test_barcode_search',
        'show_debug_info',
    ]
    
    # 模組載入成功標誌
    MODULE_LOADED = True
    
except ImportError as e:
    # 模組載入失敗
    MODULE_LOADED = False
    MODULE_ERROR = str(e)
    
    # 提供空函數避免系統崩潰
    def search_by_barcode(*args, **kwargs):
        return []
    
    def get_reference_info(*args, **kwargs):
        return None
    
    def update_reference_table(*args, **kwargs):
        return False, f"模組未正確載入：{MODULE_ERROR}"
    
    def render_reference_scanner(*args, **kwargs):
        pass
    
    def render_reference_uploader(*args, **kwargs):
        pass
    
    def check_csv_file(*args, **kwargs):
        return {'exists': False, 'valid': False, 'errors': [f"模組未載入：{MODULE_ERROR}"]}
    
    def test_barcode_search(*args, **kwargs):
        return {'found': False, 'errors': [f"模組未載入：{MODULE_ERROR}"]}
    
    def show_debug_info(*args, **kwargs):
        return f"模組未載入：{MODULE_ERROR}", False
    
    __all__ = [
        'search_by_barcode',
        'get_reference_info',
        'update_reference_table',
        'render_reference_scanner',
        'render_reference_uploader',
        'check_csv_file',
        'test_barcode_search',
        'show_debug_info',
        'MODULE_LOADED',
        'MODULE_ERROR',
    ]
