/* global DEMO_USERS, login */
// Login page logic
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

form.addEventListener("submit", function (event) {
  event.preventDefault(); // stop the page from reloading
  const role = form.querySelector('input[name="role"]:checked').value;

  if (!emailInput.value || !passwordInput.value) {
    showError("Please enter your email and password.");
    return;
  }

  const user = login(emailInput.value, passwordInput.value, role);
  if (!user) {
    showError("Email, password or role is not correct. Try a demo account.");
    return;
  }

  // Each role goes to its own dashboard
  window.location.href = user.role === "instructor" ? "instructor-dashboard.html" : "student-dashboard.html";
});
