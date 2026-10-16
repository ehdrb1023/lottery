import streamlit as st

from src.lotto_ball import LottoBall

_FONTS = """
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
"""

# 토스(toss.im)처럼 한 화면에 한 가지씩 또렷하게. 글꼴은 Pretendard 하나, 위계는 크기·굵기·회색 농도로만 나눈다.
_CSS = """
:root{
  --bg:#151515; --card:#1F1F1F; --ink:#EDE6D8; --body:#CFC8BA; --muted:#A39E93;
  --gold:#C9A44C; --gold-hi:#D6B461;
  --sans:'Pretendard',-apple-system,'Segoe UI',system-ui,sans-serif;
}
html{font-size:17px;background:var(--bg);}
body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"],[data-testid="stMain"]{background:transparent !important;}
html,body,.stApp,.stApp p,.stApp li,.stApp label,.stApp span,.stApp div,.stApp input,.stApp button,.stApp h1,.stApp h2,.stApp h3{
  font-family:var(--sans) !important;}
.stApp{color:var(--ink);word-break:keep-all;}
.stApp *{font-variant-numeric:tabular-nums;}
[data-testid="stAppViewContainer"]{position:relative;z-index:1;}

[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="stDecoration"],
[data-testid="stToolbar"],.stAppDeployButton,[data-testid="stHeaderActionElements"],footer,#MainMenu{display:none !important;}
[data-testid="stElementContainer"]:has(.coin-bg-host),[data-testid="stElementContainer"]:has(.intro-host){display:none;}

/* 콘텐츠 영역: 세로 구분선 없이 여백으로 구분 */
[data-testid="stMainBlockContainer"]{max-width:720px;margin:0 auto;padding:3.4rem 1.5rem 4rem;
  background:transparent;height:auto !important;flex-shrink:0 !important;min-height:100vh;}
[data-testid="stVerticalBlock"]{gap:1.1rem;}
@media (max-width:700px){
  [data-testid="stMainBlockContainer"]{padding:3.4rem 1.1rem 9rem !important;background:rgba(21,21,21,.55);}
}

/* 글자 위계 */
h1,[data-testid="stHeading"] h1{font-size:1.9rem !important;line-height:1.3 !important;font-weight:700 !important;
  letter-spacing:-.02em !important;color:var(--ink);margin:0 !important;padding:.2rem 0 0 !important;}
h2,h3,[data-testid="stHeading"] h2,[data-testid="stHeading"] h3{font-size:1.18rem !important;line-height:1.4 !important;
  font-weight:600 !important;letter-spacing:-.01em !important;color:var(--ink);margin:0 !important;padding:0 !important;}
.stApp p,.stApp li,[data-testid="stMarkdownContainer"]{font-size:1rem;line-height:1.6;font-weight:400;color:var(--body);}
[data-testid="stCaptionContainer"],.caption{font-size:.88rem !important;line-height:1.5;color:var(--muted) !important;}
strong,b{font-weight:600;color:var(--ink);}
@media (max-width:700px){h1,[data-testid="stHeading"] h1{font-size:1.75rem !important;}}

/* 머리말 */
.hero{padding:.2rem 0 .2rem;}
.hero h1{margin:0 0 .35rem !important;}
.hero .sub{margin:0;font-size:.88rem;color:var(--muted);}

/* 카드: 배경보다 살짝 밝은 회색, 모서리 20px, 테두리·그림자 없음 */
.card,[data-testid="stForm"],.st-key-games{background:var(--card) !important;border:none !important;
  border-radius:20px !important;box-shadow:none !important;}
.card{padding:1.3rem 1.4rem;margin:0;}
.card .label{margin:0 0 .85rem;font-size:.88rem;line-height:1.4;color:var(--muted);}
[data-testid="stForm"]{padding:1.4rem;}
[data-testid="stAlert"] > div,[data-baseweb="notification"]{border-radius:16px !important;border:none !important;}
@media (max-width:480px){.card{padding:1.1rem 1.1rem;}}

/* 알약 세그먼트 탭 */
[data-testid="stElementContainer"]:has([data-testid="stRadio"]),[data-testid="stRadio"],[data-testid="stRadioGroup"]{width:100% !important;}
[data-testid="stRadio"] [role="radiogroup"]{background:var(--card);border-radius:999px;padding:4px;gap:2px;
  flex-wrap:nowrap;width:100%;}
[data-testid="stRadio"] [role="radiogroup"] > *{flex:1 1 0;min-width:0;display:flex;}
[data-testid="stRadioOption"]{flex:1 1 0;width:100%;display:flex !important;align-items:center;justify-content:center;min-height:46px;margin:0;padding:0 .4rem;
  border-radius:999px;cursor:pointer;transition:background .2s;}
/* Streamlit 버전마다 안쪽 단계 수가 달라서, 글자를 감싼 상자만 가운데 정렬하고 동그라미 표시는 통째로 숨긴다 */
[data-testid="stRadioOption"] div:has([data-testid="stMarkdownContainer"]){display:flex;align-items:center;justify-content:center;width:100%;}
[data-testid="stRadioOption"] div:not(:has([data-testid="stMarkdownContainer"])):not([data-testid="stMarkdownContainer"]){display:none !important;}
[data-testid="stRadioOption"] [data-testid="stMarkdownContainer"]{width:auto;}
[data-testid="stRadioOption"] p{font-size:.94rem;font-weight:500;color:var(--muted);white-space:nowrap;text-align:center;}
[data-testid="stRadioOption"][data-selected="true"]{background:var(--ink);}
[data-testid="stRadioOption"][data-selected="true"] p{color:#1A1A1A;font-weight:600;}
html.kb [data-testid="stRadioOption"]:has(input:focus-visible){outline:2px solid var(--gold);outline-offset:2px;}
[data-testid="stRadioOption"]{outline:none;}
@media (max-width:480px){[data-testid="stRadioOption"]{padding:0 .15rem;}[data-testid="stRadioOption"] p{font-size:.86rem;letter-spacing:-.03em;}}

/* 조건 목록: 체크 아이콘 + 짧은 한 줄 */
.checks{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.7rem;}
.checks li{position:relative;padding-left:2.05rem;line-height:1.5;color:var(--body);}
.checks li::before{content:"";position:absolute;left:0;top:.08rem;width:1.3rem;height:1.3rem;border-radius:50%;
  background:rgba(201,164,76,.16);}
.checks li::after{content:"";position:absolute;left:.44rem;top:.3rem;width:.42rem;height:.7rem;
  border:solid var(--gold);border-width:0 2px 2px 0;transform:rotate(40deg) scale(.9);}

/* 게임 수: 큰 숫자 가운데 + 둥근 -/+ */
.st-key-games{padding:1.1rem 1.2rem 1.3rem;}
.st-key-games [data-testid="stWidgetLabel"]{justify-content:center;margin-bottom:.4rem;}
.st-key-games [data-testid="stWidgetLabel"] p{font-size:.88rem;color:var(--muted);text-align:center;}
.st-key-games [data-testid="stNumberInputContainer"]{display:flex;align-items:center;gap:.6rem;background:transparent;border:none;height:auto !important;min-height:3.6rem;overflow:visible !important;}
.st-key-games [data-testid="stNumberInputContainer"] > div:not([data-baseweb]){display:contents;}
.st-key-games [data-testid="stNumberInputContainer"] > div{background:transparent !important;border:none !important;}
.st-key-games input[data-testid="stNumberInputField"]{order:1;flex:1;min-width:0;text-align:center;
  font-size:2.6rem;font-weight:700;letter-spacing:-.02em;color:var(--ink);background:transparent !important;
  border:none !important;padding:0;height:3.6rem;}
.st-key-games [data-testid="stNumberInputStepDown"],.st-key-games [data-testid="stNumberInputStepUp"]{
  width:3.1rem;height:3.1rem;min-width:3.1rem;aspect-ratio:1;border-radius:50% !important;overflow:visible;border:none !important;background:#2B2B2B !important;
  color:var(--ink);display:flex;align-items:center;justify-content:center;flex:0 0 auto;
  transition:transform .12s ease,background .2s;}
.st-key-games [data-testid="stNumberInputStepDown"]{order:0;}
.st-key-games [data-testid="stNumberInputStepUp"]{order:2;}
.st-key-games [data-testid="stNumberInputStepDown"] svg,.st-key-games [data-testid="stNumberInputStepUp"] svg{width:14px;height:14px;}
.st-key-games [data-testid="stNumberInputStepDown"]:hover,.st-key-games [data-testid="stNumberInputStepUp"]:hover{background:#363636 !important;}
.st-key-games [data-testid="stNumberInputStepDown"]:active,.st-key-games [data-testid="stNumberInputStepUp"]:active{transform:scale(.94);}

/* 버튼: 폭을 꽉 채운 큰 금색 버튼. 누르면 살짝 작아졌다 돌아온다 */
.stButton > button,[data-testid="stFormSubmitButton"] > button{width:100%;min-height:3.6rem;padding:0 1.6rem;border-radius:18px;
  font-size:1.1rem;font-weight:700;box-shadow:none;transition:transform .12s ease,background .2s;}
.stButton > button[kind="primary"],[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]{
  background:var(--gold);border:none;color:#1A1A1A;}
.stButton > button[kind="primary"]:hover,[data-testid="stFormSubmitButton"] > button:hover{background:var(--gold-hi);color:#1A1A1A;border:none;}
.stButton > button:active,[data-testid="stFormSubmitButton"] > button:active{transform:scale(.97);}
.stButton > button:focus-visible,[data-testid="stFormSubmitButton"] > button:focus-visible{outline:2px solid var(--ink);outline-offset:3px;}
@media (max-width:700px){
  .stButton{position:fixed;left:0;right:0;bottom:0;z-index:50;padding:1.4rem 1.1rem calc(.9rem + env(safe-area-inset-bottom));
    background:linear-gradient(180deg,rgba(21,21,21,0),rgba(21,21,21,.94) 38%);}
}

[data-testid="stBaseButton-primary"] p,[data-testid="stBaseButton-primaryFormSubmit"] p{color:#1A1A1A !important;font-size:1.1rem;font-weight:700;}

/* 입력창 */
[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input{font-size:1rem;}
[data-baseweb="input"],[data-baseweb="base-input"]{border-radius:14px !important;}

/* 추천 결과: 세트마다 카드 한 장 */
.draw-list{display:flex;flex-direction:column;gap:.8rem;}
.draw-card{background:var(--card);border-radius:20px;padding:1.15rem 1.3rem 1.2rem;
  animation:card-in .28s ease both;}
.draw-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:.8rem;}
.draw-idx{font-size:.88rem;color:var(--muted);}
.copy-btn{min-height:40px;padding:0 16px;border:none;border-radius:999px;background:#2B2B2B;color:var(--ink);
  font:600 .88rem/1 var(--sans);cursor:pointer;transition:transform .12s ease,background .2s;}
.copy-btn:hover{background:#363636;} .copy-btn:active{transform:scale(.95);}
.copy-btn.done{background:var(--gold);color:#1A1A1A;}
.copy-btn:focus-visible{outline:2px solid var(--gold);outline-offset:2px;}
.stApp .draw-meta{margin:.85rem 0 0;font-size:.88rem;line-height:1.55;color:var(--muted);}
@keyframes card-in{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:none;}}

/* 표 */
[data-testid="stTable"] table{font-size:.94rem;}
[data-testid="stTable"] th,[data-testid="stTable"] td{border-color:#2A2A2A !important;}

/* 푸터 */
.site-footer{margin-top:1.4rem;padding-top:.4rem;color:var(--muted);font-size:.88rem;line-height:1.6;}
.site-footer p{margin:0;font-size:.88rem;color:var(--muted);}

@media (prefers-reduced-motion:reduce){*{transition:none !important;scroll-behavior:auto !important;}.draw-card{animation:none;}}
"""

# 결과 카드의 "복사" 버튼은 한 번만 연결해 두면 된다 (화면이 다시 그려져도 유지)
_COPY_JS = """
(function () {
  if (window.__copyBound) return;
  window.__copyBound = true;
  document.addEventListener('keydown', function (e) { if (e.key === 'Tab') document.documentElement.classList.add('kb'); });
  document.addEventListener('pointerdown', function () { document.documentElement.classList.remove('kb'); });
  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-copy]') : null;
    if (!b) return;
    var text = b.getAttribute('data-copy');
    function ok() {
      b.textContent = '복사했어요';
      b.classList.add('done');
      setTimeout(function () { b.textContent = '복사'; b.classList.remove('done'); }, 1600);
    }
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.cssText = 'position:fixed;opacity:0;left:-9999px';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); ok(); } catch (err) {}
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok).catch(fallback);
    } else { fallback(); }
  });
})();
"""


def inject_theme():
    st.markdown(f"<style>{_FONTS}{LottoBall.css()}{_CSS}</style>", unsafe_allow_html=True)
    st.html(f"<script>{_COPY_JS}</script>", unsafe_allow_javascript=True)


def render_header(latest_round, recent_numbers, recent_bonus):
    st.markdown(
        '<div class="hero"><h1>로또 번호 추천</h1>'
        '<p class="sub">재미로 보는 번호 추천이에요</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="card"><p class="label">{latest_round}회 당첨번호</p>'
        f'{LottoBall.row(recent_numbers, bonus=recent_bonus)}</div>',
        unsafe_allow_html=True,
    )


def render_conditions(items):
    lis = "".join(f"<li>{t}</li>" for t in items)
    st.markdown(f'<div class="card"><ul class="checks">{lis}</ul></div>', unsafe_allow_html=True)


def render_draws(combos):
    cards = []
    for i, r in enumerate(combos, 1):
        base = (i - 1) * 0.28 + 0.1
        carry = ", ".join(str(x) for x in r["carry"]) or "없음"
        top10 = ", ".join(str(x) for x in r["top10"]) or "없음"
        copy_text = " ".join(f"{x:02d}" for x in r["combo"])
        cards.append(
            f'<div class="draw-card" style="animation-delay:{base:.2f}s">'
            f'<div class="draw-head"><span class="draw-idx">{i}번째 세트</span>'
            f'<button type="button" class="copy-btn" data-copy="{copy_text}">복사</button></div>'
            f'{LottoBall.row(r["combo"], base_delay=base + 0.15)}'
            f'<p class="draw-meta">이월수 {carry} · {r["sections"]}구간 · 동끝수 {r["dup_pairs"]}쌍'
            f'<br>많이 나온 번호 {top10}</p></div>'
        )
    st.markdown(f'<div class="draw-list">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_footer():
    st.markdown(
        '<div class="site-footer"><p>로또 번호는 무작위예요. 당첨을 보장하지 않아요.</p></div>',
        unsafe_allow_html=True,
    )
