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
    minutes: 15,
    questions: [
      { text: "What is the capital city of Japan?", options: ["Seoul", "Tokyo", "Beijing", "Bangkok"], answer: 1 },
      { text: "Which planet is known as the Red Planet?", options: ["Venus", "Jupiter", "Mars", "Saturn"], answer: 2 },
      { text: "How many continents are there on Earth?", options: ["5", "6", "7", "8"], answer: 2 },
      { text: "Which is the largest ocean?", options: ["Atlantic", "Indian", "Arctic", "Pacific"], answer: 3 },
      { text: "Who painted the Mona Lisa?", options: ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Claude Monet"], answer: 0 },
      { text: "Which is the longest river in the world?", options: ["Amazon", "Nile", "Yangtze", "Ganga"], answer: 1 },
      { text: "What is the national animal of India?", options: ["Lion", "Elephant", "Bengal Tiger", "Peacock"], answer: 2 },
      { text: "Which gas do plants absorb from the air?", options: ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"], answer: 2 },
      { text: "How many days are there in a leap year?", options: ["365", "366", "364", "360"], answer: 1 },
      { text: "Which is the smallest planet in our solar system?", options: ["Mercury", "Mars", "Venus", "Pluto"], answer: 0 },
      { text: "Who wrote 'Romeo and Juliet'?", options: ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"], answer: 1 },
      { text: "What is the hardest natural substance?", options: ["Gold", "Iron", "Diamond", "Quartz"], answer: 2 },
      { text: "Which country is home to the kangaroo?", options: ["New Zealand", "South Africa", "Australia", "Brazil"], answer: 2 },
      { text: "What is the boiling point of water at sea level?", options: ["90 °C", "100 °C", "110 °C", "120 °C"], answer: 1 },
      { text: "Which is the tallest mountain in the world?", options: ["K2", "Kangchenjunga", "Mount Everest", "Lhotse"], answer: 2 }
    ]
  },
  {
    id: "math-101",
    theme: "math",
    title: "Basic Maths",
    description: "Quick arithmetic and number sense questions.",
    minutes: 15,
    questions: [
      { text: "What is 12 × 8?", options: ["86", "96", "108", "92"], answer: 1 },
      { text: "What is 15% of 200?", options: ["15", "20", "30", "35"], answer: 2 },
      { text: "What is the square root of 144?", options: ["12", "14", "11", "16"], answer: 0 },
      { text: "Which number is a prime number?", options: ["21", "27", "29", "33"], answer: 2 },
      { text: "What is 3/4 written as a decimal?", options: ["0.34", "0.75", "0.43", "0.70"], answer: 1 },
      { text: "What is 7 × 9?", options: ["56", "63", "72", "69"], answer: 1 },
      { text: "What is 25% of 80?", options: ["20", "25", "16", "40"], answer: 0 },
      { text: "What is 2 to the power of 5?", options: ["10", "25", "32", "64"], answer: 2 },
      { text: "How many sides does a hexagon have?", options: ["5", "6", "7", "8"], answer: 1 },
      { text: "What is 144 ÷ 12?", options: ["11", "12", "13", "14"], answer: 1 },
      { text: "What is the sum of angles in a triangle?", options: ["90°", "180°", "270°", "360°"], answer: 1 },
      { text: "What is 0.5 + 0.25?", options: ["0.55", "0.7", "0.75", "0.8"], answer: 2 },
      { text: "What is the next prime number after 7?", options: ["9", "10", "11", "13"], answer: 2 },
      { text: "What is the area of a square with side 6 cm?", options: ["24 cm²", "36 cm²", "12 cm²", "30 cm²"], answer: 1 },
      { text: "What is 1000 − 357?", options: ["643", "653", "743", "657"], answer: 0 }
    ]
  },
  {
    id: "web-101",
    theme: "web",
    title: "Web Basics",
    description: "HTML, CSS and JavaScript fundamentals for beginners.",
    minutes: 15,
    questions: [
      { text: "What does HTML stand for?", options: ["HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyperlink Text Mode Language"], answer: 0 },
      { text: "Which language is used to style web pages?", options: ["HTML", "Python", "CSS", "SQL"], answer: 2 },
      { text: "Which HTML tag makes a link?", options: ["<link>", "<a>", "<href>", "<url>"], answer: 1 },
      { text: "Which keyword declares a variable that cannot be reassigned in JavaScript?", options: ["var", "let", "const", "static"], answer: 2 },
      { text: "Which CSS property changes text colour?", options: ["font-color", "text-color", "color", "foreground"], answer: 2 },
      { text: "Which HTML tag is used for the largest heading?", options: ["<head>", "<h6>", "<heading>", "<h1>"], answer: 3 },
      { text: "Which HTML tag shows an image?", options: ["<img>", "<image>", "<pic>", "<src>"], answer: 0 },
      { text: "How do you write a comment in JavaScript (single line)?", options: ["<!-- -->", "//", "#", "**"], answer: 1 },
      { text: "Which CSS property sets the space inside an element's border?", options: ["margin", "spacing", "padding", "gap"], answer: 2 },
      { text: "Which method prints a message to the browser console?", options: ["console.log()", "print()", "echo()", "alert.log()"], answer: 0 },
      { text: "What does CSS stand for?", options: ["Computer Style Sheets", "Cascading Style Sheets", "Creative Style System", "Colourful Style Sheets"], answer: 1 },
      { text: "Which HTML element holds a numbered list?", options: ["<ul>", "<li>", "<ol>", "<list>"], answer: 2 },
      { text: "Which operator checks equal value AND type in JavaScript?", options: ["=", "==", "===", "!="], answer: 2 },
      { text: "Which CSS layout makes items sit in a flexible row or column?", options: ["float", "flexbox", "inline", "table"], answer: 1 },
      { text: "Which attribute gives a link its destination?", options: ["src", "link", "href", "to"], answer: 2 }
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

// ---- Test setup: subject + number of questions ----
const SECONDS_PER_QUESTION = 60; // time allowed for a subject test, per question

// Every question for one subject ("all" = every subject), gathered from all its quizzes
function getQuestionPool(subject) {
  const pool = [];
  getQuizzes().forEach(function (quiz) {
    if (subject === "all" || themeOf(quiz) === subject) {
      quiz.questions.forEach(function (q) { pool.push(q); });
    }
  });
  return pool;
}

// Subjects that actually have questions, with how many each has
function getSubjectsWithCounts() {
  const order = ["math", "gk", "web", "mix"];
  return order.map(function (key) { return { key: key, name: TOPIC_NAMES[key], count: getQuestionPool(key).length }; })
    .filter(function (s) { return s.count > 0; });
}

// Shuffle a copy of a list (Fisher–Yates)
function shuffled(list) {
  const copy = list.slice();
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const tmp = copy[i]; copy[i] = copy[j]; copy[j] = tmp;
  }
  return copy;
}

// Quick-pick sizes for the question-count picker, never more than what is available
function countPresets(max) {
  const presets = [5, 10, 15, 20, 25, 30].filter(function (n) { return n < max; });
  presets.push(max);
  return presets;
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

// Built-in demo quizzes always use the latest question bank; instructor-made quizzes come from storage
function getQuizzes() {
  const saved = load("qs_quizzes", []);
  const custom = saved.filter(function (q) {
    return !DEMO_QUIZZES.some(function (d) { return d.id === q.id; });
  });
  return DEMO_QUIZZES.concat(custom);
}
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
  const all = load("qs_quizzes", []);
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
