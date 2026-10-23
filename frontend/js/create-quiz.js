/* global requireRole, saveQuiz */
// Create Quiz page logic
const author = requireRole("instructor");

if (author) {
  const list = document.getElementById("question-list");
  const errorBox = document.getElementById("form-error");
  const letters = ["A", "B", "C", "D"];
  let counter = 0; // gives every question block a unique id

  // Build one question block: text, 4 options, and radio buttons to mark the correct one
  function addQuestion() {
    counter++;
    const id = counter;
    const block = document.createElement("fieldset");
    block.className = "glass builder-card question-block";
    block.dataset.testid = "question-block";

    let html = '<legend class="q-legend"></legend>' +
      '<div class="form-group"><label for="q' + id + '-text">Question text</label>' +
      '<input type="text" id="q' + id + '-text" class="q-text-input" required data-testid="question-text-input"></div>' +
      '<p class="hint">Type the 4 answer choices and select the correct one.</p>';
    letters.forEach(function (letter, i) {
      html += '<div class="option-row">' +
        '<input type="radio" name="q' + id + '-correct" id="q' + id + '-c' + i + '" value="' + i + '"' + (i === 0 ? " checked" : "") +
        ' aria-label="Mark option ' + letter + ' as correct" data-testid="correct-radio-' + i + '">' +
        '<label for="q' + id + '-o' + i + '" class="option-letter">' + letter + "</label>" +
        '<input type="text" id="q' + id + '-o' + i + '" class="q-option-input" placeholder="Option ' + letter + '" required data-testid="option-input-' + i + '">' +
        "</div>";
    });
    html += '<button type="button" class="btn btn-ghost remove-btn" data-testid="remove-question-btn">Remove question</button>';
    block.innerHTML = html;

    block.querySelector(".remove-btn").addEventListener("click", function () {
      if (list.children.length === 1) { showError("A quiz needs at least one question."); return; }
      block.remove();
      renumber();
    });

    list.appendChild(block);
    renumber();
    block.querySelector(".q-text-input").focus();
  }

  // Keep the "Question 1, 2, 3" titles in order after adding or removing
  function renumber() {
    list.querySelectorAll(".q-legend").forEach(function (legend, i) {
      legend.textContent = "Question " + (i + 1);
    });
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.add("show");
  }

  document.getElementById("add-question").addEventListener("click", addQuestion);

  // Preview the chosen subject's 3D shapes straight away
  const topicSelect = document.getElementById("quiz-topic");
  topicSelect.addEventListener("change", function () { window.setBgTheme(topicSelect.value); });

  document.getElementById("quiz-form").addEventListener("submit", function (event) {
    event.preventDefault();
    errorBox.classList.remove("show");

    const title = document.getElementById("quiz-title").value.trim();
    const description = document.getElementById("quiz-desc").value.trim();
    const minutes = parseInt(document.getElementById("quiz-minutes").value, 10);

    if (!title) { showError("Please give the quiz a title."); return; }
    if (!minutes || minutes < 1 || minutes > 180) { showError("Time limit must be between 1 and 180 minutes."); return; }

    // Collect every question block into plain data
    const questions = [];
    const blocks = list.querySelectorAll(".question-block");
    for (let b = 0; b < blocks.length; b++) {
      const block = blocks[b];
      const text = block.querySelector(".q-text-input").value.trim();
      const options = Array.from(block.querySelectorAll(".q-option-input")).map(function (input) { return input.value.trim(); });
      if (!text || options.some(function (o) { return !o; })) {
        showError("Question " + (b + 1) + " needs its text and all 4 options filled in.");
        return;
      }
      const answer = parseInt(block.querySelector('input[type="radio"]:checked').value, 10);
      questions.push({ text: text, options: options, answer: answer });
    }

    saveQuiz({
      id: "quiz-" + Date.now(),
      title: title,
      theme: topicSelect.value,
      description: description || "A quiz created by " + author.name + ".",
      minutes: minutes,
      questions: questions
    });
    window.location.href = "instructor-dashboard.html";
  });

  addQuestion(); // start with one empty question
}
