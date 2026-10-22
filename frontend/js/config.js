/**
 * Quiz Assessment Platform - Global Configuration
 * 
 * Configure backend API base URL and runtime settings.
 */

const CONFIG = {
  // Backend FastAPI base URL
  API_BASE_URL: 'http://127.0.0.1:8000',
  
  // Timeout for API requests in milliseconds
  REQUEST_TIMEOUT: 6000,

  // App operating mode:
  // 'auto': tests FastAPI backend connection, automatically falls back to Demo Mode if server is offline
  // 'real': strictly communicates with FastAPI backend, shows connection error if offline
  // 'demo': offline interactive demo mode with realistic mock data
  MODE: 'auto',

  // Local storage keys
  STORAGE_KEYS: {
    AUTH_TOKEN: 'qap_auth_token',
    AUTH_USER: 'qap_auth_user',
    REMEMBER_ME: 'qap_remember_me',
    DEMO_STORE: 'qap_demo_database',
    ACTIVE_ATTEMPT: 'qap_active_attempt'
  },

  // API Endpoints
  ENDPOINTS: {
    HEALTH: '/api/health',
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    ME: '/api/auth/me',
    QUIZZES: '/api/quizzes',
    QUIZ_DETAIL: (id) => `/api/quizzes/${id}`,
    QUIZ_QUESTIONS: (id) => `/api/quizzes/${id}/questions`,
    ATTEMPT_START: (id) => `/api/quizzes/${id}/start`,
    ATTEMPT_SUBMIT: (id) => `/api/attempts/${id}/submit`,
    ATTEMPT_RESULT: (id) => `/api/attempts/${id}/result`,
    STUDENT_HISTORY: '/api/attempts/history',
    INSTRUCTOR_RESULTS: (id) => `/api/quizzes/${id}/results`
  }
};

// Freeze configuration to prevent accidental modification
Object.freeze(CONFIG);
