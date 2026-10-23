// OFFLINE DEMO MODE: sample users, quizzes and scores saved in the browser (localStorage).
// Connects to local mock data and supports CBSE 11th & 12th + CS & Web subjects.

const DEMO_USERS = [
  { email: "student@college.edu", password: "student123", role: "student", name: "Demo Student" },
  { email: "instructor@college.edu", password: "instructor123", role: "instructor", name: "Demo Instructor" }
];

const DEMO_QUIZZES = [
  {
    id: "phys-101",
    theme: "phys",
    title: "CBSE Physics (Classes 11 & 12)",
    description: "Mechanics, Thermodynamics, Electrostatics, Gauss's Law, and Wave Optics.",
    minutes: 20,
    questions: [
      { text: "What is the dimensional formula of Universal Gravitational Constant (G)?", options: ["[M⁻¹ L³ T⁻²]", "[M¹ L² T⁻²]", "[M⁻¹ L² T⁻¹]", "[M⁰ L³ T⁻²]"], answer: 0 },
      { text: "In projectile motion under gravity, which component of velocity remains constant?", options: ["Vertical component", "Horizontal component", "Both", "Neither"], answer: 1 },
      { text: "According to the First Law of Thermodynamics, ΔQ is equal to:", options: ["ΔU - W", "ΔU + W", "W - ΔU", "ΔU * W"], answer: 1 },
      { text: "What is the electric field inside a charged thin spherical conducting shell?", options: ["Zero", "q / (4πε₀ R²)", "q / (4πε₀ r)", "Infinite"], answer: 0 },
      { text: "Which phenomenon demonstrates the transverse wave nature of light?", options: ["Interference", "Diffraction", "Polarization", "Refraction"], answer: 2 },
      { text: "The SI unit of magnetic flux is:", options: ["Tesla", "Weber", "Henry", "Gauss"], answer: 1 },
      { text: "In Young's Double Slit Experiment, what happens to fringe width if slit separation is halved?", options: ["Halved", "Doubled", "Remains unchanged", "Quadrupled"], answer: 1 },
      { text: "What is the de Broglie wavelength for an electron accelerated through V volts?", options: ["12.27 / √V Å", "1.227 / √V Å", "122.7 / √V Å", "0.1227 / √V Å"], answer: 0 }
    ]
  },
  {
    id: "chem-101",
    theme: "chem",
    title: "CBSE Chemistry (Classes 11 & 12)",
    description: "Hybridization, Chemical Equilibrium, Redox, Lucas Test, Kinetics, and Coordination.",
    minutes: 20,
    questions: [
      { text: "What is the hybridization of carbon in ethane, ethene, and ethyne respectively?", options: ["sp³, sp², sp", "sp, sp², sp³", "sp², sp³, sp", "sp³, sp, sp²"], answer: 0 },
      { text: "Increasing pressure on N₂(g) + 3H₂(g) ⇌ 2NH₃(g) at equilibrium will shift:", options: ["Forward (more NH₃)", "Backward", "No effect", "Stop reaction"], answer: 0 },
      { text: "What is the oxidation state of Chromium in K₂Cr₂O₇?", options: ["+4", "+5", "+6", "+3"], answer: 2 },
      { text: "Which reagent is used in the Lucas Test to distinguish alcohols?", options: ["Anhydrous ZnCl₂ + conc. HCl", "Alkaline KMnO₄", "Br₂ in CCl₄", "Acidified K₂Cr₂O₇"], answer: 0 },
      { text: "What is the unit of rate constant for a first-order chemical reaction?", options: ["mol L⁻¹ s⁻¹", "L mol⁻¹ s⁻¹", "s⁻¹", "mol² L⁻² s⁻¹"], answer: 2 },
      { text: "Which compound does NOT undergo the Aldol Condensation reaction?", options: ["Acetaldehyde", "Benzaldehyde", "Propanal", "Acetone"], answer: 1 },
      { text: "Lanthanoid contraction is primarily caused by:", options: ["Poor shielding effect of 4f electrons", "Strong shielding effect of 4f electrons", "Increase in nuclear charge alone", "Presence of 5d electrons"], answer: 0 }
    ]
  },
  {
    id: "math-cbse-101",
    theme: "math",
    title: "CBSE Mathematics (Classes 11 & 12)",
    description: "Calculus, Derivatives, Definite Integrals, Matrices, Probability, and Vectors.",
    minutes: 25,
    questions: [
      { text: "What is the derivative of e^(sin x) with respect to x?", options: ["cos(x) * e^(sin x)", "-cos(x) * e^(sin x)", "sin(x) * e^(cos x)", "e^(cos x)"], answer: 0 },
      { text: "What is the value of ∫₀^(π/2) sin²(x) dx?", options: ["π/2", "π/4", "1", "0"], answer: 1 },
      { text: "If A is an invertible square matrix of order n, what is det(adj A)?", options: ["(det A)^n", "(det A)^(n - 1)", "n * det A", "1 / det A"], answer: 1 },
      { text: "If independent events A, B have P(A) = 0.3, P(B) = 0.4, what is P(A ∩ B)?", options: ["0.7", "0.12", "0.1", "0.58"], answer: 1 },
      { text: "What is the dot product of two mutually perpendicular non-zero vectors?", options: ["1", "-1", "0", "Product of magnitudes"], answer: 2 },
      { text: "The number of subsets of a set having 5 elements is:", options: ["10", "25", "32", "64"], answer: 2 },
      { text: "What is the value of lim(x -> 0) [sin(x) / x]?", options: ["0", "1", "Undefined", "Infinity"], answer: 1 }
    ]
  },
  {
    id: "cs-prog-101",
    theme: "prog",
    title: "Basic Programming & Python (CBSE CS)",
    description: "Python data types, operators, functions, lists, and SQL query basics.",
    minutes: 15,
    questions: [
      { text: "What is the output of print(type([1, 2, 3])) in Python?", options: ["<class 'tuple'>", "<class 'list'>", "<class 'array'>", "<class 'set'>"], answer: 1 },
      { text: "Which data type in Python is IMMUTABLE?", options: ["List", "Dictionary", "Tuple", "Set"], answer: 2 },
      { text: "What is the output of: print('Hello' * 3)?", options: ["Hello Hello Hello", "Hello*3", "HelloHelloHello", "TypeError"], answer: 2 },
      { text: "What is the result of 2 ** 3 ** 2 in Python?", options: ["64", "512", "36", "12"], answer: 1 },
      { text: "Which keyword is used to define a function in Python?", options: ["function", "def", "fun", "define"], answer: 1 },
      { text: "In SQL, which clause filters records aggregated by GROUP BY?", options: ["WHERE", "HAVING", "ORDER BY", "FILTER"], answer: 1 },
      { text: "What will list(range(2, 10, 3)) produce in Python?", options: ["[2, 5, 8]", "[2, 5, 8, 10]", "[3, 6, 9]", "[2, 3, 4]"], answer: 0 },
      { text: "What does a Boolean expression evaluate to in programming?", options: ["Any integer", "True or False", "A string", "Null"], answer: 1 }
    ]
  },
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
const TOPIC_NAMES = {
  mix: "All Subjects",
  phys: "Physics",
  chem: "Chemistry",
  math: "Maths",
  prog: "Programming",
  gk: "General Knowledge",
  web: "Web & Code"
};

function themeOf(quiz) {
  return quiz.theme || {
    "phys-101": "phys",
    "chem-101": "chem",
    "math-cbse-101": "math",
    "cs-prog-101": "prog",
    "gk-101": "gk",
    "math-101": "math",
    "web-101": "web"
  }[quiz.id] || "mix";
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
  const order = ["phys", "chem", "math", "prog", "gk", "web", "mix"];
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

// LocalStorage helpers
function load(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    return fallback;
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
  const account = getUsers().find(function (u) { return u.email === user.email; });
  if (account) user.name = account.name;
  return user;
}

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
  if (getUsers().some(function (u) { return u.email === email; })) return false;
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

function requireUser() {
  const user = getCurrentUser();
  if (!user) window.location.href = "login.html";
  return user;
}

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

function getParam(name) { return new URLSearchParams(window.location.search).get(name); }

document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("logout-btn");
  if (btn) btn.addEventListener("click", logout);
});
