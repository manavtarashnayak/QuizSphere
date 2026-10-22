/**
 * Quiz Assessment Platform - Unified API Service
 * 
 * Provides HTTP client for FastAPI backend with robust demo fallback,
 * token management, and standardized request/response handling.
 */

// Global State for Connection Mode
const API_STATE = {
  isDemoMode: false,
  checkedHealth: false
};

// ==========================================================================
// Demo Data Store (Offline Simulation for FastAPI Backend)
// ==========================================================================
const DEFAULT_DEMO_DB = {
  users: [
    {
      id: "u_student_1",
      full_name: "Alex Johnson",
      email: "student@college.edu",
      role: "student",
      password: "student123"
    },
    {
      id: "u_instructor_1",
      full_name: "Prof. Sarah Miller",
      email: "instructor@college.edu",
      role: "instructor",
      password: "instructor123"
    }
  ],
  quizzes: [
    {
      id: "q_1",
      title: "Data Structures & Algorithms Assessment",
      description: "Test your fundamental knowledge of trees, graphs, sorting algorithms, and asymptotic complexity analysis.",
      category: "Computer Science",
      difficulty: "Intermediate",
      duration_minutes: 15,
      passing_score_percentage: 60,
      instructor_id: "u_instructor_1",
      instructor_name: "Prof. Sarah Miller",
      created_at: "2026-10-15T10:00:00Z",
      // Server-side authoritative questions (including answers)
      questions: [
        {
          id: "q1_1",
          text: "What is the worst-case time complexity of QuickSort?",
          options: ["O(n log n)", "O(n²)", "O(log n)", "O(n)"],
          correct_option: 1, // 0-indexed: O(n²)
          explanation: "In the worst case when the pivot chosen is always the smallest or largest element, QuickSort degrades to O(n²)."
        },
        {
          id: "q1_2",
          text: "Which data structure follows the LIFO (Last In, First Out) principle?",
          options: ["Queue", "Priority Queue", "Stack", "Binary Search Tree"],
          correct_option: 2,
          explanation: "A Stack follows the Last In First Out order for insertions and deletions."
        },
        {
          id: "q1_3",
          text: "What is the average time complexity to search for an element in a balanced Binary Search Tree (AVL or Red-Black)?",
          options: ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
          correct_option: 1,
          explanation: "In a balanced BST, tree height is log(n), making search operations O(log n)."
        },
        {
          id: "q1_4",
          text: "Which algorithm is used to find the shortest path in a weighted graph with non-negative edge weights?",
          options: ["Dijkstra's Algorithm", "Kruskal's Algorithm", "Prim's Algorithm", "Depth First Search"],
          correct_option: 0,
          explanation: "Dijkstra's algorithm efficiently computes single-source shortest paths in weighted graphs with non-negative weights."
        },
        {
          id: "q1_5",
          text: "What data structure is typically used to implement Breadth-First Search (BFS)?",
          options: ["Stack", "Queue", "Heap", "Hash Map"],
          correct_option: 1,
          explanation: "BFS explores nodes level by level using a FIFO Queue."
        }
      ]
    },
    {
      id: "q_2",
      title: "Database Management & SQL Systems",
      description: "Assess understanding of relational database design, ACID properties, normalization, and SQL query optimizations.",
      category: "Databases",
      difficulty: "Advanced",
      duration_minutes: 20,
      passing_score_percentage: 70,
      instructor_id: "u_instructor_1",
      instructor_name: "Prof. Sarah Miller",
      created_at: "2026-10-18T14:30:00Z",
      questions: [
        {
          id: "q2_1",
          text: "Which normal form deals with eliminating transitive dependencies?",
          options: ["First Normal Form (1NF)", "Second Normal Form (2NF)", "Third Normal Form (3NF)", "Boyce-Codd Normal Form (BCNF)"],
          correct_option: 2,
          explanation: "3NF requires a relation to be in 2NF and have no transitive functional dependencies of non-prime attributes on candidate keys."
        },
        {
          id: "q2_2",
          text: "In ACID properties, what does 'I' stand for?",
          options: ["Integrity", "Iteration", "Isolation", "Indexing"],
          correct_option: 2,
          explanation: "Isolation ensures concurrent transactions execute without interfering with one another."
        },
        {
          id: "q2_3",
          text: "Which SQL clause is used to filter groups created by the GROUP BY statement?",
          options: ["WHERE", "HAVING", "FILTER", "ORDER BY"],
          correct_option: 1,
          explanation: "HAVING filters aggregated groups, whereas WHERE filters individual rows before grouping."
        },
        {
          id: "q2_4",
          text: "What type of JOIN returns all records when there is a match in either the left or the right table?",
          options: ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"],
          correct_option: 3,
          explanation: "FULL OUTER JOIN combines the results of both LEFT and RIGHT outer joins."
        }
      ]
    },
    {
      id: "q_3",
      title: "Web Technologies & Modern JavaScript",
      description: "Fundamentals of DOM manipulation, asynchronous programming, HTTP/REST, and modern frontend concepts.",
      category: "Web Development",
      difficulty: "Beginner",
      duration_minutes: 10,
      passing_score_percentage: 50,
      instructor_id: "u_instructor_1",
      instructor_name: "Prof. Sarah Miller",
      created_at: "2026-10-20T09:15:00Z",
      questions: [
        {
          id: "q3_1",
          text: "Which method is used to add a single class to a DOM element in JavaScript?",
          options: ["element.classes.add()", "element.classList.add()", "element.addClass()", "element.className.push()"],
          correct_option: 1,
          explanation: "The standard DOM API is `element.classList.add('className')`."
        },
        {
          id: "q3_2",
          text: "What will `typeof NaN` evaluate to in JavaScript?",
          options: ["'number'", "'undefined'", "'NaN'", "'object'"],
          correct_option: 0,
          explanation: "In JavaScript specifications, NaN is of type 'number'."
        },
        {
          id: "q3_3",
          text: "Which HTTP status code signifies that a resource was successfully created on the server?",
          options: ["200 OK", "201 Created", "204 No Content", "304 Not Modified"],
          correct_option: 1,
          explanation: "HTTP 201 Created is the standard response code for successful POST creation."
        }
      ]
    }
  ],
  attempts: [
    {
      id: "att_1",
      user_id: "u_student_1",
      quiz_id: "q_1",
      quiz_title: "Data Structures & Algorithms Assessment",
      started_at: "2026-10-19T11:00:00Z",
      completed_at: "2026-10-19T11:12:30Z",
      time_taken_seconds: 750,
      total_questions: 5,
      correct_answers: 4,
      incorrect_answers: 1,
      unanswered: 0,
      score: 4,
      percentage: 80,
      passed: true,
      user_answers: {
        "q1_1": 1,
        "q1_2": 2,
        "q1_3": 1,
        "q1_4": 0,
        "q1_5": 0 // incorrect (stack chosen instead of queue)
      }
    }
  ]
};

function getDemoStore() {
  const stored = localStorage.getItem(CONFIG.STORAGE_KEYS.DEMO_STORE);
  if (!stored) {
    localStorage.setItem(CONFIG.STORAGE_KEYS.DEMO_STORE, JSON.stringify(DEFAULT_DEMO_DB));
    return DEFAULT_DEMO_DB;
  }
  try {
    return JSON.parse(stored);
  } catch (e) {
    return DEFAULT_DEMO_DB;
  }
}

function saveDemoStore(data) {
  localStorage.setItem(CONFIG.STORAGE_KEYS.DEMO_STORE, JSON.stringify(data));
}

// ==========================================================================
// Authentication Token Helpers
// ==========================================================================
const tokenStorage = {
  getToken() {
    return localStorage.getItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN) || 
           sessionStorage.getItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
  },
  setToken(token, remember = true) {
    if (remember) {
      localStorage.setItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN, token);
    } else {
      sessionStorage.setItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN, token);
    }
  },
  getUser() {
    const raw = localStorage.getItem(CONFIG.STORAGE_KEYS.AUTH_USER) || 
                sessionStorage.getItem(CONFIG.STORAGE_KEYS.AUTH_USER);
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  setUser(user, remember = true) {
    const str = JSON.stringify(user);
    if (remember) {
      localStorage.setItem(CONFIG.STORAGE_KEYS.AUTH_USER, str);
    } else {
      sessionStorage.setItem(CONFIG.STORAGE_KEYS.AUTH_USER, str);
    }
  },
  clear() {
    localStorage.removeItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
    localStorage.removeItem(CONFIG.STORAGE_KEYS.AUTH_USER);
    sessionStorage.removeItem(CONFIG.STORAGE_KEYS.AUTH_TOKEN);
    sessionStorage.removeItem(CONFIG.STORAGE_KEYS.AUTH_USER);
  }
};

// ==========================================================================
// Base HTTP Client with Automatic Health Checking
// ==========================================================================
async function checkBackendHealth() {
  if (CONFIG.MODE === 'demo') {
    API_STATE.isDemoMode = true;
    API_STATE.checkedHealth = true;
    updateModeIndicator();
    return false;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1200);
    const res = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.HEALTH}`, {
      method: 'GET',
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (res.ok) {
      API_STATE.isDemoMode = false;
      API_STATE.checkedHealth = true;
      updateModeIndicator();
      return true;
    }
  } catch (err) {
    // Backend unreachable
  }

  if (CONFIG.MODE === 'auto') {
    API_STATE.isDemoMode = true;
  }
  API_STATE.checkedHealth = true;
  updateModeIndicator();
  return !API_STATE.isDemoMode;
}

function updateModeIndicator() {
  const container = document.getElementById('api-status-badge');
  if (!container) return;

  if (API_STATE.isDemoMode) {
    container.innerHTML = `
      <span class="demo-badge-indicator" title="FastAPI backend is offline. Running in Demo Mock Mode with full local functionality.">
        <span class="demo-dot"></span> Demo Mode
      </span>
    `;
  } else {
    container.innerHTML = `
      <span class="badge badge-success" title="Connected to FastAPI backend at ${CONFIG.API_BASE_URL}">
        ● Connected
      </span>
    `;
  }
}

async function request(endpoint, options = {}) {
  // Check health on first call
  if (!API_STATE.checkedHealth) {
    await checkBackendHealth();
  }

  // If in demo mode, route to demo handler
  if (API_STATE.isDemoMode) {
    return handleDemoRequest(endpoint, options);
  }

  const url = `${CONFIG.API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = tokenStorage.getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers
  };

  try {
    const response = await fetch(url, config);

    if (response.status === 401) {
      // Unauthorized: clear token and redirect to login
      tokenStorage.clear();
      if (!window.location.pathname.includes('login.html') && !window.location.pathname.includes('register.html')) {
        window.location.href = 'login.html?expired=1';
      }
      throw new Error('Session expired. Please log in again.');
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMsg = data.detail || data.message || `Request failed with status ${response.status}`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      // Network failed during call - if mode auto, fallback to demo mode
      if (CONFIG.MODE === 'auto') {
        API_STATE.isDemoMode = true;
        updateModeIndicator();
        showToast('Backend unavailable, switched to interactive Demo Mode.', 'warning');
        return handleDemoRequest(endpoint, options);
      }
      throw new Error(`Unable to connect to backend at ${CONFIG.API_BASE_URL}. Ensure FastAPI is running.`);
    }
    throw error;
  }
}

// ==========================================================================
// Demo Request Dispatcher (Simulates FastAPI Server Responses)
// ==========================================================================
async function handleDemoRequest(endpoint, options = {}) {
  // Artificial short delay to simulate network latency for loading states
  await new Promise(r => setTimeout(r, 200));
  const method = (options.method || 'GET').toUpperCase();
  const body = options.body ? JSON.parse(options.body) : null;
  const store = getDemoStore();

  // 1. Auth: Login
  if (endpoint === CONFIG.ENDPOINTS.LOGIN && method === 'POST') {
    const user = store.users.find(u => u.email.toLowerCase() === body.email.toLowerCase() && u.password === body.password);
    if (!user) {
      throw new Error('Invalid email or password.');
    }
    if (body.role && user.role !== body.role) {
      throw new Error(`Account exists but does not match role '${body.role}'.`);
    }
    return {
      access_token: `mock_jwt_token_${user.id}_${Date.now()}`,
      token_type: 'bearer',
      user: {
        id: user.id,
        full_name: user.full_name,
        email: user.email,
        role: user.role
      }
    };
  }

  // 2. Auth: Register
  if (endpoint === CONFIG.ENDPOINTS.REGISTER && method === 'POST') {
    const existing = store.users.find(u => u.email.toLowerCase() === body.email.toLowerCase());
    if (existing) {
      throw new Error('An account with this email address already exists.');
    }
    const newUser = {
      id: `u_${Date.now()}`,
      full_name: body.full_name,
      email: body.email,
      role: body.role || 'student',
      password: body.password
    };
    store.users.push(newUser);
    saveDemoStore(store);
    return {
      access_token: `mock_jwt_token_${newUser.id}_${Date.now()}`,
      token_type: 'bearer',
      user: {
        id: newUser.id,
        full_name: newUser.full_name,
        email: newUser.email,
        role: newUser.role
      }
    };
  }

  // 3. Auth: Current User
  if (endpoint === CONFIG.ENDPOINTS.ME && method === 'GET') {
    const currentUser = tokenStorage.getUser();
    if (!currentUser) throw new Error('Not authenticated');
    return currentUser;
  }

  // 4. Quizzes: List
  if (endpoint === CONFIG.ENDPOINTS.QUIZZES && method === 'GET') {
    // Return sanitized quiz list (without questions/answers to save bandwidth)
    return store.quizzes.map(q => ({
      id: q.id,
      title: q.title,
      description: q.description,
      category: q.category,
      difficulty: q.difficulty,
      duration_minutes: q.duration_minutes,
      question_count: q.questions.length,
      passing_score_percentage: q.passing_score_percentage,
      instructor_name: q.instructor_name,
      created_at: q.created_at
    }));
  }

  // 5. Quizzes: Create (Instructor)
  if (endpoint === CONFIG.ENDPOINTS.QUIZZES && method === 'POST') {
    const currentUser = tokenStorage.getUser() || { id: 'u_instructor_1', full_name: 'Instructor' };
    const newQuiz = {
      id: `q_${Date.now()}`,
      title: body.title,
      description: body.description || '',
      category: body.category || 'General',
      difficulty: body.difficulty || 'Intermediate',
      duration_minutes: parseInt(body.duration_minutes, 10) || 15,
      passing_score_percentage: parseInt(body.passing_score_percentage, 10) || 60,
      instructor_id: currentUser.id,
      instructor_name: currentUser.full_name,
      created_at: new Date().toISOString(),
      questions: body.questions.map((q, idx) => ({
        id: `q_${Date.now()}_${idx}`,
        text: q.text,
        options: q.options,
        correct_option: parseInt(q.correct_option, 10),
        explanation: q.explanation || ''
      }))
    };
    store.quizzes.unshift(newQuiz);
    saveDemoStore(store);
    return newQuiz;
  }

  // 6. Quizzes: Delete
  if (endpoint.startsWith('/api/quizzes/') && method === 'DELETE') {
    const quizId = endpoint.split('/')[3];
    store.quizzes = store.quizzes.filter(q => q.id !== quizId);
    saveDemoStore(store);
    return { success: true, message: 'Quiz deleted successfully' };
  }

  // 7. Quizzes: Details / Questions for active test (SECURITY: Never send correct answers to frontend!)
  if (endpoint.includes('/questions') && method === 'GET') {
    const parts = endpoint.split('/');
    const quizId = parts[3];
    const quiz = store.quizzes.find(q => q.id === quizId);
    if (!quiz) throw new Error('Quiz not found');

    return {
      quiz_id: quiz.id,
      title: quiz.title,
      duration_minutes: quiz.duration_minutes,
      total_questions: quiz.questions.length,
      // Sanitized questions sent to test-taker:
      questions: quiz.questions.map(q => ({
        id: q.id,
        text: q.text,
        options: q.options
      }))
    };
  }

  // 8. Attempt: Start Quiz
  if (endpoint.includes('/start') && method === 'POST') {
    const quizId = endpoint.split('/')[3];
    const quiz = store.quizzes.find(q => q.id === quizId);
    if (!quiz) throw new Error('Quiz not found');

    const currentUser = tokenStorage.getUser() || { id: 'u_student_1' };
    const attempt = {
      attempt_id: `att_${Date.now()}`,
      quiz_id: quiz.id,
      quiz_title: quiz.title,
      duration_minutes: quiz.duration_minutes,
      user_id: currentUser.id,
      started_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + quiz.duration_minutes * 60 * 1000).toISOString()
    };
    return attempt;
  }

  // 9. Attempt: Submit Answers (Evaluated authoritative on the "server")
  if (endpoint.includes('/submit') && method === 'POST') {
    const attemptId = endpoint.split('/')[3];
    const { quiz_id, answers, time_taken_seconds } = body;
    const quiz = store.quizzes.find(q => q.id === quiz_id);
    if (!quiz) throw new Error('Quiz not found');

    const currentUser = tokenStorage.getUser() || { id: 'u_student_1' };
    let correctCount = 0;
    let incorrectCount = 0;
    let unansweredCount = 0;

    const detailedReview = quiz.questions.map(q => {
      const userChoice = answers[q.id];
      const isAnswered = userChoice !== undefined && userChoice !== null;
      const isCorrect = isAnswered && userChoice === q.correct_option;

      if (!isAnswered) unansweredCount++;
      else if (isCorrect) correctCount++;
      else incorrectCount++;

      return {
        id: q.id,
        text: q.text,
        options: q.options,
        user_choice: isAnswered ? userChoice : null,
        correct_choice: q.correct_option,
        is_correct: isCorrect,
        explanation: q.explanation || ''
      };
    });

    const totalQuestions = quiz.questions.length;
    const percentage = Math.round((correctCount / totalQuestions) * 100);
    const passed = percentage >= quiz.passing_score_percentage;

    const resultRecord = {
      id: attemptId,
      user_id: currentUser.id,
      quiz_id: quiz.id,
      quiz_title: quiz.title,
      started_at: new Date(Date.now() - (time_taken_seconds || 60) * 1000).toISOString(),
      completed_at: new Date().toISOString(),
      time_taken_seconds: time_taken_seconds || 0,
      total_questions: totalQuestions,
      correct_answers: correctCount,
      incorrect_answers: incorrectCount,
      unanswered: unansweredCount,
      score: correctCount,
      percentage,
      passed,
      detailed_review: detailedReview
    };

    store.attempts.unshift(resultRecord);
    saveDemoStore(store);

    return resultRecord;
  }

  // 10. Attempt: Get Result
  if (endpoint.includes('/result') && method === 'GET') {
    const attemptId = endpoint.split('/')[3];
    const record = store.attempts.find(a => a.id === attemptId);
    if (!record) throw new Error('Attempt result not found');
    return record;
  }

  // 11. Student History
  if (endpoint === CONFIG.ENDPOINTS.STUDENT_HISTORY && method === 'GET') {
    const currentUser = tokenStorage.getUser();
    if (!currentUser) return [];
    return store.attempts.filter(a => a.user_id === currentUser.id);
  }

  // 12. Instructor Results
  if (endpoint.includes('/results') && method === 'GET') {
    const quizId = endpoint.split('/')[3];
    return store.attempts.filter(a => a.quiz_id === quizId);
  }

  throw new Error(`Endpoint '${endpoint}' not implemented in demo simulator.`);
}

// ==========================================================================
// Specialized API Services
// ==========================================================================
const authAPI = {
  async login(email, password, role) {
    const data = await request(CONFIG.ENDPOINTS.LOGIN, {
      method: 'POST',
      body: JSON.stringify({ email, password, role })
    });
    if (data.access_token) {
      tokenStorage.setToken(data.access_token);
      tokenStorage.setUser(data.user);
    }
    return data;
  },

  async register(fullName, email, password, role) {
    const data = await request(CONFIG.ENDPOINTS.REGISTER, {
      method: 'POST',
      body: JSON.stringify({
        full_name: fullName,
        email,
        password,
        role
      })
    });
    if (data.access_token) {
      tokenStorage.setToken(data.access_token);
      tokenStorage.setUser(data.user);
    }
    return data;
  },

  async getCurrentUser() {
    return tokenStorage.getUser();
  },

  logout() {
    tokenStorage.clear();
    window.location.href = 'login.html';
  },

  isAuthenticated() {
    return !!tokenStorage.getToken() && !!tokenStorage.getUser();
  },

  requireRole(allowedRoles = ['student', 'instructor']) {
    const user = tokenStorage.getUser();
    if (!user || !tokenStorage.getToken()) {
      window.location.href = 'login.html';
      return null;
    }
    if (!allowedRoles.includes(user.role)) {
      if (user.role === 'student') {
        window.location.href = 'student-dashboard.html';
      } else {
        window.location.href = 'instructor-dashboard.html';
      }
      return null;
    }
    return user;
  }
};

const quizAPI = {
  async getAll() {
    return request(CONFIG.ENDPOINTS.QUIZZES);
  },

  async getQuestionsForAttempt(quizId) {
    return request(CONFIG.ENDPOINTS.QUIZ_QUESTIONS(quizId));
  },

  async create(quizData) {
    return request(CONFIG.ENDPOINTS.QUIZZES, {
      method: 'POST',
      body: JSON.stringify(quizData)
    });
  },

  async delete(quizId) {
    return request(CONFIG.ENDPOINTS.QUIZ_DETAIL(quizId), {
      method: 'DELETE'
    });
  }
};

const attemptAPI = {
  async start(quizId) {
    return request(CONFIG.ENDPOINTS.ATTEMPT_START(quizId), {
      method: 'POST'
    });
  },

  async submit(attemptId, quizId, answers, timeTakenSeconds) {
    return request(CONFIG.ENDPOINTS.ATTEMPT_SUBMIT(attemptId), {
      method: 'POST',
      body: JSON.stringify({
        quiz_id: quizId,
        answers,
        time_taken_seconds: timeTakenSeconds
      })
    });
  },

  async getResult(attemptId) {
    return request(CONFIG.ENDPOINTS.ATTEMPT_RESULT(attemptId));
  },

  async getHistory() {
    return request(CONFIG.ENDPOINTS.STUDENT_HISTORY);
  },

  async getQuizResultsForInstructor(quizId) {
    return request(CONFIG.ENDPOINTS.INSTRUCTOR_RESULTS(quizId));
  }
};

// ==========================================================================
// Global UI Utilities (Toast & Modal)
// ==========================================================================
function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconSvg = {
    success: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>`,
    error: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 9l-6 6M9 9l6 6"/></svg>`,
    warning: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`,
    info: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 16v-4m0-4h.01"/></svg>`
  }[type] || '';

  toast.innerHTML = `
    <span style="color: inherit; display:flex;">${iconSvg}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

function showConfirmModal({ title, message, confirmText = 'Confirm', cancelText = 'Cancel', isDanger = false, onConfirm }) {
  let modalBackdrop = document.getElementById('global-confirm-modal');
  if (!modalBackdrop) {
    modalBackdrop = document.createElement('div');
    modalBackdrop.id = 'global-confirm-modal';
    modalBackdrop.className = 'modal-backdrop';
    document.body.appendChild(modalBackdrop);
  }

  modalBackdrop.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h3>${title}</h3>
        <button class="btn-icon" id="modal-close-icon">
          <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <p>${message}</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="modal-cancel-btn">${cancelText}</button>
        <button class="btn ${isDanger ? 'btn-danger' : 'btn-primary'}" id="modal-confirm-btn">${confirmText}</button>
      </div>
    </div>
  `;

  function closeModal() {
    modalBackdrop.classList.remove('is-active');
  }

  modalBackdrop.classList.add('is-active');

  modalBackdrop.querySelector('#modal-close-icon').onclick = closeModal;
  modalBackdrop.querySelector('#modal-cancel-btn').onclick = closeModal;
  modalBackdrop.querySelector('#modal-confirm-btn').onclick = () => {
    closeModal();
    if (typeof onConfirm === 'function') onConfirm();
  };
}

// Auto-run health check on load
document.addEventListener('DOMContentLoaded', () => {
  checkBackendHealth();
});
