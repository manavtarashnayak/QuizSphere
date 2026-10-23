/* global requireRole, getQuizzes, getAllAttempts, PASS_MARK, themeOf, TOPIC_NAMES, ApiClient */
// Instructor dashboard logic with live backend sync
const teacher = requireRole("instructor");

// Turns a list of attempts into average score and pass rate
function summarise(list) {
  if (list.length === 0) return { average: "–", passRate: "–" };
  const total = list.reduce(function (sum, a) { return sum + a.percent; }, 0);
  const passed = list.filter(function (a) { return a.percent >= PASS_MARK; }).length;
  return {
    average: Math.round(total / list.length) + "%",
    passRate: Math.round((passed / list.length) * 100) + "%"
  };
}

async function loadInstructorData() {
  if (!teacher) return;

  let quizzes = getQuizzes();
  
  // Try fetching live quizzes from backend if connected
  if (typeof ApiClient !== "undefined") {
    const liveQuizzes = await ApiClient.getQuizzes();
    if (liveQuizzes && liveQuizzes.length > 0) {
      // Map backend quizzes to frontend format
      const mappedLive = liveQuizzes.map(q => ({
        id: q.id,
        title: q.title,
        description: q.description,
        minutes: q.duration_minutes,
        theme: "mix",
        questions: new Array(q.question_count || 1)
      }));
      // Merge unique
      const existingIds = new Set(quizzes.map(q => q.id));
      mappedLive.forEach(mq => {
        if (!existingIds.has(mq.id)) quizzes.push(mq);
      });
    }
  }

  const attempts = getAllAttempts();
  const overall = summarise(attempts);

  document.getElementById("welcome").textContent = "Welcome, " + teacher.name;
  document.getElementById("stat-quizzes").textContent = quizzes.length;
  document.getElementById("stat-attempts").textContent = attempts.length;
  document.getElementById("stat-average").textContent = overall.average;
  document.getElementById("stat-pass").textContent = overall.passRate;

  // Render rows
  const rows = document.getElementById("quiz-rows");
  rows.innerHTML = "";
  quizzes.forEach(function (quiz) {
    const mine = attempts.filter(function (a) { return a.quizId === quiz.id; });
    const stats = summarise(mine);
    const row = document.createElement("tr");
    const topic = themeOf(quiz);
    row.dataset.testid = "quiz-row-" + quiz.id;
    row.addEventListener("pointerenter", function () { window.setBgTheme(topic); });
    const labels = ["Quiz", "Subject", "Questions", "Time", "Attempts", "Average", "Pass rate"];
    const cells = [
      quiz.title,
      TOPIC_NAMES[topic] || "Mixed",
      (quiz.questions ? quiz.questions.length : "–"),
      (quiz.minutes || 15) + " min",
      mine.length,
      stats.average,
      stats.passRate
    ];
    cells.forEach(function (value, i) {
      const cell = document.createElement(i === 0 ? "th" : "td");
      if (i === 0) cell.scope = "row";
      cell.dataset.label = labels[i];
      cell.textContent = value;
      row.appendChild(cell);
    });
    rows.appendChild(row);
  });
  rows.addEventListener("pointerleave", function () { window.setBgTheme("mix"); });
}

loadInstructorData();
