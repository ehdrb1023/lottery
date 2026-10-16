/*
 * IntroScene — 서울 야경 → 노트북 화면 속으로 들어가는 인트로.
 * 층 순서(아래→위): 야경/테이블/노트북 본체(under) < 실제 앱 화면(.stApp) < 베젤(over) < 스크롤 층.
 * 앱 화면은 노트북 화면 크기로 축소되어 있다가, 진행도 p(0→1)에 따라 실제 크기가 된다.
 *   p 0~0.8  : 노트북 화면을 기준점으로 카메라가 다가간다(야경·테이블·본체는 어두워지며 사라짐)
 *   p 0.78~1 : 화면 높이를 실제 화면 높이까지 펼친다(모바일처럼 비율이 다를 때 자연스럽게 이어짐)
 * 따로 지나가는 페이지가 아니라 "한 페이지의 맨 위 화면"이다.
 *   아래로 내리면 사이트가 되고, 사이트 맨 위에서 다시 올리면 야경 화면으로 돌아온다(되돌아갈 때는 자동 재생).
 * __OPTS__ 는 intro_scene.py 가 JSON 설정으로 치환한다.
 */
(function (OPTS) {
  'use strict';
  if (window.__introScene) return;
  window.__introScene = true;

  var ASPECT = 1.6;                  // 노트북 화면 비율(16:10)
  var DURATION = 1.4;                // 클릭 시 자동 재생 시간(초)
  var doc = document.documentElement;

  var params = new URLSearchParams(location.search);
  if (params.get('intro') === '0') { window.__introDone = true; return; }   // ?intro=0 : 야경 화면 없이 사이트만
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
      if (inSite) return;           // 사이트가 펼쳐진 동안에는 앱 화면을 건드리지 않는다
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
      if (p >= 0.999 && !inSite && performance.now() > lockUntil) enterSite();
    }

    // ---------- 야경 화면 ↔ 사이트 전환 ----------
    var inSite = false, lockUntil = 0, siteLock = 0, tween = null, st = null, tl = null;
    var proxy = { p: 0 };
    var APP_PROPS = ['width', 'height', 'transform', 'border-radius'];
    function maxScroll() { return Math.max(1, scroller.scrollHeight - scroller.clientHeight); }
    function clearApp() { APP_PROPS.forEach(function (k) { app.style.removeProperty(k); }); }
    function stMain() { return document.querySelector('[data-testid="stMain"]'); }

    function enterSite() {            // 사이트가 실제 크기가 됨 → 야경 화면은 숨김(지우지 않고 보관)
      if (inSite) return;
      inSite = true; siteLock = performance.now() + 700;
      if (tween) { tween.kill(); tween = null; }
      clearApp();
      doc.classList.remove('intro-on');
      nodes.forEach(function (n) { n.style.display = 'none'; });
      if (!window.__introDone) {
        window.__introDone = true;
        window.dispatchEvent(new Event('intro:done'));
      }
    }

    function fadeToSite() {           // 건너뛰기 / 움직임 줄이기: 확대 없이 페이드로만 전환
      if (inSite) return;
      if (tween) { tween.kill(); tween = null; }
      clearApp();
      doc.classList.remove('intro-on');
      scroller.style.pointerEvents = 'none';
      gsap.to([root, over, hero, ui, skip], {
        opacity: 0, duration: 0.45, ease: 'power1.out',
        onComplete: function () {
          gsap.set([root, over, hero, ui, skip], { clearProps: 'opacity' });
          scroller.style.pointerEvents = '';
          inSite = false; enterSite();
        }
      });
    }

    function reopenIntro() {          // 사이트 맨 위에서 다시 올림 → 야경 화면으로 돌아감
      if (!inSite) return;
      inSite = false;
      var m = stMain(); if (m) m.scrollTop = 0;
      window.scrollTo(0, 0);
      nodes.forEach(function (n) { n.style.display = ''; });
      doc.classList.add('intro-on');
      layout();
      if (reduce) {
        render(0);
        gsap.fromTo([root, over, hero, ui, skip], { opacity: 0 }, { opacity: 1, duration: 0.45, clearProps: 'opacity' });
        return;
      }
      var f = 0.776;                  // 진행도 약 0.9 (사이트가 막 펼쳐지는 지점)에서 시작해 거꾸로 재생
      lockUntil = performance.now() + 600;
      tl.progress(f);
      scroller.scrollTop = f * maxScroll();
      render(proxy.p);
      tween = gsap.to(scroller, { scrollTop: 0, duration: 1.1, ease: 'none', onComplete: function () { tween = null; } });
    }

    // ---------- 스크롤 / 클릭 ----------
    layout();
    render(0);

    if (!reduce) {
      tl = gsap.timeline({
        scrollTrigger: {
          trigger: spacer, scroller: scroller, start: 'top top', end: 'bottom bottom', scrub: 0.3
        }
      });
      tl.to(proxy, { p: 1, ease: 'power2.inOut', duration: 1, onUpdate: function () { render(proxy.p); } });
      st = tl.scrollTrigger;
    } else {
      ['wheel', 'touchmove'].forEach(function (ev) {
        scroller.addEventListener(ev, function () { if (ready) fadeToSite(); }, { passive: true });
      });
    }

    function enter() {
      if (inSite || !ready) return;
      if (reduce) { fadeToSite(); return; }
      if (tween) return;
      tween = gsap.to(scroller, { scrollTop: maxScroll(), duration: DURATION, ease: 'none', onComplete: function () { tween = null; } });
    }
    scroller.addEventListener('click', enter);
    cta.addEventListener('click', function (e) { e.stopPropagation(); enter(); });
    scroller.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown' || e.key === 'PageDown') {
        e.preventDefault(); enter();
      }
    });
    skip.addEventListener('click', function (e) { e.stopPropagation(); fadeToSite(); });

    // 스크롤을 중간에서 멈추면 가던 방향 쪽으로 마저 이동 (어중간한 상태로 남지 않게)
    var lastTop = 0, dir = 1, snapT = 0, touching = false;
    function snap() {
      if (inSite || tween || touching || reduce) return;
      var max = maxScroll(), f = scroller.scrollTop / max;
      if (f < 0.015 || f > 0.985) return;
      var target = dir > 0 ? max : 0;
      tween = gsap.to(scroller, {
        scrollTop: target, duration: 0.35 + 0.9 * Math.abs(target / max - f), ease: 'power2.out',
        onComplete: function () { tween = null; }
      });
    }
    scroller.addEventListener('scroll', function () {
      var t = scroller.scrollTop;
      if (t !== lastTop) { dir = t > lastTop ? 1 : -1; lastTop = t; }
      clearTimeout(snapT);
      if (!tween && !touching) snapT = setTimeout(snap, 170);
    }, { passive: true });
    scroller.addEventListener('wheel', function () { if (tween) { tween.kill(); tween = null; } }, { passive: true });
    scroller.addEventListener('touchstart', function () { touching = true; if (tween) { tween.kill(); tween = null; } }, { passive: true });
    scroller.addEventListener('touchend', function () { touching = false; clearTimeout(snapT); snapT = setTimeout(snap, 120); }, { passive: true });

    // 사이트 맨 위에서 위로 올리려는 동작 → 야경 화면으로
    function siteAtTop() { var m = stMain(); return (m ? m.scrollTop : window.scrollY) <= 1; }
    // 위로 빠르게 올리다 관성으로 맨 위에 닿은 경우에는 되돌아가지 않고, 맨 위에 잠시 머문 뒤의 새 동작만 인정한다
    var awayAt = 0;
    document.addEventListener('scroll', function () { if (inSite && !siteAtTop()) awayAt = performance.now(); }, true);
    function canReopen(target) {
      if (!inSite || performance.now() < siteLock || performance.now() - awayAt < 450 || !siteAtTop()) return false;
      return !(target && target.closest && target.closest('[data-testid="stDataFrame"],textarea,input,[role="listbox"]'));
    }
    var lastWheelAt = 0;
    window.addEventListener('wheel', function (e) {
      var now = performance.now(), fresh = now - lastWheelAt > 220;   // 휠이 잠시 멈췄다가 새로 시작된 동작만
      lastWheelAt = now;
      if (e.deltaY < 0 && fresh && canReopen(e.target)) reopenIntro();
    }, { passive: true });
    var ty0 = 0, tTop = false;
    window.addEventListener('touchstart', function (e) { ty0 = e.touches[0].clientY; tTop = inSite && siteAtTop(); }, { passive: true });
    window.addEventListener('touchmove', function (e) {
      if (tTop && e.touches[0].clientY - ty0 > 28 && canReopen(e.target)) { tTop = false; reopenIntro(); }
    }, { passive: true });
    window.addEventListener('keydown', function (e) {
      if ((e.key === 'ArrowUp' || e.key === 'PageUp' || e.key === 'Home') && canReopen(e.target)) reopenIntro();
    });

    var rt = 0;
    window.addEventListener('resize', function () {
      if (inSite) return;
      cancelAnimationFrame(rt);
      rt = requestAnimationFrame(function () { layout(); render(P); if (st) st.refresh(); });
    });

    setTimeout(function () { try { scroller.focus({ preventScroll: true }); } catch (e) {} }, 300);
  }

  function el(tag, id) { var n = document.createElement(tag); n.id = id; return n; }
})(__OPTS__);
