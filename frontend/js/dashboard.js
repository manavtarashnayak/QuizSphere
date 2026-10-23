/* global requireRole, getQuizzes, getAttempts, enableTilt, themeOf, TOPIC_NAMES, renderBadges, BADGES */
// Student dashboard logic
const user = requireRole("student");

if (user) {
  const quizzes = getQuizzes();
  const attempts = getAttempts(user.email);

  document.getElementById("welcome").textContent = "Welcome, " + user.name;
  document.getElementById("stat-available").textContent = quizzes.length;
  document.getElementById("stat-taken").textContent = attempts.length;

  if (attempts.length > 0) {
    const total = attempts.reduce(function (sum, a) { return sum + a.percent; }, 0);
    document.getElementById("stat-average").textContent = Math.round(total / attempts.length) + "%";
  }

  // Build one card per quiz
  const grid = document.getElementById("quiz-grid");
  quizzes.forEach(function (quiz) {
    const topic = themeOf(quiz);
    const card = document.createElement("article");
    card.className = "glass tilt quiz-card";
    card.dataset.topic = topic;
    card.dataset.testid = "quiz-card-" + quiz.id;
    card.innerHTML =
      '<span class="topic-tag pop"></span>' +
      '<h3 class="pop"></h3>' +
      "<p></p>" +
      '<div class="quiz-meta">' +
      '<span class="badge">' + quiz.questions.length + " questions</span>" +
      '<span class="badge">' + quiz.minutes + " min</span>" +
      "</div>" +
      '<a class="btn btn-primary" href="take-quiz.html?id=' + encodeURIComponent(quiz.id) + '" data-testid="start-quiz-' + quiz.id + '">Start quiz</a>';
    // textContent keeps quiz text safe (no HTML injection)
    card.querySelector(".topic-tag").textContent = TOPIC_NAMES[topic];
    card.querySelector("h3").textContent = quiz.title;
    card.querySelector("p").textContent = quiz.description;
    // Hovering or tabbing to a card shows that subject's 3D shapes
    card.addEventListener("pointerenter", function () { window.setBgTheme(topic); });
    card.addEventListener("focusin", function () { window.setBgTheme(topic); });
    grid.appendChild(card);
  });
  grid.addEventListener("pointerleave", function () { window.setBgTheme("mix"); });

  // Show the 5 most recent attempts
  const list = document.getElementById("attempt-list");
  if (attempts.length === 0) {
    list.innerHTML = '<li class="empty-note">No attempts yet. Pick a quiz above to begin.</li>';
  } else {
    attempts.slice(-5).reverse().forEach(function (a) {
      const item = document.createElement("li");
      item.className = "glass attempt-item";
      item.innerHTML = "<strong></strong><span></span>" +
        '<a class="btn btn-ghost" href="results.html?attempt=' + a.id + '">View result</a>';
      item.querySelector("strong").textContent = a.quizTitle;
      item.querySelector("span").textContent = a.percent + "% · " + new Date(a.date).toLocaleDateString();
      list.appendChild(item);
    });
  }

  enableTilt(grid); // cards were added after page load, so switch tilt on for them

  // Achievement badges (oldest attempt first, so streaks are counted in order)
  const earned = renderBadges(document.getElementById("badge-grid"), attempts);
  document.getElementById("badge-count").textContent = earned + " of " + BADGES.length + " unlocked · hover or press a badge to flip it";
}
