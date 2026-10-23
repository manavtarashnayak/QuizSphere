/* global getQuiz, themeOf, PASS_MARK */
// Achievement badges: worked out from the student's saved attempts (nothing extra is stored)

function topicOfAttempt(a) {
  if (a.theme) return a.theme;
  const quiz = getQuiz(a.quizId);
  return quiz ? themeOf(quiz) : "mix";
}

// Longest run of passed quizzes in a row (oldest to newest)
function bestStreak(list) {
  let best = 0, run = 0;
  list.forEach(function (a) {
    run = a.percent >= PASS_MARK ? run + 1 : 0;
    best = Math.max(best, run);
  });
  return best;
}

const BADGES = [
  { id: "first", icon: "1st", name: "First Steps", desc: "Finish your first quiz.",
    test: function (list) { return list.length >= 1; } },
  { id: "perfect", icon: "100", name: "Perfectionist", desc: "Score 100% on any quiz.",
    test: function (list) { return list.some(function (a) { return a.percent === 100; }); } },
  { id: "streak", icon: "×3", name: "Hat Trick", desc: "Pass 3 quizzes in a row.",
    test: function (list) { return bestStreak(list) >= 3; } },
  { id: "explorer", icon: "◎", name: "Explorer", desc: "Try Maths, General Knowledge and Web & Code.",
    test: function (list) {
      return ["math", "gk", "web"].every(function (t) { return list.some(function (a) { return topicOfAttempt(a) === t; }); });
    } },
  { id: "flyer", icon: "★", name: "High Flyer", desc: "Average 80% or more over 3+ quizzes.",
    test: function (list) {
      if (list.length < 3) return false;
      return list.reduce(function (s, a) { return s + a.percent; }, 0) / list.length >= 80;
    } },
  { id: "master", icon: "10", name: "Quiz Master", desc: "Complete 10 quizzes.",
    test: function (list) { return list.length >= 10; } }
];

function unlockedIds(list) {
  return BADGES.filter(function (b) { return b.test(list); }).map(function (b) { return b.id; });
}

// Draw badge coins into a container. Hover (or press) a coin to flip it in 3D.
// freshIds = badges just unlocked; they get a shiny spin animation.
function renderBadges(container, list, onlyIds, freshIds) {
  const unlocked = unlockedIds(list);
  container.innerHTML = "";
  BADGES.filter(function (b) { return !onlyIds || onlyIds.indexOf(b.id) !== -1; }).forEach(function (b) {
    const isOpen = unlocked.indexOf(b.id) !== -1;
    const isFresh = Boolean(freshIds) && freshIds.indexOf(b.id) !== -1;
    const coin = document.createElement("button");
    coin.type = "button";
    coin.className = "badge-coin " + (isOpen ? "unlocked" : "locked") + (isFresh ? " just-unlocked" : "");
    coin.dataset.testid = "badge-" + b.id;
    coin.setAttribute("aria-label", b.name + ", " + (isFresh ? "just unlocked" : isOpen ? "unlocked" : "locked") + ". " + b.desc);
    coin.innerHTML =
      '<span class="coin-inner" aria-hidden="true">' +
      '<span class="coin-face coin-front"><span class="coin-medal"></span><span class="coin-name"></span>' +
      '<span class="coin-status">' + (isFresh ? "New!" : isOpen ? "Unlocked" : "Locked") + "</span></span>" +
      '<span class="coin-face coin-back"><span class="coin-name"></span><span class="coin-desc"></span></span>' +
      "</span>";
    coin.querySelector(".coin-medal").textContent = b.icon;
    coin.querySelectorAll(".coin-name").forEach(function (n) { n.textContent = b.name; });
    coin.querySelector(".coin-desc").textContent = b.desc;
    coin.addEventListener("click", function () { coin.classList.toggle("flipped"); });
    container.appendChild(coin);
  });
  return unlocked.length;
}
