// Confetti burst: draws falling paper pieces on a temporary canvas, then removes it.
function launchConfetti() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const canvas = document.createElement("canvas");
  canvas.className = "confetti-canvas";
  canvas.setAttribute("aria-hidden", "true");
  canvas.dataset.testid = "confetti-canvas";
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  document.body.appendChild(canvas);
  const ctx = canvas.getContext("2d");

  const colours = ["#fbbf24", "#22d3ee", "#ffffff", "#4169e1", "#f59e0b"];
  const count = window.innerWidth < 700 ? 90 : 180;
  const pieces = [];
  for (let i = 0; i < count; i++) {
    pieces.push({
      x: canvas.width / 2,
      y: canvas.height / 3,
      vx: (Math.random() - 0.5) * 16,       // sideways speed
      vy: Math.random() * -14 - 4,          // upward speed
      size: Math.random() * 8 + 5,
      spin: Math.random() * Math.PI,
      colour: colours[Math.floor(Math.random() * colours.length)]
    });
  }

  const start = performance.now();
  setTimeout(function () { canvas.remove(); }, 3500); // backup clean-up even if the tab is hidden
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    pieces.forEach(function (p) {
      p.vy += 0.35;      // gravity pulls pieces down
      p.vx *= 0.99;      // air slows them a little
      p.x += p.vx;
      p.y += p.vy;
      p.spin += 0.15;
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.spin);
      ctx.fillStyle = p.colour;
      ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
      ctx.restore();
    });
    if (performance.now() - start < 3000) requestAnimationFrame(draw); // run for 3 seconds
    else canvas.remove();
  }
  draw();
}
