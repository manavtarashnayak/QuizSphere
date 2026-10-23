/* global requireUser, getQuiz, getParam, saveAttempt, themeOf, getQuestionPool, shuffled, TOPIC_NAMES, SECONDS_PER_QUESTION */
// Take Quiz page logic
// Two ways in:  take-quiz.html?id=<quiz>&count=<n>      → n questions from one quiz
//               take-quiz.html?subject=<topic>&count=<n> → n random questions from a whole subject
const student = requireUser();
const quiz = buildTest();

if (student && !quiz) window.location.href = "student-dashboard.html";

function buildTest() {
  const wanted = parseInt(getParam("count"), 10);
  const subject = getParam("subject");
  let base;
  let pool;
  if (subject) {
    pool = getQuestionPool(subject);
    if (pool.length === 0) return null;
    base = {
      id: "subject-" + subject,
      theme: subject === "all" ? "mix" : subject,
      title: (subject === "all" ? "All Subjects" : TOPIC_NAMES[subject] || "Mixed") + " Test",
      secondsPerQuestion: SECONDS_PER_QUESTION
    };
  } else {
    const source = getQuiz(getParam("id"));
    if (!source) return null;
    pool = source.questions;
    base = {
      id: source.id,
      theme: themeOf(source),
      title: source.title,
      secondsPerQuestion: (source.minutes * 60) / source.questions.length
    };
  }
  // No count (or a bad one) → use every question; otherwise clamp to what's available
  const count = wanted > 0 ? Math.min(wanted, pool.length) : pool.length;
  // Using every question of a single quiz keeps its original order; a smaller pick is random
  const questions = (!subject && count === pool.length) ? pool.slice() : shuffled(pool).slice(0, count);
  return {
    id: base.id,
    theme: base.theme,
    title: base.title,
    subject: subject,
    requested: count,
    seconds: Math.max(30, Math.round(base.secondsPerQuestion * count)),
    questions: questions
  };
}

if (student && quiz) {
  let current = 0;                                          // index of the question on screen
  const answers = new Array(quiz.questions.length).fill(null); // chosen option per question
  const totalSeconds = quiz.seconds;
  let secondsLeft = totalSeconds;
  let timerId = null;

  const optionsBox = document.getElementById("options");
  const palette = document.getElementById("palette");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const dialog = document.getElementById("confirm-dialog");
  const letters = ["A", "B", "C", "D"];

  document.getElementById("quiz-name").textContent = quiz.title;
  document.title = quiz.title + " — QuizSphere";
  window.setBgTheme(themeOf(quiz)); // background shows this subject's shapes

  // Make one numbered button per question in the side palette
  quiz.questions.forEach(function (_, i) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = i + 1;
    b.setAttribute("aria-label", "Go to question " + (i + 1));
    b.dataset.testid = "palette-btn-" + (i + 1);
    b.addEventListener("click", function () { current = i; showQuestion(); b.focus(); });
    palette.appendChild(b);
  });

  function showQuestion() {
    const q = quiz.questions[current];
    document.getElementById("q-counter").textContent = "Question " + (current + 1) + " of " + quiz.questions.length;
    document.getElementById("q-text").textContent = q.text;

    optionsBox.innerHTML = "";
    q.options.forEach(function (text, i) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "option-btn";
      btn.dataset.testid = "option-" + i;
      btn.setAttribute("aria-pressed", answers[current] === i ? "true" : "false");
      btn.innerHTML = '<span class="option-letter" aria-hidden="true">' + letters[i] + "</span><span></span>";
      btn.lastChild.textContent = text;
      btn.addEventListener("click", function () {
        answers[current] = i;
        showQuestion();
        optionsBox.children[i].focus(); // keep keyboard focus on the chosen answer
      });
      optionsBox.appendChild(btn);
    });

    prevBtn.disabled = current === 0;
    nextBtn.disabled = current === quiz.questions.length - 1;

    palette.querySelectorAll("button").forEach(function (b, i) {
      b.classList.toggle("answered", answers[i] !== null);
      b.classList.toggle("current", i === current);
    });

    const answered = answers.filter(function (a) { return a !== null; }).length;
    document.getElementById("progress-bar").style.width = (answered / quiz.questions.length) * 100 + "%";
  }

  prevBtn.addEventListener("click", function () { if (current > 0) { current--; showQuestion(); } });
  nextBtn.addEventListener("click", function () { if (current < quiz.questions.length - 1) { current++; showQuestion(); } });

  // Countdown timer
  function tick() {
    const timer = document.getElementById("timer");
    const m = Math.floor(secondsLeft / 60);
    const s = secondsLeft % 60;
    timer.textContent = String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
    timer.setAttribute("aria-label", m + " minutes " + s + " seconds left");
    timer.classList.toggle("warning", secondsLeft <= 30);

    // Time bar shrinks with the time left and turns red near the end
    const percentLeft = (secondsLeft / totalSeconds) * 100;
    const bar = document.getElementById("time-bar");
    document.getElementById("time-bar-fill").style.width = percentLeft + "%";
    bar.setAttribute("aria-valuenow", Math.round(percentLeft));
    bar.classList.toggle("low", secondsLeft <= 30 || percentLeft <= 20);
    if (secondsLeft <= 0) { finish(); return; } // time is up: auto-submit
    secondsLeft--;
  }
  tick();
  timerId = setInterval(tick, 1000);

  // Ask before submitting
  document.getElementById("submit-btn").addEventListener("click", function () {
    const unanswered = answers.filter(function (a) { return a === null; }).length;
    document.getElementById("confirm-text").textContent = unanswered > 0
      ? "You have " + unanswered + " unanswered question(s). You cannot change answers after submitting."
      : "All questions answered. You cannot change answers after submitting.";
    dialog.showModal();
  });
  document.getElementById("cancel-submit").addEventListener("click", function () { dialog.close(); });
  document.getElementById("confirm-submit").addEventListener("click", finish);

  // Mark the quiz, save the attempt and go to the results page
  let finished = false;
  function finish() {
    if (finished) return; // stop double submits
    finished = true;
    clearInterval(timerId);
    let correct = 0;
    quiz.questions.forEach(function (q, i) { if (answers[i] === q.answer) correct++; });
    const attempt = {
      id: Date.now().toString(),
      email: student.email,
      quizId: quiz.id,
      quizTitle: quiz.title,
      theme: quiz.theme,
      subject: quiz.subject || null,           // set for subject tests
      questions: quiz.questions,               // the exact questions asked, so results can be reviewed
      answers: answers,
      correct: correct,
      total: quiz.questions.length,
      percent: Math.round((correct / quiz.questions.length) * 100),
      date: new Date().toISOString()
    };
    saveAttempt(attempt);
    window.location.href = "results.html?attempt=" + attempt.id + "&new=1"; // new=1 lets results show fresh badges once
  }

  showQuestion();
}
