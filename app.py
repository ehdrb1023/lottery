import streamlit as st
import pandas as pd
from datetime import datetime

# 우리가 만든 모듈 임포트
from src.parser import load_lotto_data
from src.stats import LottoStats
from src.filter import LottoFilter
from src.generator import LottoGenerator
from src.updater import update_lotto_excel

# 웹페이지 기본 설정
st.set_page_config(page_title="AI 로또 분석기", page_icon="🎲", layout="wide")

# 데이터 로딩 (캐싱하여 속도 최적화)
@st.cache_data
def get_data_and_engines():
    try:
        df_history, path = load_lotto_data("data/복권_모음집.xlsx")
        stats = LottoStats(df_history)
        l_filter = LottoFilter(df_history)
        generator = LottoGenerator(stats, l_filter)
        return df_history, stats, generator, path
    except Exception as e:
        return None, None, None, str(e)

df_history, stats, generator, excel_path = get_data_and_engines()

if df_history is None:
    st.error(f"데이터를 불러오지 못했습니다. 에러: {excel_path}")
    st.stop()

# 사이드바 (메뉴 네비게이션)
st.sidebar.title("🎲 AI 로또 대시보드")
menu = st.sidebar.radio("메뉴를 선택하세요:", ["🔮 번호 추출기", "📥 최신 회차 업데이트", "📊 역대 당첨 내역"])

st.sidebar.markdown("---")
st.sidebar.info(f"**현재 최신 회차:** {stats.latest_round}회\n\n**최근 당첨 번호:** {stats.recent_numbers} + {stats.recent_bonus}")


# ==========================================
# 1. 번호 추출기 화면
# ==========================================
if menu == "🔮 번호 추출기":
    st.title("🔮 AI 가중치 기반 번호 추출기")
    st.markdown("""
    역대 1~1240회 통계를 바탕으로 **실제 당첨 비율(가중치)**을 적용하여 최적의 번호를 생성합니다.
    - 십의 자리 3~4구간 분배 (37% / 63%)
    - 동끝수 1~2쌍 포함 (70% / 30%)
    - 직전 회차 이월수 1~2개 포함
    - 역대 1, 2등 기출 완전 배제
    """)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        n_sets = st.number_input("생성할 게임 수 (세트)", min_value=1, max_value=20, value=5)
        generate_btn = st.button("🚀 번호 생성하기", type="primary", use_container_width=True)
        
    if generate_btn:
        with st.spinner('수만 개의 조합 중 최적의 번호를 필터링하고 있습니다...'):
            combos = generator.generate(n_sets=n_sets)
            
        st.success(f"제 {stats.latest_round + 1}회차 대비 {n_sets}세트 추출 완료!")
        
        # 결과를 예쁜 표 형태로 가공
        res_df = []
        for i, r in enumerate(combos, 1):
            res_df.append({
                "세트": f"{i:02d}",
                "조합 번호": "  ".join([f"{x:02d}" for x in r['combo']]),
                "이월수": ", ".join(str(x) for x in r['carry']),
                "구간 분포": f"{r['sections']}구간",
                "동끝수": f"{r['dup_pairs']}쌍",
                "Top10 포함": ", ".join(str(x) for x in r['top10'])
            })
            
        st.dataframe(pd.DataFrame(res_df), hide_index=True, use_container_width=True)

        # 👇 [여기가 교체된 부분입니다: 텍스트 파일 대신 Supabase DB에 로그 저장] 👇
        from src.updater import save_log_to_db
        
        target_round = stats.latest_round + 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_content = f"[{now_str}] 제 {target_round}회차 추천 번호 ({n_sets}세트)\n"
        for i, r in enumerate(combos, 1):
            combo_str = ", ".join([f"{x:02d}" for x in r['combo']])
            log_content += f"  - 세트 {i:02d}: {combo_str} (이월: {r['carry']}, {r['sections']}구간)\n"
            
        # Supabase 로그 테이블에 저장
        try:
            save_log_to_db(target_round, log_content)
        except Exception as e:
            st.error(f"로그 저장 중 오류가 발생했습니다: {e}")
            
# ==========================================
# 2. 최신 회차 업데이트 화면
# ==========================================
elif menu == "📥 최신 회차 업데이트":
    st.title("📥 최신 당첨 번호 업데이트")
    st.info("토요일 추첨 후 새로운 당첨 번호를 입력하면 엑셀 파일에 자동으로 누적됩니다.")
    
    with st.form("update_form"):
        r_num = st.number_input("업데이트 할 회차 (예: 1241)", min_value=stats.latest_round + 1, value=stats.latest_round + 1)
        
        st.write("당첨 번호 6개 입력 (공백 없이 숫자만 하나씩 기재 가능)")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        n1 = c1.number_input("번호 1", min_value=1, max_value=45, step=1)
        n2 = c2.number_input("번호 2", min_value=1, max_value=45, step=1)
        n3 = c3.number_input("번호 3", min_value=1, max_value=45, step=1)
        n4 = c4.number_input("번호 4", min_value=1, max_value=45, step=1)
        n5 = c5.number_input("번호 5", min_value=1, max_value=45, step=1)
        n6 = c6.number_input("번호 6", min_value=1, max_value=45, step=1)
        
        bonus = st.number_input("보너스 번호", min_value=1, max_value=45, step=1)
        draw_date = st.date_input("추첨 일자", datetime.today())
        
        submit = st.form_submit_button("엑셀에 저장 및 업데이트", type="primary")
        
        if submit:
            nums = [n1, n2, n3, n4, n5, n6]
            if len(set(nums)) != 6:
                st.error("❌ 중복된 번호가 있습니다. 6개의 각기 다른 번호를 입력해 주세요.")
            else:
                success = update_lotto_excel(
                    round_num=r_num,
                    nums=nums,
                    bonus=bonus,
                    date_str=draw_date.strftime("%Y-%m-%d"),
                    file_path=excel_path
                )
                if success:
                    st.success(f"✨ {r_num}회차 당첨 번호가 성공적으로 저장되었습니다!")
                    # 캐시를 초기화하여 다음 접속/생성 시 새로운 데이터를 물고 오게 함
                    st.cache_data.clear()
                    st.rerun()

# ==========================================
# 3. 역대 당첨 내역 화면
# ==========================================
elif menu == "📊 역대 당첨 내역":
    st.title("📊 역대 당첨 내역 및 데이터베이스")
    
    st.subheader(f"총 {stats.total_draws}회차 데이터")
    st.dataframe(df_history.sort_values('회차', ascending=False), hide_index=True, use_container_width=True)
    
    st.subheader("🔥 역대 최다 출현 번호 Top 10")
    top_df = pd.DataFrame(
        stats.freq_counter.most_common(10),
        columns=["번호", "출현 횟수"]
    )
    # 인덱스를 순위로 변경
    top_df.index = [f"{i}위" for i in range(1, 11)]
    st.table(top_df.T)