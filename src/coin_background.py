import json
from pathlib import Path

import streamlit as st

_JS_PATH = Path(__file__).with_name("coin_background.js")


class CoinBackground:
    """화면 양옆에 금화가 떠다니는 고정 배경 (canvas + Matter.js).

    이미지 파일 없이 canvas로 금화를 그린다. 페이지에 한 번만 render() 하면 된다.
    """

    def __init__(
        self,
        desktop_count=20,
        mobile_count=8,
        column_width=720,
        click_radius=90,
        desktop_radius=(34, 44),
        mobile_radius=(26, 32),
        desktop_opacity=0.95,
        mobile_opacity=0.26,
        mobile_breakpoint=700,
        sound_toggle=True,
        matter_url="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js",
    ):
        self.options = {
            "desktopCount": desktop_count,
            "mobileCount": mobile_count,
            "columnWidth": column_width,
            "clickRadius": click_radius,
            "desktopRadius": list(desktop_radius),
            "mobileRadius": list(mobile_radius),
            "desktopOpacity": desktop_opacity,
            "mobileOpacity": mobile_opacity,
            "mobileBreakpoint": mobile_breakpoint,
            "soundToggle": sound_toggle,
            "matterUrl": matter_url,
        }

    def render(self):
        js = _JS_PATH.read_text(encoding="utf-8").replace("__OPTS__", json.dumps(self.options))
        st.html(
            f'<div class="coin-bg-host"></div><script>{js}</script>',
            unsafe_allow_javascript=True,
        )
