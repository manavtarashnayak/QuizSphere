// Shared visual effects: 3D tilt, button ripple, scroll reveal.
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// 1. Tilt any element with class "tilt" toward the mouse
function enableTilt(root) {
  if (reduceMotion) return;
  (root || document).querySelectorAll(".tilt").forEach(function (card) {
    card.addEventListener("pointermove", function (e) {
      const box = card.getBoundingClientRect();
      const x = (e.clientX - box.left) / box.width - 0.5;  // -0.5 to 0.5
      const y = (e.clientY - box.top) / box.height - 0.5;
      card.style.transform =
        "perspective(900px) rotateX(" + (-y * 10) + "deg) rotateY(" + (x * 10) + "deg) translateY(-4px)";
    });
    card.addEventListener("pointerleave", function () { card.style.transform = ""; });
  });
}

// 2. Ripple circle when any .btn is clicked
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".btn");
  if (!btn || reduceMotion) return;
  const box = btn.getBoundingClientRect();
  const size = Math.max(box.width, box.height);
  const circle = document.createElement("span");
  circle.className = "ripple";
  circle.style.width = circle.style.height = size + "px";
  circle.style.left = e.clientX - box.left - size / 2 + "px";
  circle.style.top = e.clientY - box.top - size / 2 + "px";
  btn.appendChild(circle);
  setTimeout(function () { circle.remove(); }, 600);
});

// 3. Slide in elements with class "reveal" when they scroll into view
function enableReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    items.forEach(function (el) { el.classList.add("visible"); });
    return;
  }
  const watcher = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        watcher.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  items.forEach(function (el) { watcher.observe(el); });
}

document.addEventListener("DOMContentLoaded", function () {
  enableTilt();
  enableReveal();
});
