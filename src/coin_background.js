/*
 * CoinBackground — 화면 고정 canvas 위에 금화가 떠다니는 배경 효과.
 * Matter.js(중력 0)로 충돌·반사를 처리하고, 금화 모양은 canvas로 직접 그린다.
 * 앞면(볼록한 방사형 그라데이션 + 톱니 테두리 + "$" 각인), 옆면(두께·결), 바닥 그림자,
 * 코인마다 랜덤 타이밍으로 스치는 빛줄기를 그린다.
 * __OPTS__ 는 coin_background.py 가 JSON 설정으로 치환한다.
 * 인트로가 있으면(window.__introDone === false) 끝난 뒤에 하나씩 나타난다.
 */
(function (OPTS) {
  'use strict';
  if (window.__coinBackground) return;
  window.__coinBackground = true;

  var TAU = Math.PI * 2;
  var STEP = 1000 / 60;
  var FONT = '"Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif';

  function loadMatter(cb) {
    if (window.Matter) return cb();
    var s = document.createElement('script');
    s.src = OPTS.matterUrl;
    s.async = true;
    s.onload = cb;
    s.onerror = function () { window.__coinBackground = false; };
    document.head.appendChild(s);
  }

  function fontsReady() {
    if (!document.fonts || !document.fonts.load) return Promise.resolve();
    var p = document.fonts.load('700 48px Pretendard', '$');
    var t = new Promise(function (r) { setTimeout(r, 2500); });
    return Promise.race([p, t]).catch(function () {});
  }

  function whenIntroDone(cb) {
    if (window.__introDone === false) {
      window.addEventListener('intro:done', function () { cb(); }, { once: true });
    } else { cb(); }
  }

  function rand(a, b) { return a + Math.random() * (b - a); }
  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }

  function start() {
    var M = window.Matter;
    var Engine = M.Engine, Bodies = M.Bodies, Body = M.Body, Composite = M.Composite;

    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var isMobile = window.innerWidth < OPTS.mobileBreakpoint;
    var W = 0, H = 0, dpr = 1;

    // ---------- canvas ----------
    var canvas = document.createElement('canvas');
    canvas.id = 'coin-bg';
    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.cssText =
      'position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:0;pointer-events:none;opacity:' +
      (isMobile ? OPTS.mobileOpacity : OPTS.desktopOpacity);
    document.body.appendChild(canvas);
    var ctx = canvas.getContext('2d');

    // ---------- physics ----------
    var engine = Engine.create();
    engine.gravity.x = 0;
    engine.gravity.y = 0;
    engine.gravity.scale = 0;
    var walls = [];

    function buildWalls() {
      if (walls.length) Composite.remove(engine.world, walls);
      var t = 200, o = { isStatic: true, restitution: 1, friction: 0, frictionStatic: 0 };
      walls = [
        Bodies.rectangle(W / 2, -t / 2, W + 2 * t, t, o),
        Bodies.rectangle(W / 2, H + t / 2, W + 2 * t, t, o),
        Bodies.rectangle(-t / 2, H / 2, t, H + 2 * t, o),
        Bodies.rectangle(W + t / 2, H / 2, t, H + 2 * t, o)
      ];
      Composite.add(engine.world, walls);
    }

    // ---------- coin sprites (앞면 / 옆면) ----------
    function makeFace(r) {
      var S = Math.ceil(2 * r * dpr);
      var c = document.createElement('canvas');
      c.width = c.height = S;
      var g = c.getContext('2d');
      var m = S / 2, R = S / 2 * 0.98, i, a;

      // 바탕: 살짝 볼록한 느낌의 방사형 그라데이션
      var body = g.createRadialGradient(m - R * 0.32, m - R * 0.38, R * 0.06, m, m, R);
      body.addColorStop(0, '#F7E6AE');
      body.addColorStop(0.35, '#E0BC62');
      body.addColorStop(0.75, '#B58B34');
      body.addColorStop(1, '#7A5819');
      g.fillStyle = body;
      g.beginPath(); g.arc(m, m, R, 0, TAU); g.fill();

      // 테두리 톱니
      var teeth = 56;
      g.lineWidth = Math.max(1, R * 0.034);
      for (i = 0; i < teeth; i++) {
        a = i / teeth * TAU;
        g.strokeStyle = (i % 2) ? 'rgba(78,52,10,0.72)' : 'rgba(255,238,175,0.4)';
        g.beginPath();
        g.moveTo(m + Math.cos(a) * R * 0.905, m + Math.sin(a) * R * 0.905);
        g.lineTo(m + Math.cos(a) * R * 0.985, m + Math.sin(a) * R * 0.985);
        g.stroke();
      }
      g.lineWidth = R * 0.05;
      g.strokeStyle = '#6E4F14';
      g.beginPath(); g.arc(m, m, R - g.lineWidth / 2, 0, TAU); g.stroke();

      // 안쪽 턱(경사)
      g.lineWidth = R * 0.045;
      g.strokeStyle = 'rgba(120,88,26,0.7)';
      g.beginPath(); g.arc(m, m, R * 0.865, 0, TAU); g.stroke();
      g.lineWidth = R * 0.03;
      g.strokeStyle = 'rgba(255,240,185,0.5)';
      g.beginPath(); g.arc(m, m, R * 0.835, 0, TAU); g.stroke();

      // 앞면: 가운데가 볼록하게 보이도록
      var face = g.createRadialGradient(m - R * 0.2, m - R * 0.25, R * 0.04, m, m, R * 0.82);
      face.addColorStop(0, '#F3DE98');
      face.addColorStop(0.55, '#D2AB4F');
      face.addColorStop(1, '#B58C36');
      g.fillStyle = face;
      g.beginPath(); g.arc(m, m, R * 0.815, 0, TAU); g.fill();

      // 음각 "$"
      g.font = '800 ' + Math.round(R * 1.18) + 'px ' + FONT;
      g.textAlign = 'center';
      g.textBaseline = 'middle';
      var off = Math.max(1, R * 0.028), ty = m + R * 0.05;
      g.fillStyle = 'rgba(255,242,195,0.62)';
      g.fillText('$', m + off, ty + off);
      g.fillStyle = 'rgba(70,46,6,0.78)';
      g.fillText('$', m - off, ty - off);
      g.fillStyle = '#B28A33';
      g.fillText('$', m, ty);
      return c;
    }

    function makeEdge(r) {
      var h = Math.ceil(2 * r * dpr), w = 8;
      var c = document.createElement('canvas');
      c.width = w; c.height = h;
      var g = c.getContext('2d');
      var grad = g.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, '#6A4C14');
      grad.addColorStop(0.3, '#E2C068');
      grad.addColorStop(0.55, '#BE9639');
      grad.addColorStop(1, '#5E4311');
      g.fillStyle = grad; g.fillRect(0, 0, w, h);
      // 옆면 결(톱니)은 위아래로 갈수록 촘촘하게 보인다
      g.fillStyle = 'rgba(70,46,8,0.45)';
      for (var i = -11; i <= 11; i++) {
        var y = h / 2 + Math.sin(i / 12 * Math.PI / 2) * h / 2 * 0.98;
        g.fillRect(0, y, w, Math.max(1, dpr * 0.8));
      }
      return c;
    }

    // ---------- coins ----------
    var coins = [];
    var time = 0;

    function placeCoins() {
      var count = isMobile ? OPTS.mobileCount : OPTS.desktopCount;
      var range = isMobile ? OPTS.mobileRadius : OPTS.desktopRadius;
      var wide = !isMobile && W >= OPTS.columnWidth + 280;
      var sideW = wide ? (W - OPTS.columnWidth) / 2 : 0;
      var pad = 14;
      var rMax = range[1], rMin = range[0];
      if (wide) {
        rMax = Math.min(rMax, (sideW - pad * 2) / 2);
        rMin = Math.min(rMin, rMax * 0.78);
      }
      var placed = [];
      for (var i = 0; i < count; i++) {
        var r = rand(rMin, rMax), ok = null;
        for (var a = 0; a < 360 && !ok; a++) {
          var gap = a < 120 ? 20 : (a < 240 ? 12 : 5);
          var x0, x1;
          if (wide) {
            if (i % 2 === 0) { x0 = pad + r; x1 = sideW - pad - r; }
            else { x0 = W - sideW + pad + r; x1 = W - pad - r; }
          } else { x0 = r + pad; x1 = W - r - pad; }
          if (x1 < x0) x0 = x1 = (x0 + x1) / 2;
          var x = rand(x0, x1), y = rand(r + 10, H - r - 10), clear = true;
          for (var j = 0; j < placed.length; j++) {
            var dx = x - placed[j].x, dy = y - placed[j].y;
            if (Math.sqrt(dx * dx + dy * dy) < r + placed[j].r + gap) { clear = false; break; }
          }
          if (clear) ok = { x: x, y: y, r: r };
        }
        if (ok) placed.push(ok);
      }
      // 나타나는 순서를 섞는다
      placed.sort(function () { return Math.random() - 0.5; });
      placed.forEach(function (p, idx) {
        var b = Bodies.circle(p.x, p.y, p.r, {
          restitution: 0.95, friction: 0, frictionStatic: 0, frictionAir: 0.015,
          density: 0.001, slop: 0.02
        });
        Body.setInertia(b, Infinity);
        var base = (reduce ? 0.04 : rand(0.5, 0.9)) * (Math.random() < 0.5 ? -1 : 1);
        coins.push({
          body: b, r: p.r, home: { x: p.x, y: p.y },
          face: makeFace(p.r), edge: makeEdge(p.r),
          phase: rand(0, TAU), phase2: rand(0, TAU), period: rand(7, 11),
          spin: rand(0, TAU), baseSpin: base, spinVel: base,
          born: 0.3 + idx * (reduce ? 0.05 : 0.32) + rand(0, 0.2),
          shineAt: rand(1.5, 6), shineDur: rand(0.7, 1.1)
        });
        Composite.add(engine.world, b);
      });
    }

    // ---------- sizing ----------
    function resize() {
      var nw = window.innerWidth, nh = window.innerHeight;
      var nd = Math.min(window.devicePixelRatio || 1, 2);
      if (nw === W && nh === H && nd === dpr) return;
      var sx = W ? nw / W : 1, sy = H ? nh / H : 1;
      W = nw; H = nh; dpr = nd;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      buildWalls();
      coins.forEach(function (c) {
        Body.setPosition(c.body, { x: c.body.position.x * sx, y: c.body.position.y * sy });
        c.home.x *= sx; c.home.y *= sy;
      });
    }

    // ---------- simulation ----------
    var K_SPRING = 7e-5;           // 제자리로 돌아오려는 아주 약한 복원력 (px/step²)
    var BOB = reduce ? 0 : 2.6e-3; // 위아래 부유 가속도 (px/step²)

    function stepPhysics() {
      time += STEP / 1000;
      var f = 1 / (STEP * STEP);
      for (var i = 0; i < coins.length; i++) {
        var c = coins[i], b = c.body;
        var w = TAU / (c.period * 60);
        var ax = K_SPRING * (c.home.x - b.position.x) + BOB * 0.35 * Math.sin(time * w * 60 + c.phase2);
        var ay = K_SPRING * (c.home.y - b.position.y) + BOB * Math.sin(time * w * 60 + c.phase);
        Body.applyForce(b, b.position, { x: ax * b.mass * f, y: ay * b.mass * f });
      }
      Engine.update(engine, STEP);
    }

    // ---------- drawing ----------
    function drawShadow(p, r, alpha) {
      ctx.save();
      ctx.globalAlpha = alpha * 0.9;
      ctx.translate(p.x, p.y + r * 1.22);
      ctx.scale(1, 0.2);
      var g = ctx.createRadialGradient(0, 0, 0, 0, 0, r * 0.95);
      g.addColorStop(0, 'rgba(0,0,0,0.34)');
      g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g;
      ctx.fillRect(-r, -r, 2 * r, 2 * r);
      ctx.restore();
    }

    function drawCoin(c, dt) {
      var p = c.body.position, r = c.r;
      var alpha = clamp01((time - c.born) / 1.3);
      if (alpha <= 0) return;
      var pop = 0.86 + 0.14 * (1 - Math.pow(1 - alpha, 3));

      var k = 1 - Math.exp(-dt / 1.6);
      c.spinVel += (c.baseSpin - c.spinVel) * k;
      c.spin += c.spinVel * dt;
      var cs = Math.cos(c.spin), sn = Math.sin(c.spin);
      var sx = Math.max(Math.abs(cs), 0.05);
      var th = r * 0.17;
      var e = th * Math.abs(sn);                 // 옆면이 보이는 폭
      var front = (cs >= 0 ? 1 : -1) * (sn >= 0 ? 1 : -1) * e / 2;

      drawShadow(p, r * pop, alpha);

      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.translate(p.x, p.y);
      ctx.scale(pop, pop);

      if (e > 0.4) {
        // 뒷면 타원 + 옆면 띠
        ctx.fillStyle = '#7D5C1A';
        ctx.beginPath();
        ctx.ellipse(-front, 0, r * sx * 0.98, r * 0.98, 0, 0, TAU);
        ctx.fill();
        ctx.drawImage(c.edge, -e / 2, -r * 0.98, e, 2 * r * 0.98);
      }

      ctx.translate(front, 0);
      ctx.save();
      ctx.scale(sx, 1);
      ctx.drawImage(c.face, -r, -r, 2 * r, 2 * r);

      // 옆으로 돌수록 앞면이 어두워진다
      var shade = (1 - sx) * 0.42;
      if (shade > 0.02) {
        ctx.fillStyle = 'rgba(30,20,4,' + shade.toFixed(3) + ')';
        ctx.beginPath(); ctx.arc(0, 0, r * 0.98, 0, TAU); ctx.fill();
      }

      // 빛줄기: 코인마다 타이밍이 다르다
      var q = (time - c.shineAt) / c.shineDur;
      if (q > 1) { c.shineAt = time + rand(3, 7.5); c.shineDur = rand(0.7, 1.1); q = -1; }
      if (q >= 0 && q <= 1) {
        ctx.beginPath(); ctx.arc(0, 0, r * 0.97, 0, TAU); ctx.clip();
        ctx.rotate(-0.62);
        var x = -1.5 * r + q * 3 * r, bw = r * 0.55;
        var sg = ctx.createLinearGradient(x - bw, 0, x + bw, 0);
        sg.addColorStop(0, 'rgba(255,248,220,0)');
        sg.addColorStop(0.5, 'rgba(255,248,220,0.62)');
        sg.addColorStop(1, 'rgba(255,248,220,0)');
        ctx.fillStyle = sg;
        ctx.fillRect(x - bw, -2 * r, 2 * bw, 4 * r);
      }
      ctx.restore();
      ctx.restore();
    }

    function draw(dt) {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < coins.length; i++) drawCoin(coins[i], dt);
    }

    // ---------- loop ----------
    var raf = 0, last = 0, acc = 0;
    function frame(ts) {
      raf = requestAnimationFrame(frame);
      if (!last) last = ts;
      var dt = Math.min(ts - last, 100);
      last = ts;
      acc += dt;
      var n = 0;
      while (acc >= STEP && n < 4) { stepPhysics(); acc -= STEP; n++; }
      if (acc > STEP) acc = 0;
      draw(dt / 1000);
    }
    function run() { if (!raf) { last = 0; raf = requestAnimationFrame(frame); } }
    function pause() { if (raf) { cancelAnimationFrame(raf); raf = 0; } }
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) pause(); else run();
    });

    var rt = 0;
    window.addEventListener('resize', function () {
      cancelAnimationFrame(rt);
      rt = requestAnimationFrame(resize);
    });

    // ---------- sound (기본 꺼짐) ----------
    var soundOn = false, actx = null, lastPing = 0;
    function ping() {
      if (!soundOn) return;
      var now = performance.now();
      if (now - lastPing < 120) return;
      lastPing = now;
      try {
        actx = actx || new (window.AudioContext || window.webkitAudioContext)();
        if (actx.state === 'suspended') actx.resume();
        var t = actx.currentTime, out = actx.createGain();
        out.gain.setValueAtTime(0.0001, t);
        out.gain.exponentialRampToValueAtTime(0.05, t + 0.005);
        out.gain.exponentialRampToValueAtTime(0.0001, t + 0.32);
        out.connect(actx.destination);
        [1760, 1760 * 2.76].forEach(function (hz, idx) {
          var o = actx.createOscillator(), g = actx.createGain();
          o.type = 'sine'; o.frequency.value = hz * rand(0.97, 1.03);
          g.gain.value = idx ? 0.35 : 1;
          o.connect(g); g.connect(out);
          o.start(t); o.stop(t + 0.34);
        });
      } catch (e) {}
    }

    if (OPTS.soundToggle) {
      var st = document.createElement('style');
      st.textContent =
        '#coin-sound-toggle{position:fixed;right:16px;bottom:16px;z-index:5;min-height:44px;padding:0 18px;' +
        'font:500 16px/1 Pretendard,system-ui,sans-serif;color:#EDE6D8;background:#1c1a17;' +
        'border:1px solid rgba(201,164,76,.55);border-radius:999px;cursor:pointer}' +
        '#coin-sound-toggle[aria-pressed="true"]{color:#1A1A1A;background:#C9A44C;border-color:#C9A44C}' +
        '#coin-sound-toggle:focus-visible{outline:2px solid #C9A44C;outline-offset:3px}' +
        '@media (max-width:700px){#coin-sound-toggle{bottom:auto;top:10px;right:10px;min-height:40px;padding:0 12px;font-size:15px}}';
      document.head.appendChild(st);
      var btn = document.createElement('button');
      btn.id = 'coin-sound-toggle';
      btn.type = 'button';
      btn.setAttribute('aria-pressed', 'false');
      btn.textContent = '금화 소리 꺼짐';
      btn.addEventListener('click', function () {
        soundOn = !soundOn;
        btn.setAttribute('aria-pressed', String(soundOn));
        btn.textContent = soundOn ? '금화 소리 켜짐' : '금화 소리 꺼짐';
        if (soundOn) ping();
      });
      document.body.appendChild(btn);
    }

    // ---------- click / touch ----------
    var SKIP = 'button,a,input,textarea,select,option,label,summary,[role="button"],[role="radio"],' +
      '[role="tab"],[role="link"],[role="slider"],[contenteditable="true"],[data-baseweb="select"]';
    window.addEventListener('pointerdown', function (e) {
      if (reduce) return;
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      var t = e.target;
      if (t && t.closest && t.closest(SKIP)) return;
      var R = OPTS.clickRadius, hit = false;
      for (var i = 0; i < coins.length; i++) {
        var c = coins[i], p = c.body.position;
        var dx = p.x - e.clientX, dy = p.y - e.clientY, d = Math.sqrt(dx * dx + dy * dy);
        if (d > R) continue;
        if (d < 1) { var an = rand(0, TAU); dx = Math.cos(an); dy = Math.sin(an); d = 1; }
        var k = 1 - d / R, v = 4 + 6 * k;
        Body.setVelocity(c.body, {
          x: c.body.velocity.x + (dx / d) * v,
          y: c.body.velocity.y + (dy / d) * v
        });
        c.spinVel += (Math.random() < 0.5 ? -1 : 1) * (10 + 8 * k);
        hit = true;
      }
      if (hit) ping();
    }, { passive: true });

    resize();
    placeCoins();
    run();
  }

  loadMatter(function () {
    fontsReady().then(function () { whenIntroDone(start); });
  });
})(__OPTS__);
