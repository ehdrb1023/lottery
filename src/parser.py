import pandas as pd
import streamlit as st
from supabase import create_client

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def load_lotto_data(file_path=None):
    supabase = init_supabase()
    
    # DB에서 전체 데이터 오름차순으로 가져오기
    response = supabase.table("lotto_history").select("*").order("round").execute()
    df = pd.DataFrame(response.data)
    
    # 기존 코드 호환성을 위해 컬럼명 맵핑
    df.rename(columns={"round": "회차", "draw_date": "날짜"}, inplace=True)
    
    return df, "Supabase Database"