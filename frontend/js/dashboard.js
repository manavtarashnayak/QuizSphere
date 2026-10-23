/* global requireRole, getQuizzes, getAttempts, enableTilt, themeOf, TOPIC_NAMES, renderBadges, BADGES,
   getSubjectsWithCounts, getQuestionPool, countPresets, SECONDS_PER_QUESTION */
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

  const SUBJECT_COLOURS = { math: "#fbbf24", gk: "#34d399", web: "#22d3ee", mix: "#93b4ff" };

  // Reusable "how many questions" picker: quick-pick chips + a − / number / + stepper
  function makeCountPicker(box, prefix, onChange) {
    let max = 1;
    let value = 0; // 0 = nothing picked yet, so the first setMax uses the default
    box.className = "count-picker";
    box.innerHTML =
      '<div class="count-presets" role="group" aria-label="Quick pick"></div>' +
      '<div class="count-stepper">' +
      '<button type="button" class="step-btn" aria-label="Fewer questions" data-testid="' + prefix + '-minus">−</button>' +
      '<label class="sr-only" for="' + prefix + '-input">Number of questions</label>' +
      '<input type="number" id="' + prefix + '-input" inputmode="numeric" min="1" data-testid="' + prefix + '-input">' +
      '<button type="button" class="step-btn" aria-label="More questions" data-testid="' + prefix + '-plus">+</button>' +
      '<span class="count-of"></span>' +
      "</div>";
    const presets = box.querySelector(".count-presets");
    const input = box.querySelector("input");
    const [minus, plus] = box.querySelectorAll(".step-btn");

    function set(n) {
      value = Math.min(max, Math.max(1, Math.round(n) || 1));
      input.value = value;
      minus.disabled = value <= 1;
      plus.disabled = value >= max;
      presets.querySelectorAll(".chip").forEach(function (c) {
        c.setAttribute("aria-pressed", Number(c.dataset.count) === value ? "true" : "false");
      });
      onChange(value);
    }

    minus.addEventListener("click", function () { set(value - 1); });
    plus.addEventListener("click", function () { set(value + 1); });
    input.addEventListener("change", function () { set(Number(input.value)); });
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); set(Number(input.value)); } });

    return {
      setMax: function (newMax, preferred) {
        max = Math.max(1, newMax);
        input.max = max;
        box.querySelector(".count-of").textContent = "of " + max + " available";
        presets.innerHTML = "";
        countPresets(max).forEach(function (n) {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = "chip chip-sm";
          chip.dataset.count = n;
          chip.dataset.testid = prefix + "-preset-" + n;
          chip.textContent = n === max ? "All " + n : String(n);
          chip.addEventListener("click", function () { set(n); });
          presets.appendChild(chip);
        });
        set(preferred || Math.min(10, max));
      },
      value: function () { return value; }
    };
  }

  function minutesText(seconds) {
    const m = Math.max(1, Math.round(seconds / 60));
    return m + " min";
  }

  // ---- "Start a test" panel: subject + number of questions ----
  const subjects = getSubjectsWithCounts();
  const subjectChips = document.getElementById("subject-chips");
  const summary = document.getElementById("setup-summary");
  let chosenSubject = "all";

  const setupPicker = makeCountPicker(document.getElementById("setup-count"), "setup-count", function (n) {
    const name = chosenSubject === "all" ? "All subjects" : TOPIC_NAMES[chosenSubject];
    summary.textContent = name + " · " + n + " question" + (n === 1 ? "" : "s") + " · " + minutesText(n * SECONDS_PER_QUESTION);
  });

  const subjectOptions = [{ key: "all", name: "All subjects", count: getQuestionPool("all").length }].concat(subjects);
  subjectOptions.forEach(function (sub) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.dataset.topic = sub.key;
    chip.dataset.testid = "subject-" + sub.key;
    chip.setAttribute("aria-pressed", sub.key === chosenSubject ? "true" : "false");
    chip.innerHTML = (SUBJECT_COLOURS[sub.key] ? '<span class="chip-dot" aria-hidden="true"></span>' : "") +
      '<span class="chip-name"></span><span class="chip-count"></span>';
    if (SUBJECT_COLOURS[sub.key]) chip.querySelector(".chip-dot").style.background = SUBJECT_COLOURS[sub.key];
    chip.querySelector(".chip-name").textContent = sub.name;
    chip.querySelector(".chip-count").textContent = sub.count;
    chip.setAttribute("aria-label", sub.name + ", " + sub.count + " questions");
    chip.addEventListener("click", function () { chooseSubject(sub.key); });
    subjectChips.appendChild(chip);
  });

  function chooseSubject(key) {
    chosenSubject = key;
    subjectChips.querySelectorAll(".chip").forEach(function (c) {
      c.setAttribute("aria-pressed", c.dataset.topic === key ? "true" : "false");
    });
    window.setBgTheme(key === "all" ? "mix" : key);
    const keep = setupPicker.value();
    setupPicker.setMax(getQuestionPool(key).length, keep);
    filterCards(key);
  }

  document.getElementById("start-test-btn").addEventListener("click", function () {
    window.location.href = "take-quiz.html?subject=" + encodeURIComponent(chosenSubject) + "&count=" + setupPicker.value();
  });

  // ---- Quiz cards: each one asks how many questions before starting ----
  const dialog = document.getElementById("count-dialog");
  const dialogSummary = document.getElementById("dialog-summary");
  let dialogQuiz = null;
  const dialogPicker = makeCountPicker(document.getElementById("dialog-count"), "dialog-count", function (n) {
    if (!dialogQuiz) return;
    const secs = (dialogQuiz.minutes * 60 * n) / dialogQuiz.questions.length;
    dialogSummary.textContent = n + " question" + (n === 1 ? "" : "s") + " · " + minutesText(secs);
  });

  function openCountDialog(quiz) {
    dialogQuiz = quiz;
    document.getElementById("count-dialog-title").textContent = quiz.title;
    document.getElementById("count-dialog-text").textContent =
      "This quiz has " + quiz.questions.length + " questions. How many do you want to answer?";
    dialogPicker.setMax(quiz.questions.length, quiz.questions.length);
    dialog.showModal();
  }
  document.getElementById("count-cancel").addEventListener("click", function () { dialog.close(); });
  document.getElementById("count-start").addEventListener("click", function () {
    window.location.href = "take-quiz.html?id=" + encodeURIComponent(dialogQuiz.id) + "&count=" + dialogPicker.value();
  });

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
      '<button type="button" class="btn btn-primary" data-testid="start-quiz-' + quiz.id + '">Start quiz</button>';
    // textContent keeps quiz text safe (no HTML injection)
    card.querySelector(".topic-tag").textContent = TOPIC_NAMES[topic];
    card.querySelector("h3").textContent = quiz.title;
    card.querySelector("p").textContent = quiz.description;
    card.querySelector("button").addEventListener("click", function () { openCountDialog(quiz); });
    // Hovering or tabbing to a card shows that subject's 3D shapes
    card.addEventListener("pointerenter", function () { window.setBgTheme(topic); });
    card.addEventListener("focusin", function () { window.setBgTheme(topic); });
    grid.appendChild(card);
  });
  grid.addEventListener("pointerleave", function () { window.setBgTheme(chosenSubject === "all" ? "mix" : chosenSubject); });

  // Only show quiz cards for the chosen subject
  function filterCards(key) {
    let shown = 0;
    grid.querySelectorAll(".quiz-card").forEach(function (card) {
      const show = key === "all" || card.dataset.topic === key;
      card.hidden = !show;
      if (show) shown++;
    });
    document.getElementById("quiz-filter-note").textContent = key === "all"
      ? "Showing all " + shown + " quizzes."
      : "Showing " + shown + " " + TOPIC_NAMES[key] + " quiz" + (shown === 1 ? "" : "zes") + ".";
  }

  chooseSubject("all");

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
