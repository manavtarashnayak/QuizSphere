// OFFLINE DEMO MODE: sample users, quizzes and scores saved in the browser (localStorage).
// Nothing is sent to a server. Real API calls will be added once the teammate shares endpoints.

const DEMO_USERS = [
  { email: "student@college.edu", password: "student123", role: "student", name: "Demo Student" },
  { email: "instructor@college.edu", password: "instructor123", role: "instructor", name: "Demo Instructor" }
];

const DEMO_QUIZZES = [
  {
    id: "gk-101",
    theme: "gk",
    title: "General Knowledge",
    description: "Warm up with questions about the world around you.",
    minutes: 10,
    questions: [
      { text: "What is the capital city of Japan?", options: ["Seoul", "Tokyo", "Beijing", "Bangkok"], answer: 1 },
      { text: "Which planet is known as the Red Planet?", options: ["Venus", "Jupiter", "Mars", "Saturn"], answer: 2 },
      { text: "How many continents are there on Earth?", options: ["5", "6", "7", "8"], answer: 2 },
      { text: "Which is the largest ocean?", options: ["Atlantic", "Indian", "Arctic", "Pacific"], answer: 3 },
      { text: "Who painted the Mona Lisa?", options: ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Claude Monet"], answer: 0 }
    ]
  },
  {
    id: "math-101",
    theme: "math",
    title: "Basic Maths",
    description: "Quick arithmetic and number sense questions.",
    minutes: 10,
    questions: [
      { text: "What is 12 × 8?", options: ["86", "96", "108", "92"], answer: 1 },
      { text: "What is 15% of 200?", options: ["15", "20", "30", "35"], answer: 2 },
      { text: "What is the square root of 144?", options: ["12", "14", "11", "16"], answer: 0 },
      { text: "Which number is a prime number?", options: ["21", "27", "29", "33"], answer: 2 },
      { text: "What is 3/4 written as a decimal?", options: ["0.34", "0.75", "0.43", "0.70"], answer: 1 }
    ]
  },
  {
    id: "web-101",
    theme: "web",
    title: "Web Basics",
    description: "HTML, CSS and JavaScript fundamentals for beginners.",
    minutes: 8,
    questions: [
      { text: "What does HTML stand for?", options: ["HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyperlink Text Mode Language"], answer: 0 },
      { text: "Which language is used to style web pages?", options: ["HTML", "Python", "CSS", "SQL"], answer: 2 },
      { text: "Which HTML tag makes a link?", options: ["<link>", "<a>", "<href>", "<url>"], answer: 1 },
      { text: "Which keyword declares a variable that cannot be reassigned in JavaScript?", options: ["var", "let", "const", "static"], answer: 2 },
      { text: "Which CSS property changes text colour?", options: ["font-color", "text-color", "color", "foreground"], answer: 2 }
    ]
  }
];

const PASS_MARK = 50;

// SAMPLE classmates so the leaderboard is not empty in Offline Demo Mode
const SAMPLE_CLASSMATES = [
  { name: "Aarav Mehta", average: 92, quizzes: 7 },
  { name: "Sara Khan", average: 88, quizzes: 6 },
  { name: "Liam Chen", average: 81, quizzes: 5 },
  { name: "Diya Patel", average: 76, quizzes: 8 },
  { name: "Noah Fernandes", average: 69, quizzes: 4 },
  { name: "Ishita Rao", average: 63, quizzes: 5 },
  { name: "Kabir Singh", average: 55, quizzes: 3 }
];

// Subject names used for tags and filters
const TOPIC_NAMES = { mix: "Mixed", math: "Maths", gk: "General Knowledge", web: "Web & Code" };
function themeOf(quiz) {
  return quiz.theme || { "gk-101": "gk", "math-101": "math", "web-101": "web" }[quiz.id] || "mix";
}

// Small helpers to read/write JSON in localStorage
function load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    return fallback; // saved data was broken, use the default instead
  }
}
function save(key, value) { localStorage.setItem(key, JSON.stringify(value)); }

function getQuizzes() { return load("qs_quizzes", DEMO_QUIZZES); }
function getQuiz(id) { return getQuizzes().find(function (q) { return q.id === id; }); }

function getCurrentUser() {
  const user = load("qs_user", null);
  if (!user) return null;
  // Always use the latest account name (e.g. after a demo name change)
  const account = getUsers().find(function (u) { return u.email === user.email; });
  if (account) user.name = account.name;
  return user;
}

// Demo accounts + accounts made on the Register page (demo only: saved in this browser)
// Names changed on the Profile page are kept in "qs_names" and override the saved name
function getUsers() {
  const names = load("qs_names", {});
  return DEMO_USERS.concat(load("qs_users", [])).map(function (u) {
    return names[u.email] ? Object.assign({}, u, { name: names[u.email] }) : u;
  });
}
function updateUserName(email, name) {
  const names = load("qs_names", {});
  names[email] = name;
  save("qs_names", names);
}
function registerUser(user) {
  const email = user.email.trim().toLowerCase();
  if (getUsers().some(function (u) { return u.email === email; })) return false; // email already used
  const saved = load("qs_users", []);
  saved.push({ email: email, password: user.password, role: user.role, name: user.name });
  save("qs_users", saved);
  return true;
}
function logout() { localStorage.removeItem("qs_user"); window.location.href = "login.html"; }

function login(email, password, role) {
  const user = getUsers().find(function (u) {
    return u.email === email.trim().toLowerCase() && u.password === password && u.role === role;
  });
  if (user) save("qs_user", { email: user.email, role: user.role, name: user.name });
  return user || null;
}

// Send people to login if they are not signed in
function requireUser() {
  const user = getCurrentUser();
  if (!user) window.location.href = "login.html";
  return user;
}

// Only let one role see a page; others go back to their own dashboard
function requireRole(role) {
  const user = requireUser();
  if (!user) return null;
  if (user.role !== role) {
    window.location.href = user.role === "instructor" ? "instructor-dashboard.html" : "student-dashboard.html";
    return null;
  }
  return user;
}

function saveQuiz(quiz) {
  const all = getQuizzes();
  all.push(quiz);
  save("qs_quizzes", all);
}

function getAllAttempts() { return load("qs_attempts", []); }

function getAttempts(email) {
  return load("qs_attempts", []).filter(function (a) { return a.email === email; });
}
function saveAttempt(attempt) {
  const all = load("qs_attempts", []);
  all.push(attempt);
  save("qs_attempts", all);
}

// Read "?id=..." from the page address
function getParam(name) { return new URLSearchParams(window.location.search).get(name); }

// Connect the "Log out" button if the page has one
document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("logout-btn");
  if (btn) btn.addEventListener("click", logout);
});
