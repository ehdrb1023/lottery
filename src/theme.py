import streamlit as st

_FONTS = """
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;700&display=swap');
"""

_CSS = """
:root{
  --bg:#151515; --panel:rgba(21,21,21,.88); --ink:#EDE6D8; --muted:#B5AD9C;
  --gold:#C9A44C; --line:rgba(201,164,76,.28);
  --sans:'Pretendard',-apple-system,'Segoe UI',sans-serif;
  --serif:'Noto Serif KR','Noto Serif CJK KR',serif;
}
html{font-size:17px;background:var(--bg);}
body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"],[data-testid="stMain"]{
  background:transparent !important;
}
html,body,.stApp,.stApp p,.stApp li,.stApp label,.stApp span,.stApp div,.stApp input,.stApp button{
  font-family:var(--sans);
}
.stApp{color:var(--ink);word-break:keep-all;}
[data-testid="stAppViewContainer"]{position:relative;z-index:1;}

/* 불필요한 요소 정리 */
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],
[data-testid="stDecoration"],[data-testid="stToolbar"],.stAppDeployButton,
[data-testid="stHeaderActionElements"],footer,#MainMenu{display:none !important;}
[data-testid="stElementContainer"]:has(.coin-bg-host){display:none;}

/* 가운데 720px 컬럼 */
[data-testid="stMainBlockContainer"]{
  max-width:720px;margin:0 auto;padding:3.2rem 1.6rem 3rem;
  background:var(--panel);border-left:1px solid var(--line);border-right:1px solid var(--line);
  min-height:100vh;
}
@media (max-width:700px){
  [data-testid="stMainBlockContainer"]{padding:2rem 1.1rem 2.4rem;background:rgba(21,21,21,.72);
    border-left:none;border-right:none;}
}

/* 글자 */
h1,h2,h3,[data-testid="stHeading"] *{font-family:var(--serif) !important;color:var(--ink);
  font-weight:700;letter-spacing:-.01em;}
h1{font-size:2.1rem !important;line-height:1.3;}
h1,h2,h3{word-break:keep-all !important;overflow-wrap:break-word;}
@media (max-width:700px){[data-testid="stHeading"] h1,[data-testid="stHeading"] h1 *{font-size:1.55rem !important;word-break:keep-all !important;}}
h2,h3{font-size:1.45rem !important;line-height:1.4;}
.stApp p,.stApp li,[data-testid="stMarkdownContainer"]{font-size:1rem;line-height:1.75;}
[data-testid="stCaptionContainer"],small{font-size:1rem !important;color:var(--muted);}
strong{color:var(--ink);}

/* 머리말 */
.hero{padding-bottom:1.1rem;margin-bottom:.4rem;border-bottom:1px solid var(--line);}
.hero .eyebrow{color:var(--gold);letter-spacing:.14em;font-size:1rem;margin:0 0 .35rem;}
.hero h1{margin:0 0 .6rem;padding:0;}
.hero .latest{color:var(--muted);margin:0;}
.hero .latest b{font-family:var(--serif);font-weight:700;color:var(--ink);letter-spacing:.06em;}

/* 메뉴(가로 라디오) */
[data-testid="stRadio"] [role="radiogroup"]{gap:.2rem 1.7rem;flex-wrap:wrap;}
[data-testid="stRadioOption"]{padding:.5rem .1rem;margin:0;border-bottom:2px solid transparent;
  cursor:pointer;min-height:44px;align-items:center;}
[data-testid="stRadioOption"] > div > div > div:first-child{display:none;}
[data-testid="stRadioOption"] p{font-size:1.06rem;color:var(--muted);}
[data-testid="stRadioOption"][data-selected="true"]{border-bottom-color:var(--gold);}
[data-testid="stRadioOption"][data-selected="true"] p{color:var(--gold);font-weight:700;}
[data-testid="stRadioOption"]:has(input:focus-visible){outline:2px solid var(--gold);outline-offset:2px;}

/* 버튼 */
.stButton > button,[data-testid="stFormSubmitButton"] > button{
  min-height:3.3rem;padding:0 1.6rem;border-radius:4px;font-size:1.06rem;font-weight:700;
  box-shadow:none;transition:background .2s,border-color .2s;
}
.stButton > button[kind="primary"],[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]{
  background:var(--gold);border:1px solid var(--gold);color:#1A1A1A;
}
.stButton > button[kind="primary"]:hover,[data-testid="stFormSubmitButton"] > button:hover{
  background:#D6B461;border-color:#D6B461;color:#1A1A1A;
}
.stButton > button:focus-visible,[data-testid="stFormSubmitButton"] > button:focus-visible{
  outline:2px solid var(--ink);outline-offset:3px;
}

/* 입력창 */
[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input{font-size:1.06rem;min-height:2.8rem;}
[data-testid="stForm"]{border:1px solid var(--line);border-radius:4px;background:transparent;}
[data-testid="stAlert"]{border-radius:4px;}

/* 추천 번호 목록 */
.draw-list{margin:1.4rem 0 .6rem;border-bottom:1px solid var(--line);}
.draw-row{display:grid;grid-template-columns:4rem 1fr;column-gap:1rem;padding:1.15rem 0;
  border-top:1px solid var(--line);}
.draw-idx{font-family:var(--serif);color:var(--gold);font-size:1.1rem;padding-top:.5rem;}
.draw-nums{display:flex;flex-wrap:wrap;gap:.1rem 1.05rem;font-family:var(--serif);font-weight:700;
  font-size:2.1rem;line-height:1.35;color:var(--ink);font-variant-numeric:lining-nums tabular-nums;}
.draw-meta{grid-column:2;margin-top:.25rem;color:var(--muted);font-size:1rem;line-height:1.6;}
@media (max-width:600px){
  .draw-row{grid-template-columns:1fr;}
  .draw-idx{padding-top:0;}
  .draw-nums{font-size:1.85rem;gap:.1rem .8rem;}
  .draw-meta{grid-column:1;}
}

/* 표 */
[data-testid="stTable"] table{font-size:1rem;}
[data-testid="stTable"] th,[data-testid="stTable"] td{border-color:var(--line) !important;}

/* 푸터 */
.site-footer{margin-top:2.6rem;padding-top:1.2rem;border-top:1px solid var(--line);color:var(--muted);
  font-size:1rem;line-height:1.7;}
.site-footer p{margin:0 0 .25rem;font-size:1rem;}

@media (prefers-reduced-motion:reduce){*{transition:none !important;scroll-behavior:auto !important;}}
"""


def inject_theme():
    st.markdown(f"<style>{_FONTS}{_CSS}</style>", unsafe_allow_html=True)


def render_header(latest_round, recent_numbers, recent_bonus):
    nums = " ".join(f"{int(n):02d}" for n in recent_numbers)
    st.markdown(
        f"""<div class="hero">
<p class="eyebrow">재미로 보는 번호 추천</p>
<h1>로또 번호 추천</h1>
<p class="latest">최신 {latest_round}회 &nbsp;·&nbsp; 당첨 번호 <b>{nums}</b> + 보너스 <b>{recent_bonus}</b></p>
</div>""",
        unsafe_allow_html=True,
    )


def render_draws(combos):
    rows = []
    for i, r in enumerate(combos, 1):
        nums = "".join(f"<span>{x:02d}</span>" for x in r["combo"])
        carry = ", ".join(str(x) for x in r["carry"]) or "없음"
        top10 = ", ".join(str(x) for x in r["top10"]) or "없음"
        rows.append(
            f'<div class="draw-row"><div class="draw-idx">{i:02d}번째</div>'
            f'<div class="draw-nums">{nums}</div>'
            f'<div class="draw-meta">이월수 {carry} &nbsp;·&nbsp; {r["sections"]}구간 &nbsp;·&nbsp; '
            f'동끝수 {r["dup_pairs"]}쌍 &nbsp;·&nbsp; 최다 출현 번호 {top10}</div></div>'
        )
    st.markdown(f'<div class="draw-list">{"".join(rows)}</div>', unsafe_allow_html=True)


def render_footer():
    st.markdown(
        """<div class="site-footer">
<p>재미로 보는 번호 추천입니다.</p>
<p>로또 번호는 무작위이며 당첨을 보장하지 않습니다.</p>
</div>""",
        unsafe_allow_html=True,
    )
