// Central API Client connecting frontend to FastAPI backend with graceful Offline fallback

const API_BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://127.0.0.1:8000/api"
  : "/api"; // In production on Vercel

const ApiClient = {
  // Check if live backend server is reachable
  async checkConnection() {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        const data = await res.json();
        return data.status === "ok";
      }
      return false;
    } catch (e) {
      return false;
    }
  },

  // Auth: Login
  async login(email, password, role) {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, role })
      });
      if (!res.ok) throw new Error("Invalid credentials");
      const data = await res.json();
      localStorage.setItem("qs_token", data.access_token);
      localStorage.setItem("qs_user", JSON.stringify({
        id: data.user.id,
        email: data.user.email,
        name: data.user.full_name,
        role: data.user.role
      }));
      return data.user;
    } catch (err) {
      console.warn("Backend login failed or unreachable, falling back to local auth:", err);
      return null;
    }
  },

  // Auth: Register
  async register(full_name, email, password, role) {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ full_name, email, password, role })
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Registration failed");
      }
      const data = await res.json();
      localStorage.setItem("qs_token", data.access_token);
      localStorage.setItem("qs_user", JSON.stringify({
        id: data.user.id,
        email: data.user.email,
        name: data.user.full_name,
        role: data.user.role
      }));
      return data.user;
    } catch (err) {
      console.warn("Backend register failed, falling back to local:", err);
      return null;
    }
  },

  // Quizzes: Fetch all live published quizzes
  async getQuizzes() {
    try {
      const res = await fetch(`${API_BASE_URL}/quizzes`, { signal: AbortSignal.timeout(3000) });
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      return null;
    }
  },

  // Leaderboard: Fetch live leaderboard
  async getLeaderboard() {
    try {
      const res = await fetch(`${API_BASE_URL}/leaderboard`, { signal: AbortSignal.timeout(3000) });
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      return null;
    }
  }
};

// Auto update status badge on all pages
document.addEventListener("DOMContentLoaded", async function () {
  const badges = document.querySelectorAll(".badge, .site-footer .container");
  const isOnline = await ApiClient.checkConnection();

  badges.forEach(b => {
    if (b.textContent.includes("Offline Demo Mode") || b.id === "connection-status-badge") {
      if (isOnline) {
        b.innerHTML = '<span style="color:#10b981">● Live Server Connected</span>';
        b.style.borderColor = "#10b981";
      } else {
        b.innerHTML = '<span style="color:#f59e0b">● Offline Demo Mode</span>';
      }
    }
  });
});
