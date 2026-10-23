/* global requireRole, getAttempts, getQuiz, themeOf, TOPIC_NAMES, PASS_MARK */
// History page: every past attempt, filtered by subject
const learner = requireRole("student");

if (learner) {
  const list = document.getElementById("history-list");
  const count = document.getElementById("history-count");
  const chips = document.querySelectorAll("#filters .chip");

  // Newest first, and remember each attempt's subject
  const attempts = getAttempts(learner.email).reverse().map(function (a) {
    const quiz = getQuiz(a.quizId);
    return { data: a, topic: a.theme || (quiz ? themeOf(quiz) : "mix") };
  });

  function render(topic) {
    const shown = attempts.filter(function (a) { return topic === "all" || a.topic === topic; });
    list.innerHTML = "";
    count.textContent = "Showing " + shown.length + " of " + attempts.length + " attempt(s)";

    if (shown.length === 0) {
      list.innerHTML = '<li class="empty-note" data-testid="history-empty">No attempts for this subject yet.</li>';
      return;
    }
    shown.forEach(function (entry) {
      const a = entry.data;
      const passed = a.percent >= PASS_MARK;
      const item = document.createElement("li");
      item.className = "glass attempt-item history-item";
      item.dataset.topic = entry.topic;
      item.dataset.testid = "history-item-" + a.id;
      item.innerHTML =
        '<div><span class="topic-tag"></span><h3></h3><p class="hint date"></p></div>' +
        '<div class="history-score"><strong class="stat-value"></strong>' +
        '<span class="pass-label ' + (passed ? "pass" : "fail") + '">' + (passed ? "Passed" : "Not passed") + "</span></div>" +
        '<a class="btn btn-ghost" href="results.html?attempt=' + a.id + '" data-testid="history-view-' + a.id + '">View result</a>';
      item.querySelector(".topic-tag").textContent = TOPIC_NAMES[entry.topic];
      item.querySelector("h3").textContent = a.quizTitle;
      item.querySelector(".date").textContent = new Date(a.date).toLocaleString() + " · " + a.correct + "/" + a.total + " correct";
      item.querySelector(".stat-value").textContent = a.percent + "%";
      list.appendChild(item);
    });
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      window.setBgTheme(chip.dataset.topic === "all" ? "mix" : chip.dataset.topic);
      render(chip.dataset.topic);
    });
  });

  render("all");
}
