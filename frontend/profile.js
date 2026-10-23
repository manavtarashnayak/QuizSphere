/* global requireUser, updateUserName */
// Profile page: show account details and let the user change their display name
const person = requireUser();

if (person) {
  const nameInput = document.getElementById("profile-name");
  const errorBox = document.getElementById("form-error");
  const successBox = document.getElementById("form-success");
  const avatar = document.getElementById("profile-avatar");

  function initials(name) {
    return name.split(/\s+/).map(function (w) { return w.charAt(0); }).join("").slice(0, 2).toUpperCase();
  }

  if (person.role === "instructor") document.getElementById("nav-dashboard").href = "instructor-dashboard.html";
  document.getElementById("profile-role").textContent = person.role === "instructor" ? "Instructor" : "Student";
  document.getElementById("profile-email").textContent = person.email;
  nameInput.value = person.name;
  avatar.textContent = initials(person.name);

  // Live preview of the initials while typing
  nameInput.addEventListener("input", function () {
    successBox.classList.remove("show");
    avatar.textContent = initials(nameInput.value.trim() || "?");
  });

  document.getElementById("profile-form").addEventListener("submit", function (event) {
    event.preventDefault();
    errorBox.classList.remove("show");
    successBox.classList.remove("show");
    const name = nameInput.value.trim().replace(/\s+/g, " ");

    if (name.length < 2) {
      errorBox.textContent = "Please enter a name with at least 2 characters.";
      errorBox.classList.add("show");
      return;
    }

    updateUserName(person.email, name);
    nameInput.value = name;
    successBox.textContent = "Saved! Your dashboard and the leaderboard will now show \"" + name + "\".";
    successBox.classList.add("show");
  });
}
