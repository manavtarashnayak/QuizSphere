/* global DEMO_USERS, login, ApiClient */
// Login page logic connecting to FastAPI Backend with Local Fallback
const form = document.getElementById("login-form");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const errorBox = document.getElementById("form-error");

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.add("show");
}

// Demo buttons fill in the form for you
function fillDemo(role) {
  const user = DEMO_USERS.find(function (u) { return u.role === role; });
  emailInput.value = user.email;
  passwordInput.value = user.password;
  document.getElementById("role-" + role).checked = true;
  errorBox.classList.remove("show");
}
document.getElementById("demo-student").addEventListener("click", function () { fillDemo("student"); });
document.getElementById("demo-instructor").addEventListener("click", function () { fillDemo("instructor"); });

form.addEventListener("submit", async function (event) {
  event.preventDefault();
  const role = form.querySelector('input[name="role"]:checked').value;

  if (!emailInput.value || !passwordInput.value) {
    showError("Please enter your email and password.");
    return;
  }

  // 1. Try Live Backend API First
  let user = null;
  if (typeof ApiClient !== "undefined") {
    user = await ApiClient.login(emailInput.value, passwordInput.value, role);
  }

  // 2. If backend is offline or returned error, fallback to offline local database
  if (!user) {
    user = login(emailInput.value, passwordInput.value, role);
  }

  if (!user) {
    showError("Email, password or role is not correct. Try a demo account.");
    return;
  }

  // Each role goes to its own dashboard
  window.location.href = user.role === "instructor" ? "instructor-dashboard.html" : "student-dashboard.html";
});
