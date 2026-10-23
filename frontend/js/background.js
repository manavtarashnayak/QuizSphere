// 3D background: slowly turning wireframe shapes that change colour with the subject.
// Everything is drawn with plain JavaScript on a <canvas>. No libraries.
(function () {
  const canvas = document.getElementById("bg-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const isPhone = window.innerWidth < 700;
  const calm = document.body.classList.contains("focus-mode");
  const pace = calm ? 0.35 : 1; // slower movement on the quiz page

  // ---------- 1. Subject themes: colour and 3D shapes ----------
  const THEMES = {
    mix:  { colour: [125, 170, 255], shapes: ["icosa", "globe", "layers", "torus", "cube", "octa", "planet"] },
    math: { colour: [251, 191, 36],  shapes: ["icosa", "cube", "torus", "octa", "tetra", "icosa", "cube"] },
    gk:   { colour: [52, 211, 153],  shapes: ["globe", "planet", "octa", "globe", "tetra", "planet", "icosa"] },
    web:  { colour: [34, 211, 238],  shapes: ["layers", "cube", "octa", "layers", "icosa", "cube", "layers"] }
  };

  // ---------- 2. Building 3D shapes as points (v) and lines between points (e) ----------
  function connectByLength(g, len) {
    for (let i = 0; i < g.v.length; i++) {
      for (let j = i + 1; j < g.v.length; j++) {
        const a = g.v[i], b = g.v[j];
        const d = Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
        if (Math.abs(d - len) < 0.01) g.e.push([i, j]);
      }
    }
    return g;
  }
  function scaleGeo(g, k) { g.v = g.v.map(function (p) { return [p[0] * k, p[1] * k, p[2] * k]; }); return g; }

  // A box: 8 corners, joined when they differ on exactly one side
  function box(g, cx, cy, cz, sx, sy, sz) {
    const start = g.v.length;
    for (let i = 0; i < 8; i++) {
      g.v.push([cx + (i & 1 ? sx : -sx), cy + (i & 2 ? sy : -sy), cz + (i & 4 ? sz : -sz)]);
    }
    for (let i = 0; i < 8; i++) {
      for (let j = i + 1; j < 8; j++) {
        const diff = i ^ j;
        if (diff === 1 || diff === 2 || diff === 4) g.e.push([start + i, start + j]);
      }
    }
    return g;
  }
  // A closed circle of points
  function ring(g, n, pointAt) {
    const start = g.v.length;
    for (let i = 0; i < n; i++) g.v.push(pointAt((i / n) * Math.PI * 2));
    for (let i = 0; i < n; i++) g.e.push([start + i, start + ((i + 1) % n)]);
    return g;
  }
  function globe(g, r) {
    [-60, -30, 0, 30, 60].forEach(function (deg) {
      const la = (deg * Math.PI) / 180;
      ring(g, 20, function (t) { return [Math.cos(t) * r * Math.cos(la), r * Math.sin(la), Math.sin(t) * r * Math.cos(la)]; });
    });
    for (let k = 0; k < 6; k++) {
      const lon = (k / 6) * Math.PI;
      ring(g, 20, function (t) { return [r * Math.cos(t) * Math.cos(lon), r * Math.sin(t), r * Math.cos(t) * Math.sin(lon)]; });
    }
    return g;
  }

  const BUILD = {
    cube: function () { return box({ v: [], e: [] }, 0, 0, 0, 0.8, 0.8, 0.8); },
    octa: function () {
      return connectByLength({ v: [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], e: [] }, Math.SQRT2);
    },
    tetra: function () {
      return scaleGeo(connectByLength({ v: [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], e: [] }, Math.sqrt(8)), 0.75);
    },
    icosa: function () {
      const p = (1 + Math.sqrt(5)) / 2, g = { v: [], e: [] };
      [-1, 1].forEach(function (a) {
        [-1, 1].forEach(function (b) { g.v.push([0, a, b * p], [a, b * p, 0], [b * p, 0, a]); });
      });
      return scaleGeo(connectByLength(g, 2), 1 / p);
    },
    torus: function () {
      const g = { v: [], e: [] }, U = 16, V = 8, R = 0.8, r = 0.32;
      for (let u = 0; u < U; u++) {
        for (let w = 0; w < V; w++) {
          const a = (u / U) * Math.PI * 2, b = (w / V) * Math.PI * 2;
          g.v.push([(R + r * Math.cos(b)) * Math.cos(a), r * Math.sin(b), (R + r * Math.cos(b)) * Math.sin(a)]);
          g.e.push([u * V + w, ((u + 1) % U) * V + w], [u * V + w, u * V + ((w + 1) % V)]);
        }
      }
      return g;
    },
    globe: function () { return globe({ v: [], e: [] }, 1); },
    planet: function () {
      const g = globe({ v: [], e: [] }, 0.6), tilt = 0.45;
      [1.15, 1.4].forEach(function (rad) {
        ring(g, 36, function (t) {
          const x = Math.cos(t) * rad, z = Math.sin(t) * rad;
          return [x, z * Math.sin(tilt), z * Math.cos(tilt)];
        });
      });
      return g;
    },
    layers: function () {
      const g = { v: [], e: [] };
      [-0.55, 0, 0.55].forEach(function (y) { box(g, 0, y, 0, 0.9, 0.12, 0.9); });
      return g;
    }
  };

  // ---------- 3. Things on screen ----------
  let W = 0, H = 0;
  let theme = "";
  let shapes = [], dots = [];
  let colour = THEMES.mix.colour.slice(); // particle colour, fades between themes
  const mouse = { x: -9999, y: -9999, nx: 0, ny: 0 };

  function makeShape(type, i, total, rgb) {
    const depth = 0.35 + Math.random() * 0.65; // 1 = close to you, 0.35 = far away
    return {
      geo: BUILD[type](), depth: depth, colour: rgb,
      x: ((i + 0.5) / total + (Math.random() - 0.5) * 0.12) * W,
      y: (0.12 + Math.random() * 0.76) * H,
      size: (isPhone ? 45 : 85) * depth + Math.random() * 25,
      rx: Math.random() * 6, ry: Math.random() * 6,
      rsx: (Math.random() - 0.5) * 0.006, rsy: 0.003 + Math.random() * 0.006,
      dx: (Math.random() - 0.5) * 0.25, dy: (Math.random() - 0.5) * 0.2,
      alpha: 0, target: 1, spin: 0, pulse: 0.3
    };
  }
  function makeDots() {
    dots = [];
    const n = isPhone ? 25 : calm ? 30 : 55;
    for (let i = 0; i < n; i++) {
      dots.push({ x: Math.random() * W, y: Math.random() * H, r: Math.random() * 1.8 + 0.6, dx: (Math.random() - 0.5) * 0.3, dy: (Math.random() - 0.5) * 0.3 });
    }
  }

  // Swap to a new subject: old shapes fade out, new ones fade in
  function setTheme(name) {
    if (!THEMES[name]) name = "mix";
    if (name === theme) return;
    theme = name;
    const t = THEMES[name];
    document.body.dataset.theme = name;

    shapes.forEach(function (s) { s.target = 0; });
    const n = isPhone ? 4 : calm ? 5 : 7;
    for (let i = 0; i < n; i++) shapes.push(makeShape(t.shapes[i % t.shapes.length], i, n, t.colour));

    if (reduceMotion) { // no animation: show the new set straight away
      shapes = shapes.filter(function (s) { return s.target === 1; });
      shapes.forEach(function (s) { s.alpha = 1; s.pulse = 0; });
      colour = t.colour.slice();
      draw();
    }
  }

  // ---------- 4. 3D to 2D: rotate each point, then shrink it with distance (perspective) ----------
  function drawShape(s) {
    const ax = s.rx + mouse.ny * 0.4, ay = s.ry + mouse.nx * 0.4; // shapes lean toward the mouse
    const cx = Math.cos(ax), sx = Math.sin(ax), cy = Math.cos(ay), sy = Math.sin(ay);
    const scale = s.size * (1 + s.pulse);
    const ox = s.x + mouse.nx * 30 * s.depth, oy = s.y + mouse.ny * 20 * s.depth;
    const pts = s.geo.v.map(function (p) {
      const y1 = p[1] * cx - p[2] * sx, z1 = p[1] * sx + p[2] * cx;
      const x2 = p[0] * cy + z1 * sy, z2 = -p[0] * sy + z1 * cy;
      const persp = 500 / (500 + z2 * scale);
      return [ox + x2 * scale * persp, oy + y1 * scale * persp];
    });
    const rgb = s.colour.join(","), a = s.alpha * (0.35 + 0.5 * s.depth);

    // soft glow behind the shape
    const glow = ctx.createRadialGradient(ox, oy, 0, ox, oy, scale * 1.6);
    glow.addColorStop(0, "rgba(" + rgb + "," + a * 0.18 + ")");
    glow.addColorStop(1, "rgba(" + rgb + ",0)");
    ctx.fillStyle = glow;
    ctx.fillRect(ox - scale * 1.6, oy - scale * 1.6, scale * 3.2, scale * 3.2);

    // lines
    ctx.beginPath();
    s.geo.e.forEach(function (e) { ctx.moveTo(pts[e[0]][0], pts[e[0]][1]); ctx.lineTo(pts[e[1]][0], pts[e[1]][1]); });
    ctx.strokeStyle = "rgba(" + rgb + "," + a + ")";
    ctx.lineWidth = 0.8 + s.depth * 1.2;
    ctx.shadowBlur = 14 * s.depth;
    ctx.shadowColor = "rgba(" + rgb + "," + a + ")";
    ctx.stroke();

    // corner dots on simple shapes
    if (pts.length <= 40) {
      ctx.beginPath();
      pts.forEach(function (p) { ctx.moveTo(p[0], p[1]); ctx.arc(p[0], p[1], 1.4 + s.depth * 1.6, 0, Math.PI * 2); });
      ctx.fillStyle = "rgba(255,255,255," + a + ")";
      ctx.fill();
    }
    ctx.shadowBlur = 0;
  }

  function drawDots() {
    const rgb = colour.map(Math.round).join(",");
    ctx.fillStyle = "rgba(" + rgb + ",0.7)";
    dots.forEach(function (d) {
      const mx = d.x - mouse.x, my = d.y - mouse.y, dist = Math.hypot(mx, my);
      if (dist < 120 && dist > 0) { d.x += mx / dist; d.y += my / dist; } // move away from mouse
      d.x += d.dx * pace; d.y += d.dy * pace;
      if (d.x < 0 || d.x > W) d.dx *= -1;
      if (d.y < 0 || d.y > H) d.dy *= -1;
      ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2); ctx.fill();
    });
    ctx.beginPath();
    for (let i = 0; i < dots.length; i++) {
      for (let j = i + 1; j < dots.length; j++) {
        if (Math.hypot(dots[i].x - dots[j].x, dots[i].y - dots[j].y) < 110) {
          ctx.moveTo(dots[i].x, dots[i].y); ctx.lineTo(dots[j].x, dots[j].y);
        }
      }
    }
    ctx.strokeStyle = "rgba(" + rgb + ",0.08)";
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  // ---------- 5. Move everything a tiny bit each frame ----------
  function update() {
    shapes.forEach(function (s) {
      s.alpha += (s.target - s.alpha) * 0.04;
      s.rx += s.rsx * pace + s.spin * 0.3;
      s.ry += s.rsy * pace + s.spin;
      s.spin *= 0.96;
      s.pulse *= 0.93;
      s.x += s.dx * pace; s.y += s.dy * pace;
      const m = s.size * 2;
      if (s.x < -m) s.x = W + m; if (s.x > W + m) s.x = -m;
      if (s.y < -m) s.y = H + m; if (s.y > H + m) s.y = -m;
    });
    shapes = shapes.filter(function (s) { return s.target === 1 || s.alpha > 0.01; });
    const goal = THEMES[theme].colour;
    colour = colour.map(function (c, i) { return c + (goal[i] - c) * 0.04; });
  }

  function draw() {
    const bg = ctx.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0, "#0b0907");
    bg.addColorStop(1, "#22170e");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);
    drawDots();
    shapes.slice().sort(function (a, b) { return a.depth - b.depth; }).forEach(drawShape); // far ones first
  }

  function loop() {
    if (!document.hidden) { update(); draw(); } // pause while the tab is hidden
    requestAnimationFrame(loop);
  }

  // ---------- 6. Interaction ----------
  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  window.addEventListener("resize", function () { resize(); makeDots(); if (reduceMotion) draw(); });
  window.addEventListener("pointermove", function (e) {
    mouse.x = e.clientX; mouse.y = e.clientY;
    mouse.nx = (e.clientX / W - 0.5) * 2; mouse.ny = (e.clientY / H - 0.5) * 2;
  });
  // Click or tap: nearby shapes spin and bounce
  window.addEventListener("pointerdown", function (e) {
    shapes.forEach(function (s) {
      const d = Math.hypot(s.x - e.clientX, s.y - e.clientY);
      if (d < s.size * 3) { s.spin = 0.15; s.pulse = 0.25; } else { s.spin += 0.02; }
    });
  });

  // Other pages call these: window.setBgTheme("math")
  window.setBgTheme = setTheme;
  window.BG_THEMES = THEMES;

  resize();
  makeDots();
  setTheme(document.body.dataset.theme || "mix");
  if (reduceMotion) draw(); else loop();
})();
