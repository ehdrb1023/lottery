class LottoBall:
    """로또 공 (공식 색상 구간: 1~10 노랑, 11~20 파랑, 21~30 빨강, 31~40 회색, 41~45 초록)."""

    BANDS = ((10, "y"), (20, "b"), (30, "r"), (40, "g"), (45, "n"))

    @classmethod
    def band(cls, number):
        for limit, name in cls.BANDS:
            if number <= limit:
                return name
        return "n"

    @classmethod
    def html(cls, number, bonus=False, delay=None):
        style = f' style="animation-delay:{delay:.2f}s"' if delay is not None else ""
        label = f"보너스 {number}" if bonus else str(number)
        extra = " lb-bonus" if bonus else ""
        return f'<span class="lb lb-{cls.band(number)}{extra}" aria-label="{label}"{style}>{number}</span>'

    @classmethod
    def row(cls, numbers, bonus=None, base_delay=None, step=0.07):
        """공 한 줄. base_delay 를 주면 공이 하나씩 차례로 나타난다."""
        balls = []
        for i, n in enumerate(numbers):
            d = None if base_delay is None else base_delay + i * step
            balls.append(cls.html(int(n), delay=d))
        if bonus is not None:
            d = None if base_delay is None else base_delay + len(numbers) * step
            balls.append('<span class="lb-plus" aria-hidden="true">+</span>')
            balls.append(cls.html(int(bonus), bonus=True, delay=d))
        return f'<div class="lb-row">{"".join(balls)}</div>'

    @staticmethod
    def css():
        return """
.lb-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px;}
.lb{display:inline-flex;align-items:center;justify-content:center;flex:0 0 auto;
  width:46px;height:46px;border-radius:50%;color:#1A1A1A;
  font:700 19px/1 Pretendard,system-ui,sans-serif;font-variant-numeric:tabular-nums;letter-spacing:-.02em;
  box-shadow:inset 0 -3px 5px rgba(0,0,0,.14),inset 0 2px 3px rgba(255,255,255,.28);}
.lb-y{background:#FBC400;} .lb-b{background:#69C8F2;} .lb-r{background:#FF7272;}
.lb-g{background:#AAAAAA;} .lb-n{background:#B0D840;}
.lb-plus{color:#8F8A80;font:500 20px/1 Pretendard,system-ui,sans-serif;padding:0 2px;}
.lb-bonus{opacity:.96;}
.lb-anim .lb,.draw-card .lb{animation:lb-in .32s ease both;}
@keyframes lb-in{from{opacity:0;transform:translateY(8px) scale(.86);}to{opacity:1;transform:none;}}
@media (max-width:480px){
  .lb-row{gap:5px;flex-wrap:nowrap;} .lb{width:35px;height:35px;font-size:15px;} .lb-plus{font-size:16px;padding:0;}
}
@media (prefers-reduced-motion:reduce){.lb-anim .lb,.draw-card .lb{animation:none;}}
"""
