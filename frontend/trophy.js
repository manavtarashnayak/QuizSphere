// Spinning gold 3D trophy made from flat trophy outlines turned around a centre line.
function showTrophy(container) {
  const outline =
    '<svg viewBox="0 0 100 140" aria-hidden="true">' +
    '<path d="M20 8 H80 C80 44 68 62 50 66 C32 62 20 44 20 8 Z"/>' +   // cup
    '<rect x="45" y="64" width="10" height="28"/>' +                       // stem
    '<path d="M36 92 H64 L60 104 H40 Z"/>' +                               // neck
    '<rect x="26" y="104" width="48" height="16" rx="3"/>' +               // base
    "</svg>";
  // 12 copies, each turned 15 degrees more, look like one solid round trophy
  for (let i = 0; i < 12; i++) {
    const slice = document.createElement("div");
    slice.className = "trophy-slice";
    slice.style.transform = "rotateY(" + i * 15 + "deg)";
    slice.innerHTML = outline;
    container.appendChild(slice);
  }
}
