# check_users.py
# 診斷腳本：檢查用戶資料庫結構

import streamlit as st
from supabase import create_client
from config import CONFIG

st.title("🔍 用戶資料庫診斷工具")

# 連接 Supabase
url = st.secrets.get("SUPABASE_URL") or CONFIG.get("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or CONFIG.get("SUPABASE_KEY")
supabase = create_client(url, key)

st.success("✅ 資料庫連接成功")

# 獲取所有用戶
st.subheader("📋 所有用戶列表")
res = supabase.table("users").select("*").execute()

if res.data:
    st.write(f"共找到 {len(res.data)} 個用戶")
    
    # 顯示欄位名稱
    st.subheader("📊 資料庫欄位結構")
    if len(res.data) > 0:
        columns = list(res.data[0].keys())
        st.write("欄位名稱：", columns)
        
        # 檢查關鍵欄位
        st.subheader("✅ 欄位檢查")
        if "password_hash" in columns:
            st.success("✅ 找到 `password_hash` 欄位 (正確)")
        else:
            st.error("❌ 找不到 `password_hash` 欄位")
            
        if "password" in columns:
            st.warning("⚠️ 找到 `password` 欄位 (舊版欄位)")
        
        if "username" in columns:
            st.success("✅ 找到 `username` 欄位")
        
        if "role" in columns:
            st.success("✅ 找到 `role` 欄位")
    
    # 顯示用戶數據（隱藏密碼）
    st.subheader("👥 用戶數據預覽")
    for user in res.data:
        st.write(f"- **{user.get('username', 'N/A')}** (角色：{user.get('role', 'N/A')})")
else:
    st.error("❌ 資料庫中沒有用戶數據")

# 測試特定用戶
st.subheader("🔎 測試特定用戶")
test_username = st.text_input("輸入用戶名稱", placeholder="例如：TEST")
if st.button("查詢用戶"):
    if test_username:
        res = supabase.table("users").select("*").eq("username", test_username.upper()).execute()
        if res.data:
            st.success(f"✅ 找到用戶：{res.data[0]}")
        else:
            st.error(f"❌ 找不到用戶：{test_username.upper()}")
