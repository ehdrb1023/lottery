class LaptopFrame:
    """CSS로 그린 열린 노트북 + 작은 나무 책상.

    위치와 크기는 intro_scene.js 가 화면 크기에 맞춰 정한다(좌표 config 없음).
    - under_html(): 앱 화면 뒤에 깔리는 층 (바닥 그늘, 책상, 빛 번짐, 본체·키보드, 화면 바탕)
    - over_html():  앱 화면 앞에 얹히는 층 (얇은 검은 베젤, 카메라, 유리 반사)
    """

    def under_html(self):
        return (
            '<div class="lf-ground"></div>'
            '<div class="lf-leg lf-leg-l"></div><div class="lf-leg lf-leg-r"></div>'
            '<div class="lf-desk-top"></div><div class="lf-desk-front"></div>'
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
.lf-ground{position:absolute;left:0;right:0;bottom:0;pointer-events:none;
  background:linear-gradient(180deg,rgba(6,7,9,0),rgba(6,7,9,.78) 55%,rgba(5,6,8,.96));}
.lf-leg{position:absolute;background:linear-gradient(90deg,#15110d,#2a2119 50%,#15110d);border-radius:1px;}
.lf-desk-top{position:absolute;
  clip-path:polygon(7% 0,93% 0,100% 100%,0 100%);
  background:linear-gradient(180deg,#6b5238 0%,#4d3a27 100%);}
.lf-desk-front{position:absolute;border-radius:1px 1px 3px 3px;
  background:linear-gradient(180deg,#3a2a1b,#241810);
  box-shadow:0 1px 0 rgba(255,225,180,.18) inset;}
.lf-glow{position:absolute;pointer-events:none;mix-blend-mode:screen;
  background:radial-gradient(ellipse at 50% 0%,rgba(205,222,255,.30),rgba(205,222,255,.08) 48%,transparent 72%);}
.lf-shadow{position:absolute;pointer-events:none;
  background:radial-gradient(ellipse at 50% 40%,rgba(0,0,0,.5),transparent 70%);}
.lf-deck{position:absolute;
  clip-path:polygon(5.5% 0,94.5% 0,100% 100%,0 100%);
  background:linear-gradient(180deg,#d2d5da 0%,#b4b8be 50%,#92969c 100%);}
.lf-keys{position:absolute;left:9%;right:9%;top:13%;height:50%;border-radius:2px;
  background:
    repeating-linear-gradient(90deg,transparent 0 calc(var(--kp,18px) - 1.5px),#b9bdc3 calc(var(--kp,18px) - 1.5px) var(--kp,18px)),
    repeating-linear-gradient(180deg,transparent 0 calc(var(--kh,12px) - 1.5px),#b9bdc3 calc(var(--kh,12px) - 1.5px) var(--kh,12px)),
    #25272b;}
.lf-pad{position:absolute;left:36%;right:36%;bottom:9%;height:21%;border-radius:3px;
  background:linear-gradient(180deg,#a9adb3,#9a9ea4);box-shadow:inset 0 0 0 1px rgba(0,0,0,.16);}
.lf-screen-bg{position:absolute;background:#0a0a0a;border-radius:2px;
  box-shadow:0 0 90px 14px rgba(190,210,255,.13);}
.lf-bezel{position:absolute;box-sizing:border-box;border-style:solid;border-color:#060606;
  border-radius:6px;box-shadow:0 0 0 1px #9fa3a9,0 0 0 2px #5a5d62;}
.lf-cam{position:absolute;left:50%;width:3px;height:3px;margin:-1.5px 0 0 -1.5px;border-radius:50%;background:#18202c;}
.lf-glare{position:absolute;pointer-events:none;border-radius:2px;
  background:linear-gradient(115deg,rgba(255,255,255,.07) 0%,rgba(255,255,255,0) 38%);}
"""
