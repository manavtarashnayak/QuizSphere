/* global registerUser, login */
// Register page logic
const regForm = document.getElementById("register-form");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const confirmInput = document.getElementById("confirm");
const meter = document.getElementById("strength");
const meterText = document.getElementById("strength-text");
const errorBox = document.getElementById("form-error");

// Score the password from 0 to 4: one point for each rule it follows
function passwordScore(pw) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  if (pw.length < 8) return Math.min(score, 1); // under 8 characters is always weak
  return score;
}

const LEVEL_WORDS = ["Too short", "Weak", "Fair", "Good", "Strong"];

passwordInput.addEventListener("input", function () {
  const score = passwordInput.value ? passwordScore(passwordInput.value) : 0;
  meter.dataset.level = score;
  meterText.textContent = passwordInput.value
    ? "Strength: " + LEVEL_WORDS[score]
    : "Use 8+ characters with a capital letter, a number and a symbol.";
});

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.add("show");
}

regForm.addEventListener("submit", function (event) {
  event.preventDefault();
  errorBox.classList.remove("show");
  const role = regForm.querySelector('input[name="role"]:checked').value;
  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!name || !email || !password) { showError("Please fill in your name, email and password."); return; }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { showError("Please enter a valid email address."); return; }
  if (password.length < 8 || passwordScore(password) < 3) {
    showError("Please choose a stronger password (at least \"Good\").");
    return;
  }
  if (password !== confirmInput.value) { showError("The two passwords do not match."); return; }

  if (!registerUser({ name: name, email: email, password: password, role: role })) {
    showError("An account with this email already exists. Try logging in.");
    return;
  }

  // Sign in straight away and go to the right dashboard
  login(email, password, role);
  window.location.href = role === "instructor" ? "instructor-dashboard.html" : "student-dashboard.html";
});
