/* global requireUser, getAllAttempts, getUsers, SAMPLE_CLASSMATES */
// Leaderboard: real students from this browser + sample classmates, ranked by average score
const me = requireUser();

if (me) {
  if (me.role === "instructor") {
    document.getElementById("nav-dashboard").href = "instructor-dashboard.html";
    document.getElementById("nav-history-item").remove(); // History is for students
  }

  // 1. Group real attempts by student email
  const byEmail = {};
  getAllAttempts().forEach(function (a) {
    if (!byEmail[a.email]) byEmail[a.email] = [];
    byEmail[a.email].push(a.percent);
  });
  const users = getUsers();
  const real = Object.keys(byEmail).map(function (email) {
    const scores = byEmail[email];
    const account = users.find(function (u) { return u.email === email; });
    return {
      name: account ? account.name : email,
      average: Math.round(scores.reduce(function (s, p) { return s + p; }, 0) / scores.length),
      quizzes: scores.length,
      isMe: email === me.email
    };
  });
  // A student with no attempts yet still appears (0%), so they can see where they start
  if (me.role === "student" && !byEmail[me.email]) {
    real.push({ name: me.name, average: 0, quizzes: 0, isMe: true });
  }

  // 2. Mix in sample classmates and sort: highest average first, then most quizzes
  const ranking = real.concat(SAMPLE_CLASSMATES.map(function (c) {
    return { name: c.name, average: c.average, quizzes: c.quizzes, sample: true };
  })).sort(function (a, b) { return b.average - a.average || b.quizzes - a.quizzes; });

  function initials(name) {
    return name.split(/\s+/).map(function (w) { return w.charAt(0); }).join("").slice(0, 2).toUpperCase();
  }
  function nameWithTags(el, person) {
    el.textContent = person.name;
    if (person.isMe) el.insertAdjacentHTML("beforeend", '<span class="tag tag-you">You</span>');
    if (person.sample) el.insertAdjacentHTML("beforeend", '<span class="tag tag-sample">sample</span>');
  }

  // 3. Podium: show 2nd, 1st, 3rd so the winner stands in the middle
  const podium = document.getElementById("podium");
  const medals = [
    { index: 1, cls: "silver", label: "2" },
    { index: 0, cls: "gold first", label: "1" },
    { index: 2, cls: "bronze", label: "3" }
  ];
  medals.forEach(function (m) {
    const person = ranking[m.index];
    if (!person) return;
    const spot = document.createElement("li");
    spot.className = "podium-spot " + m.cls;
    spot.dataset.testid = "podium-rank-" + m.label;
    spot.setAttribute("aria-label", "Rank " + m.label + ": " + person.name + ", " + person.average + " percent");
    spot.innerHTML =
      '<span class="podium-avatar" aria-hidden="true"></span>' +
      '<span class="podium-name"></span>' +
      '<span class="podium-score">' + person.average + "%</span>" +
      '<span class="podium-block" aria-hidden="true">' + m.label + "</span>";
    spot.querySelector(".podium-avatar").textContent = initials(person.name);
    nameWithTags(spot.querySelector(".podium-name"), person);
    podium.appendChild(spot);
  });

  // 4. Everyone from 4th place down
  const list = document.getElementById("rank-list");
  ranking.slice(3).forEach(function (person, i) {
    const row = document.createElement("li");
    row.className = "glass rank-row" + (person.isMe ? " me" : "");
    row.dataset.testid = "rank-row-" + (i + 4);
    row.innerHTML =
      '<span class="rank-num">#' + (i + 4) + "</span>" +
      '<div><strong class="rank-name"></strong><div class="hint">' +
      (person.quizzes === 0 ? "Take a quiz to join the ranking" : person.quizzes + " quiz(zes)") + "</div>" +
      '<div class="rank-meter" aria-hidden="true"><span style="width:' + person.average + '%"></span></div></div>' +
      '<span class="rank-score">' + person.average + "%</span>";
    nameWithTags(row.querySelector(".rank-name"), person);
    list.appendChild(row);
  });
}
