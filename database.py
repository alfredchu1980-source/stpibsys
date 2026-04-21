# database.py
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd
from config import CONFIG

def get_supabase_client() -> Client:
    try:
        url = st.secrets.get("SUPABASE_URL") or CONFIG.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") or CONFIG.get("SUPABASE_KEY")
        if not url or not key:
            st.error("Supabase configuration not found!")
            st.stop()
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        st.stop()

supabase = get_supabase_client()

def init_database():
    pass

def get_all_batches():
    try:
        res = supabase.table("batches").select("batch_id").in_("status", ["Active", "completed", "pending"]).order("created_at", desc=True).execute()
        return [r["batch_id"] for r in res.data]
    except:
        return []

def get_batch_info(batch_id):
    res = supabase.table("batches").select("*").eq("batch_id", batch_id).execute()
    return res.data[0] if res.data else None

def create_batch(batch_id, customer_name, status='pending', source='Office'):
    data = {"batch_id": batch_id, "customer_name": customer_name, "status": status, "source": source, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    try:
        supabase.table("batches").upsert(data).execute()
        return True
    except Exception as e:
        st.error(f"Create batch failed: {str(e)}")
        return False

def update_batch_status(batch_id, status):
    try:
        supabase.table("batches").update({"status": status}).eq("batch_id", batch_id).execute()
        return True
    except:
        return False

def delete_batch(batch_id):
    try:
        supabase.table("products").delete().eq("batch_id", batch_id).execute()
        supabase.table("batches").delete().eq("batch_id", batch_id).execute()
        return True
    except:
        return False

def get_products_by_batch(batch_id):
    res = supabase.table("products").select("*").eq("batch_id", batch_id).execute()
    if not res.data:
        return pd.DataFrame()
    return pd.DataFrame(res.data)

def insert_product(data_tuple):
    data = {
        "batch_id": data_tuple[0],
        "seq": data_tuple[1],
        "barcode": data_tuple[2],
        "sku_id": data_tuple[3],
        "product_name": data_tuple[4],
        "expected_qty": data_tuple[5],
        "actual_qty": str(data_tuple[6]) if data_tuple[6] else "",
        "location": data_tuple[7],
        "expiry_date": data_tuple[8],
        "worker1": data_tuple[9],
        "worker2": data_tuple[10],
        "updated_at": data_tuple[11],
        "lot": data_tuple[12]
    }
    try:
        response = supabase.table("products").insert(data).execute()
        st.success("Write successful!")
        return True
    except Exception as e:
        st.error(f"Insert failed: {str(e)}")
        try:
            update_data = {
                "actual_qty": str(data_tuple[6]) if data_tuple[6] else "",
                "location": data_tuple[7],
                "expiry_date": data_tuple[8],
                "worker1": data_tuple[9],
                "worker2": data_tuple[10],
                "updated_at": data_tuple[11]
            }
            supabase.table("products").update(update_data).eq("batch_id", data_tuple[0]).eq("seq", data_tuple[1]).execute()
            st.success("Update successful!")
            return True
        except Exception as e2:
            st.error(f"Update failed: {str(e2)}")
            return False

def update_product_qty(batch_id, seq, qty, w1, w2):
    data = {"actual_qty": str(qty), "worker1": w1, "worker2": w2, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    try:
        supabase.table("products").update(data).eq("batch_id", batch_id).eq("seq", seq).execute()
        return True
    except Exception as e:
        st.error(f"Update qty failed: {str(e)}")
        return False

def reset_product_record(batch_id, seq):
    try:
        supabase.table("products").update({"actual_qty": "", "location": "", "expiry_date": "", "updated_at": ""}).eq("batch_id", batch_id).eq("seq", seq).execute()
        return True
    except:
        return False

def delete_product_record(batch_id, seq):
    try:
        supabase.table("products").delete().eq("batch_id", batch_id).eq("seq", seq).execute()
        return True
    except:
        return False

def get_pending_count():
    res = supabase.table("batches").select("batch_id", count="exact").eq("status", CONFIG["STATUS"]["CLIENT_SUBMITTED"]).execute()
    return res.count if res.count is not None else 0

# 新增：根據狀態獲取批次 (修復 office_admin.py 和 tv_dashboard.py 的錯誤)
def get_batches_by_status(status_list):
    try:
        res = supabase.table("batches").select("*").in_("status", status_list).order("created_at", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Get batches by status failed: {str(e)}")
        return pd.DataFrame()
