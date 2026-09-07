import streamlit as st
from supabase import create_client
from datetime import datetime

def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def update_lotto_excel(round_num, nums, bonus, date_str=None, file_path=None):
    supabase = init_supabase()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    sorted_nums = sorted(nums)
    
    # DB 중복 회차 검증
    existing = supabase.table("lotto_history").select("round").eq("round", round_num).execute()
    if len(existing.data) > 0:
        return False
        
    # DB에 인서트
    data = {
        "round": round_num,
        "draw_date": date_str,
        "n1": sorted_nums[0], "n2": sorted_nums[1], "n3": sorted_nums[2],
        "n4": sorted_nums[3], "n5": sorted_nums[4], "n6": sorted_nums[5],
        "bonus": bonus
    }
    supabase.table("lotto_history").insert(data).execute()
    return True

def save_log_to_db(target_round, log_text):
    supabase = init_supabase()
    data = {
        "target_round": target_round,
        "log_text": log_text
    }
    supabase.table("lotto_logs").insert(data).execute()