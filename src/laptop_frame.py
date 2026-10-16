class LaptopFrame:
    """CSS로 그린 열린 노트북 + 나무 테이블.

    위치와 크기는 intro_scene.js 가 화면 크기에 맞춰 정한다(좌표 config 없음).
    - under_html(): 앱 화면 뒤에 깔리는 층 (테이블, 빛 번짐, 본체·키보드, 화면 바탕)
    - over_html():  앱 화면 앞에 얹히는 층 (얇은 검은 베젤, 카메라, 유리 반사)
    """

    def under_html(self):
        return (
            '<div class="lf-table"></div>'
            '<div class="lf-glow"></div>'
            '<div class="lf-shadow"></div>'
            '<div class="lf-deck"><div class="lf-keys"></div><div class="lf-pad"></div></div>'
            '<div class="lf-screen-bg"></div>'
        )

    def over_html(self):
        return (
            '<div class="lf-bezel"><i class="lf-cam"></i></div>'
            '<div class="lf-glare"></div>'
        )

    def css(self):
        return """
.lf-table{position:absolute;left:0;right:0;bottom:0;
  background:
    linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,0) 22%),
    repeating-linear-gradient(91deg,rgba(0,0,0,.20) 0 2px,transparent 2px 11px),
    repeating-linear-gradient(89deg,rgba(255,235,200,.035) 0 1px,transparent 1px 27px),
    linear-gradient(180deg,#3b2717 0%,#2a1b0f 55%,#170f08 100%);}
.lf-table::before{content:"";position:absolute;left:0;right:0;top:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba(255,225,180,.22) 30%,rgba(255,225,180,.22) 70%,transparent);}
.lf-glow{position:absolute;pointer-events:none;mix-blend-mode:screen;
  background:radial-gradient(ellipse at 50% 0%,rgba(205,222,255,.26),rgba(205,222,255,.08) 45%,transparent 72%);}
.lf-shadow{position:absolute;pointer-events:none;
  background:radial-gradient(ellipse at 50% 40%,rgba(0,0,0,.55),transparent 70%);}
.lf-deck{position:absolute;
  clip-path:polygon(5.5% 0,94.5% 0,100% 100%,0 100%);
  background:linear-gradient(180deg,#d2d5da 0%,#b4b8be 50%,#92969c 100%);}
.lf-keys{position:absolute;left:9%;right:9%;top:13%;height:50%;border-radius:3px;
  background:
    repeating-linear-gradient(90deg,transparent 0 calc(var(--kp,18px) - 2px),#b9bdc3 calc(var(--kp,18px) - 2px) var(--kp,18px)),
    repeating-linear-gradient(180deg,transparent 0 calc(var(--kh,12px) - 2px),#b9bdc3 calc(var(--kh,12px) - 2px) var(--kh,12px)),
    #1d1f22;}
.lf-pad{position:absolute;left:36%;right:36%;bottom:9%;height:21%;border-radius:4px;
  background:linear-gradient(180deg,#a9adb3,#9a9ea4);box-shadow:inset 0 0 0 1px rgba(0,0,0,.16);}
.lf-screen-bg{position:absolute;background:#0a0a0a;border-radius:3px;
  box-shadow:0 0 140px 24px rgba(190,210,255,.11);}
.lf-bezel{position:absolute;box-sizing:border-box;border-style:solid;border-color:#060606;
  border-radius:14px;box-shadow:0 0 0 2px #9fa3a9,0 0 0 3px #5a5d62;}
.lf-cam{position:absolute;left:50%;width:5px;height:5px;margin:-2.5px 0 0 -2.5px;border-radius:50%;background:#18202c;}
.lf-glare{position:absolute;pointer-events:none;border-radius:3px;
  background:linear-gradient(115deg,rgba(255,255,255,.07) 0%,rgba(255,255,255,0) 38%);}
"""
