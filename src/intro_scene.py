import base64
import json
from pathlib import Path

import streamlit as st

from src.laptop_frame import LaptopFrame

_JS_PATH = Path(__file__).with_name("intro_scene.js")
_IMAGE_PATH = Path(__file__).resolve().parent.parent / "static" / "intro.webp"


def _image_src(fallback_url):
    """사진을 코드에 직접 포함(data URL)한다. 배포 환경의 정적 파일 서빙 설정과 무관하게 항상 보인다."""
    try:
        data = base64.b64encode(_IMAGE_PATH.read_bytes()).decode("ascii")
        return f"data:image/webp;base64,{data}"
    except OSError:
        return fallback_url

_CSS = """
html.intro-on,html.intro-on body{overflow:hidden !important;}
html.intro-on .stApp{position:fixed !important;left:0 !important;top:0 !important;z-index:99992 !important;
  transform-origin:0 0 !important;overflow:hidden !important;background:#151515 !important;pointer-events:none !important;}

#intro-root{position:fixed;inset:0;z-index:99990;background:#0b0b0b;overflow:hidden;}
#intro-under,#intro-over{position:absolute;inset:0;pointer-events:none;will-change:transform,opacity;}
#intro-over{position:fixed;z-index:99993;}
.is-photo{position:absolute;left:-3%;right:-3%;top:-38vh;height:150vh;background:#0e1420 center/cover no-repeat;
  filter:blur(2.5px) brightness(.74) saturate(.95);}
.is-vig{position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 42%,rgba(0,0,0,0) 52%,rgba(0,0,0,.55) 100%),
             linear-gradient(180deg,rgba(0,0,0,.25),rgba(0,0,0,0) 30%);}
.is-loader{position:absolute;left:50%;top:50%;width:30px;height:30px;margin:-15px 0 0 -15px;
  border:2px solid rgba(237,230,216,.18);border-top-color:#C9A44C;border-radius:50%;
  animation:is-spin .9s linear infinite;transition:opacity .4s;}
@keyframes is-spin{to{transform:rotate(360deg);}}
#intro-root.is-ready .is-loader{opacity:0;}
#intro-under{opacity:0;transition:opacity .8s ease;}
#intro-root.is-ready #intro-under{opacity:1;}

#intro-ui{position:fixed;left:0;right:0;bottom:0;z-index:99994;pointer-events:none;text-align:center;
  padding:0 20px max(26px,env(safe-area-inset-bottom));font-family:Pretendard,system-ui,sans-serif;
  opacity:0;transition:opacity .8s ease .3s;}
#intro-root.is-ready ~ #intro-ui{opacity:1;}
.is-cap{margin:0 0 .45rem;font-size:1.35rem;font-weight:600;letter-spacing:-.02em;color:#EDE6D8;
  text-shadow:0 2px 18px rgba(0,0,0,.7);}
.is-hint{margin:0;font-size:1.0625rem;color:rgba(237,230,216,.74);text-shadow:0 2px 14px rgba(0,0,0,.7);}
.is-arrow{display:block;margin:.55rem auto 0;width:22px;height:22px;animation:is-bob 1.8s ease-in-out infinite;}
@keyframes is-bob{0%,100%{transform:translateY(0);opacity:.55;}50%{transform:translateY(7px);opacity:1;}}

#intro-scroller{position:fixed;inset:0;z-index:99995;overflow-y:scroll;overflow-x:hidden;
  scrollbar-width:none;-ms-overflow-style:none;overscroll-behavior:none;cursor:pointer;}
#intro-scroller::-webkit-scrollbar{display:none;}
#intro-spacer{width:1px;}
#intro-skip{position:fixed;top:max(14px,env(safe-area-inset-top));right:16px;z-index:99996;min-height:44px;
  padding:0 18px;border:1px solid rgba(237,230,216,.28);border-radius:999px;cursor:pointer;
  background:rgba(14,14,14,.55);color:#EDE6D8;font:500 16px/1 Pretendard,system-ui,sans-serif;
  backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);}
#intro-skip:hover{background:rgba(40,40,40,.75);}
#intro-skip:focus-visible{outline:2px solid #C9A44C;outline-offset:3px;}
@media (max-width:700px){.is-cap{font-size:1.15rem;}.is-hint{font-size:1rem;}
  .is-photo{top:-27vh;height:112vh;background-position:66% 50%;}}
@media (prefers-reduced-motion:reduce){.is-arrow{animation:none;}#intro-under,#intro-ui{transition:none;}}
"""


class IntroScene:
    """서울 야경 → 노트북 화면 속으로 들어가는 인트로 (GSAP + ScrollTrigger).

    노트북 화면 안의 사이트는 이미지가 아니라 실제 앱 화면(DOM)을 축소해서 보여준다.
    한 번 본 방문자는 localStorage 로 기억해 바로 본 화면으로 간다.
    주소 뒤에 ?intro=replay 를 붙이면 다시 볼 수 있다.
    """

    def __init__(
        self,
        image_url="/app/static/intro.webp",
        caption="차분하게, 오늘의 번호를 골라보세요",
        hint="스크롤하거나 화면을 눌러보세요",
        storage_key="lotto-intro-seen",
        gsap_url="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js",
        scroll_trigger_url="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js",
        mobile_breakpoint=700,
    ):
        self.laptop = LaptopFrame()
        self.options = {
            "imageUrl": _image_src(image_url),
            "caption": caption,
            "hint": hint,
            "storageKey": storage_key,
            "gsapUrl": gsap_url,
            "scrollTriggerUrl": scroll_trigger_url,
            "mobileBreakpoint": mobile_breakpoint,
            "underHtml": self.laptop.under_html(),
            "overHtml": self.laptop.over_html(),
        }

    def render(self):
        st.markdown(f"<style>{self.laptop.css()}{_CSS}</style>", unsafe_allow_html=True)
        opts = json.dumps(self.options).replace("<", "\\u003c")  # HTML 정화기가 스크립트를 지우지 않도록
        js = _JS_PATH.read_text(encoding="utf-8").replace("__OPTS__", opts)
        st.html(
            f'<div class="intro-host"></div><script>{js}</script>',
            unsafe_allow_javascript=True,
        )
