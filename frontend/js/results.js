/* global requireUser, getAttempts, getQuiz, getParam, PASS_MARK, launchConfetti, themeOf, showTrophy, unlockedIds, renderBadges, BADGES */
// Results page logic
const viewer = requireUser();

if (viewer) {
  const attempt = getAttempts(viewer.email).find(function (a) { return a.id === getParam("attempt"); });
  // Newer attempts carry their own questions (custom subject / question-count tests)
  const source = attempt && getQuiz(attempt.quizId);
  const quiz = attempt && (attempt.questions
    ? { id: attempt.quizId, title: attempt.quizTitle, theme: attempt.theme, questions: attempt.questions }
    : source);

  if (!attempt || !quiz) {
    window.location.href = "student-dashboard.html";
  } else {
    const passed = attempt.percent >= PASS_MARK;
    const label = document.getElementById("pass-label");
    label.textContent = passed ? "Passed" : "Not passed";
    label.classList.add(passed ? "pass" : "fail");

    document.getElementById("result-title").textContent = quiz.title;
    window.setBgTheme(themeOf(quiz));
    document.getElementById("result-summary").textContent =
      "You answered " + attempt.correct + " out of " + attempt.total + " questions correctly. Pass mark is " + PASS_MARK + "%.";
    // "Try again" repeats the same setup: same subject or quiz, same number of questions
    document.getElementById("retry-btn").href = attempt.subject
      ? "take-quiz.html?subject=" + encodeURIComponent(attempt.subject) + "&count=" + attempt.total
      : "take-quiz.html?id=" + encodeURIComponent(quiz.id) + "&count=" + attempt.total;
    document.getElementById("score-ring").setAttribute("aria-label", "Score " + attempt.percent + " percent");

    // Animate the ring: the circle outline is "dashed" and we slide the dash in
    const ring = document.getElementById("ring-fill");
    const length = 2 * Math.PI * 52;
    ring.style.strokeDasharray = length;
    ring.style.strokeDashoffset = length;
    if (!passed) ring.style.stroke = "var(--danger)";
    setTimeout(function () { ring.style.strokeDashoffset = length * (1 - attempt.percent / 100); }, 200);

    // Celebrate great scores with confetti
    if (attempt.percent >= 80) setTimeout(launchConfetti, 900);

    // Perfect score: show the spinning 3D trophy
    if (attempt.percent === 100) {
      document.getElementById("trophy-section").hidden = false;
      showTrophy(document.getElementById("trophy3d"));
    }

    // Badge showcase: all badges, with ones unlocked by this attempt spinning in
    const all = getAttempts(viewer.email);
    let fresh = [];
    if (getParam("new") === "1" && all[all.length - 1].id === attempt.id) { // only right after submitting
      const before = unlockedIds(all.slice(0, -1));
      fresh = unlockedIds(all).filter(function (id) { return before.indexOf(id) === -1; });
      history.replaceState(null, "", "results.html?attempt=" + attempt.id); // reloading won't replay it
    }
    const earned = renderBadges(document.getElementById("new-badge-grid"), all, null, fresh);
    document.getElementById("showcase-count").textContent = earned + " of " + BADGES.length + " badges unlocked";
    if (fresh.length > 0) {
      document.getElementById("new-badges-eyebrow").textContent = "New achievement";
      document.getElementById("new-badges-title").textContent =
        fresh.length === 1 ? "Badge unlocked!" : fresh.length + " badges unlocked!";
    }

    // Count the number up from 0
    const text = document.getElementById("ring-text");
    let shown = 0;
    const counter = setInterval(function () {
      shown = Math.min(shown + 2, attempt.percent);
      text.textContent = shown + "%";
      if (shown >= attempt.percent) clearInterval(counter);
    }, 25);

    // Review list: your answer vs correct answer
    const list = document.getElementById("review-list");
    quiz.questions.forEach(function (q, i) {
      const mine = attempt.answers[i];
      const right = mine === q.answer;
      const item = document.createElement("li");
      item.className = "glass review-item" + (right ? "" : " wrong");
      item.dataset.testid = "review-item-" + (i + 1);
      item.innerHTML =
        "<h3></h3>" +
        "<p>Your answer: <strong class='mine'></strong></p>" +
        "<p>Correct answer: <strong class='right'></strong></p>";
      item.querySelector("h3").textContent = (i + 1) + ". " + q.text + (right ? "  ✓ Correct" : "  ✗ Incorrect");
      item.querySelector(".mine").textContent = mine === null ? "Not answered" : q.options[mine];
      item.querySelector(".right").textContent = q.options[q.answer];
      list.appendChild(item);
    });
  }
}
