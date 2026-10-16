/*
 * IntroScene — 서울 야경 → 노트북 화면 속으로 들어가는 인트로.
 * 층 순서(아래→위): 야경/테이블/노트북 본체(under) < 실제 앱 화면(.stApp) < 베젤(over) < 스크롤 층.
 * 앱 화면은 노트북 화면 크기로 축소되어 있다가, 진행도 p(0→1)에 따라 실제 크기가 된다.
 *   p 0~0.8  : 노트북 화면을 기준점으로 카메라가 다가간다(야경·테이블·본체는 어두워지며 사라짐)
 *   p 0.78~1 : 화면 높이를 실제 화면 높이까지 펼친다(모바일처럼 비율이 다를 때 자연스럽게 이어짐)
 * __OPTS__ 는 intro_scene.py 가 JSON 설정으로 치환한다.
 */
(function (OPTS) {
  'use strict';
  if (window.__introScene) return;
  window.__introScene = true;

  var KEY = OPTS.storageKey;
  var ASPECT = 1.6;                  // 노트북 화면 비율(16:10)
  var DURATION = 1.4;                // 클릭 시 자동 재생 시간(초)
  var doc = document.documentElement;

  var params = new URLSearchParams(location.search);
  var mode = params.get('intro');    // replay: 다시 보기 / 0: 건너뛰기
  var seen = false;
  try { seen = localStorage.getItem(KEY) === '1'; } catch (e) {}
  if (mode === '0' || (seen && mode !== 'replay')) { window.__introDone = true; return; }
  window.__introDone = false;

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }
  function smooth(v) { v = clamp01(v); return v * v * (3 - 2 * v); }

  function loadScript(src) {
    return new Promise(function (res, rej) {
      var s = document.createElement('script');
      s.src = src; s.async = true; s.onload = res; s.onerror = rej;
      document.head.appendChild(s);
    });
  }

  function finishNow() {          // 라이브러리를 못 불러오는 등 문제가 생기면 인트로 없이 진행
    try { localStorage.setItem(KEY, '1'); } catch (e) {}
    window.__introDone = true;
    window.dispatchEvent(new Event('intro:done'));
  }

  var gsapReady = window.gsap && window.ScrollTrigger ? Promise.resolve() :
    loadScript(OPTS.gsapUrl).then(function () { return loadScript(OPTS.scrollTriggerUrl); });
  gsapReady.then(init).catch(function () { finishNow(); });

  function init() {
    var gsap = window.gsap, ScrollTrigger = window.ScrollTrigger;
    gsap.registerPlugin(ScrollTrigger);

    var app = document.querySelector('.stApp');
    if (!app) { finishNow(); return; }

    // ---------- DOM ----------
    var root = el('div', 'intro-root');
    root.innerHTML =
      '\x3cdiv id="intro-bg">\x3cdiv class="is-photo">\x3c/div>\x3cdiv class="is-vig">\x3c/div>\x3c/div>' +
      '\x3cdiv id="intro-under">' + OPTS.underHtml + '\x3c/div>' +
      '\x3cdiv class="is-loader" role="status" aria-label="불러오는 중">\x3c/div>';
    var over = el('div', 'intro-over'); over.innerHTML = OPTS.overHtml;

    var hero = el('div', 'intro-hero');
    var title = document.createElement('h1'); title.className = 'is-title';
    OPTS.title.split('\n').forEach(function (line, i) {
      if (i) title.appendChild(document.createElement('br'));
      title.appendChild(document.createTextNode(line));
    });
    var sub = document.createElement('p'); sub.className = 'is-sub'; sub.textContent = OPTS.sub;
    var cta = document.createElement('button'); cta.type = 'button'; cta.className = 'is-cta'; cta.textContent = OPTS.cta;
    hero.appendChild(title); hero.appendChild(sub); hero.appendChild(cta);

    var ui = el('div', 'intro-ui');
    ui.innerHTML =
      '\x3cp class="is-hint">\x3c/p>' +
      '\x3csvg class="is-arrow" viewBox="0 0 24 24" fill="none" stroke="#F1EBDD" stroke-width="1.8" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">\x3cpath d="M5 9l7 7 7-7"/>\x3c/svg>';
    ui.querySelector('.is-hint').textContent = OPTS.hint;
    var scroller = el('div', 'intro-scroller');
    scroller.setAttribute('tabindex', '0');
    scroller.setAttribute('role', 'button');
    scroller.setAttribute('aria-label', OPTS.hint);
    var spacer = el('div', 'intro-spacer'); scroller.appendChild(spacer);
    var skip = el('button', 'intro-skip'); skip.type = 'button'; skip.textContent = '건너뛰기';

    var nodes = [root, over, hero, ui, scroller, skip];
    nodes.forEach(function (n) { document.body.appendChild(n); });
    doc.classList.add('intro-on');

    var under = root.querySelector('#intro-under');
    var bg = root.querySelector('#intro-bg');
    var photo = root.querySelector('.is-photo');
    function q(sel) { return root.querySelector(sel) || over.querySelector(sel); }
    var E = {
      ground: q('.lf-ground'), legL: q('.lf-leg-l'), legR: q('.lf-leg-r'), deskTop: q('.lf-desk-top'),
      deskFront: q('.lf-desk-front'), glow: q('.lf-glow'), shadow: q('.lf-shadow'), deck: q('.lf-deck'),
      screenBg: q('.lf-screen-bg'), bezel: q('.lf-bezel'), cam: q('.lf-cam'), glare: q('.lf-glare')
    };

    function px(node, o) { for (var k in o) node.style[k] = o[k] + 'px'; }

    // ---------- 사진 로딩 ----------
    var ready = false;
    function markReady() {
      if (ready) return; ready = true;
      root.classList.add('is-ready');
    }
    var img = new Image();
    img.onload = function () {
      photo.style.backgroundImage = 'url("' + OPTS.imageUrl + '")';
      photo.style.backgroundPosition = '62% 42%';
      (img.decode ? img.decode().catch(function () {}) : Promise.resolve()).then(markReady);
    };
    img.onerror = markReady;      // 사진이 없어도 어두운 배경 + 노트북으로 진행
    img.src = OPTS.imageUrl;
    setTimeout(markReady, 6000);

    // ---------- 배치 ----------
    var G = {};
    function layout() {
      var vw = window.innerWidth, vh = window.innerHeight;
      var mobile = vw < OPTS.mobileBreakpoint;
      var Lw = mobile ? vw * 0.56 : Math.max(240, Math.min(vw * 0.2, 340));
      var bz = Math.max(5, Lw * 0.016);
      var sw = Lw - 2 * bz, sh = sw / ASPECT;
      var lh = sh + bz * 1.1 + bz * 1.6, deckH = Lw * 0.15;
      var lx = (vw - Lw) / 2;
      var ly = vh * (mobile ? 0.64 : 0.66) - (lh + deckH) / 2;
      var sx = lx + bz, sy = ly + bz * 1.1;
      G = {
        vw: vw, vh: vh, mobile: mobile, Lw: Lw, lh: lh, lx: lx, ly: ly, bz: bz,
        sx: sx, sy: sy, sw: sw, sh: sh, cx: sx + sw / 2, cy: sy + sh / 2,
        k: vw / sw, Hv: vw / ASPECT, deckH: deckH
      };

      var deckTop = ly + lh - 1, deckW = Lw * 1.1;
      var deskW = Lw * 2.3, deskL = (vw - deskW) / 2;
      var topY = deckTop + deckH * 0.3, frontY = deckTop + deckH * 0.93, frontH = Math.max(7, Lw * 0.03);
      var legW = Math.max(3, Lw * 0.014), legTop = frontY + frontH, legH = Math.max(24, vh * 0.12);
      px(E.ground, { height: vh * 0.3 });
      px(E.deskTop, { left: deskL, top: topY, width: deskW, height: frontY - topY });
      px(E.deskFront, { left: deskL, top: frontY, width: deskW, height: frontH });
      px(E.legL, { left: deskL + deskW * 0.06, top: legTop, width: legW, height: legH });
      px(E.legR, { left: deskL + deskW * 0.94 - legW, top: legTop, width: legW, height: legH });
      px(E.glow, { left: lx - Lw * 0.1, top: ly + lh * 0.7, width: Lw * 1.2, height: Lw * 0.5 });
      px(E.shadow, { left: lx - Lw * 0.15, top: deckTop + deckH * 0.7, width: Lw * 1.3, height: deckH * 0.9 });
      px(E.deck, { left: (vw - deckW) / 2, top: deckTop, width: deckW, height: deckH });
      E.deck.style.setProperty('--kp', Math.max(6, Lw * 0.0235) + 'px');
      E.deck.style.setProperty('--kh', Math.max(4, deckH * 0.098) + 'px');
      px(E.screenBg, { left: sx, top: sy, width: sw, height: sh });
      px(E.bezel, { left: lx, top: ly, width: Lw, height: lh });
      E.bezel.style.borderWidth = [bz * 1.1, bz, bz * 1.6, bz].map(function (n) { return n + 'px'; }).join(' ');
      E.bezel.style.borderRadius = Math.max(5, Lw * 0.02) + 'px';
      E.cam.style.top = (bz * 0.55) + 'px';
      px(E.glare, { left: sx, top: sy, width: sw, height: sh });

      var origin = G.cx + 'px ' + G.cy + 'px';
      under.style.transformOrigin = origin;
      bg.style.transformOrigin = origin;
      over.style.transformOrigin = origin;
      scroller.style.setProperty('--x', '0');
      spacer.style.height = (G.vh * (mobile ? 2.2 : 3.2)) + 'px';
    }

    // ---------- 진행도 → 화면 ----------
    var P = 0;
    function setApp(styleObj) {
      for (var k in styleObj) app.style.setProperty(k, styleObj[k], 'important');
    }
    function render(p) {
      P = p;
      var zp = clamp01(p / 0.8);
      var S = Math.pow(G.k, zp);
      var tx = (G.vw / 2 - G.cx) * zp, ty = (G.vh / 2 - G.cy) * zp;
      var hp = smooth((p - 0.78) / 0.22);
      var Hcur = G.Hv + (G.vh - G.Hv) * hp;
      var a = (G.sw * S) / G.vw;
      var ax = G.cx + tx - G.vw * a / 2, ay = G.cy + ty - Hcur * a / 2;

      var tf = 'translate(' + tx + 'px,' + ty + 'px) scale(' + S + ')';
      under.style.transform = tf;
      over.style.transform = tf;
      bg.style.transform = 'scale(' + Math.pow(S, 0.3) + ')';   // 배경 사진은 천천히 다가온다
      under.style.opacity = ready ? String(1 - smooth((zp - 0.3) / 0.6)) : '';
      bg.style.opacity = ready ? String(1 - smooth((zp - 0.4) / 0.55)) : '';
      hero.style.opacity = ready ? String(1 - clamp01(p / 0.1)) : '';
      hero.style.transform = 'translateY(' + (-p * 80) + 'px)';
      cta.style.pointerEvents = p > 0.02 ? 'none' : 'auto';
      over.style.opacity = String(1 - smooth((zp - 0.62) / 0.35));
      ui.style.opacity = ready ? String(1 - clamp01(p / 0.1)) : '';
      skip.style.opacity = String(1 - smooth((p - 0.7) / 0.3));

      setApp({
        width: G.vw + 'px', height: Hcur + 'px',
        transform: 'translate(' + ax + 'px,' + ay + 'px) scale(' + a + ')',
        'border-radius': (3 * (1 - zp)) + 'px'
      });
      if (p >= 0.999) done();
    }

    // ---------- 종료 ----------
    var finished = false;
    function cleanup() {
      ['width', 'height', 'transform', 'border-radius'].forEach(function (k) { app.style.removeProperty(k); });
      doc.classList.remove('intro-on');
      nodes.forEach(function (n) { if (n.parentNode) n.parentNode.removeChild(n); });
    }
    function done() {
      if (finished) return; finished = true;
      try { localStorage.setItem(KEY, '1'); } catch (e) {}
      if (st) st.kill();
      cleanup();
      window.__introDone = true;
      window.dispatchEvent(new Event('intro:done'));
    }
    function fadeOut() {       // 건너뛰기 / 움직임 줄이기: 확대 없이 페이드로만 전환
      if (finished) return; finished = true;
      try { localStorage.setItem(KEY, '1'); } catch (e) {}
      if (st) st.kill();
      ['width', 'height', 'transform', 'border-radius'].forEach(function (k) { app.style.removeProperty(k); });
      doc.classList.remove('intro-on');
      scroller.style.pointerEvents = 'none';
      gsap.to([root, over, hero, ui, skip], {
        opacity: 0, duration: 0.45, ease: 'power1.out',
        onComplete: function () {
          nodes.forEach(function (n) { if (n.parentNode) n.parentNode.removeChild(n); });
          window.__introDone = true;
          window.dispatchEvent(new Event('intro:done'));
        }
      });
    }

    // ---------- 스크롤 / 클릭 ----------
    var st = null, tween = null;
    layout();
    var proxy = { p: 0 };
    render(0);

    if (!reduce) {
      var tl = gsap.timeline({
        scrollTrigger: {
          trigger: spacer, scroller: scroller, start: 'top top', end: 'bottom bottom', scrub: 0.3
        }
      });
      tl.to(proxy, { p: 1, ease: 'power2.inOut', duration: 1, onUpdate: function () { render(proxy.p); } });
      st = tl.scrollTrigger;
    } else {
      // 움직임 줄이기: 확대 없이 노트북 화면 그대로 두었다가 입력이 있으면 페이드로 전환
      ['wheel', 'touchmove'].forEach(function (ev) {
        scroller.addEventListener(ev, function () { if (ready) fadeOut(); }, { passive: true });
      });
    }

    function enter() {
      if (finished || !ready) return;
      if (reduce) { fadeOut(); return; }
      if (tween) return;
      var max = scroller.scrollHeight - scroller.clientHeight;
      tween = gsap.to(scroller, { scrollTop: max, duration: DURATION, ease: 'none', onComplete: function () { tween = null; } });
    }
    scroller.addEventListener('click', enter);
    cta.addEventListener('click', function (e) { e.stopPropagation(); enter(); });
    scroller.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown' || e.key === 'PageDown') {
        e.preventDefault(); enter();
      }
    });
    skip.addEventListener('click', function (e) { e.stopPropagation(); fadeOut(); });

    var rt = 0;
    window.addEventListener('resize', function () {
      if (finished) return;
      cancelAnimationFrame(rt);
      rt = requestAnimationFrame(function () { layout(); render(P); if (st) st.refresh(); });
    });

    setTimeout(function () { try { scroller.focus({ preventScroll: true }); } catch (e) {} }, 300);
  }

  function el(tag, id) { var n = document.createElement(tag); n.id = id; return n; }
})(__OPTS__);
