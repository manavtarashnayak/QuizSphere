/**
 * Quiz Assessment Platform - Student Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Ensure user is authenticated student
  const currentUser = authAPI.requireRole(['student', 'instructor']);
  if (!currentUser) return;

  setupUserInterface(currentUser);
  setupNavigation();
  await loadDashboardData(currentUser);
});

function setupUserInterface(user) {
  // Populate user profile info in sidebar
  const userNameElements = document.querySelectorAll('.user-name');
  userNameElements.forEach(el => el.textContent = user.full_name || 'Student');

  const greetingElem = document.getElementById('student-greeting');
  if (greetingElem) {
    greetingElem.textContent = `Welcome back, ${user.full_name?.split(' ')[0] || 'Student'}!`;
  }

  const avatarElements = document.querySelectorAll('.user-avatar');
  avatarElements.forEach(el => {
    const initials = (user.full_name || 'S')
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
    el.textContent = initials;
  });

  // Logout triggers
  const logoutButtons = document.querySelectorAll('.logout-trigger');
  logoutButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      showConfirmModal({
        title: 'Sign Out',
        message: 'Are you sure you want to sign out of your account?',
        confirmText: 'Sign Out',
        isDanger: true,
        onConfirm: () => authAPI.logout()
      });
    });
  });
}

function setupNavigation() {
  const mobileToggle = document.getElementById('mobile-menu-toggle');
  const sidebar = document.getElementById('sidebar');
  const sidebarClose = document.getElementById('sidebar-close');
  const overlay = document.getElementById('sidebar-overlay');

  if (mobileToggle && sidebar && overlay) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.add('is-open');
      overlay.classList.add('is-open');
    });

    const closeSidebar = () => {
      sidebar.classList.remove('is-open');
      overlay.classList.remove('is-open');
    };

    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    overlay.addEventListener('click', closeSidebar);
  }
}

async function loadDashboardData(user) {
  const availableContainer = document.getElementById('available-quizzes-list');
  const recentAttemptsContainer = document.getElementById('recent-attempts-list');

  try {
    const [quizzes, history] = await Promise.all([
      quizAPI.getAll(),
      attemptAPI.getHistory()
    ]);

    // Compute Summary Stats
    const totalAvailable = quizzes.length;
    const totalAttempted = history.length;
    const completedCount = history.filter(h => h.completed_at).length;
    
    let avgScore = 0;
    if (history.length > 0) {
      const sumPercentage = history.reduce((acc, curr) => acc + (curr.percentage || 0), 0);
      avgScore = Math.round(sumPercentage / history.length);
    }

    // Render Stats
    document.getElementById('stat-available-count').textContent = totalAvailable;
    document.getElementById('stat-attempted-count').textContent = totalAttempted;
    document.getElementById('stat-avg-score').textContent = `${avgScore}%`;
    document.getElementById('stat-completed-count').textContent = completedCount;

    // Render Available Quizzes
    renderAvailableQuizzes(quizzes, availableContainer);

    // Render Recent Attempts
    renderRecentAttempts(history.slice(0, 5), recentAttemptsContainer);

  } catch (error) {
    console.error('Failed to load dashboard:', error);
    showToast('Failed to load dashboard statistics.', 'error');
  }
}

function renderAvailableQuizzes(quizzes, container) {
  if (!container) return;

  if (!quizzes || quizzes.length === 0) {
    container.innerHTML = `
      <div class="card empty-state" style="grid-column: 1 / -1;">
        <div class="empty-state-icon">
          <svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        </div>
        <h4 class="empty-state-title">No Quizzes Available</h4>
        <p class="empty-state-text">Your instructors haven't published any quizzes yet. Please check back later.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = quizzes.map(quiz => `
    <div class="quiz-card">
      <div class="quiz-card-header">
        <h3 class="quiz-card-title">${escapeHTML(quiz.title)}</h3>
        <span class="badge ${getDifficultyBadgeClass(quiz.difficulty)}">${escapeHTML(quiz.difficulty || 'General')}</span>
      </div>
      <p class="quiz-card-desc">${escapeHTML(quiz.description || 'No description provided.')}</p>
      
      <div class="quiz-card-meta">
        <div class="meta-item" title="Question Count">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span>${quiz.question_count || (quiz.questions ? quiz.questions.length : 0)} Questions</span>
        </div>
        <div class="meta-item" title="Duration">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6l4 2"/></svg>
          <span>${quiz.duration_minutes} Mins</span>
        </div>
      </div>

      <div class="quiz-card-footer">
        <span class="badge badge-indigo">${escapeHTML(quiz.category || 'General')}</span>
        <a href="take-quiz.html?id=${quiz.id}" class="btn btn-primary btn-sm">
          <span>Start Quiz</span>
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        </a>
      </div>
    </div>
  `).join('');
}

function renderRecentAttempts(attempts, container) {
  if (!container) return;

  if (!attempts || attempts.length === 0) {
    container.innerHTML = `
      <div class="card empty-state">
        <div class="empty-state-icon">
          <svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <h4 class="empty-state-title">No Recent Attempts</h4>
        <p class="empty-state-text">You haven't attempted any assessments yet. Choose an available quiz above to get started!</p>
        <a href="quiz-list.html" class="btn btn-secondary btn-sm">Browse Available Quizzes</a>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Quiz Title</th>
            <th>Date Attempted</th>
            <th>Score</th>
            <th>Percentage</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${attempts.map(att => `
            <tr>
              <td><strong>${escapeHTML(att.quiz_title)}</strong></td>
              <td>${formatDate(att.completed_at || att.started_at)}</td>
              <td>${att.score} / ${att.total_questions}</td>
              <td><strong>${att.percentage}%</strong></td>
              <td>
                <span class="badge ${att.passed ? 'badge-success' : 'badge-danger'}">
                  ${att.passed ? 'Passed' : 'Needs Improvement'}
                </span>
              </td>
              <td>
                <a href="results.html?attemptId=${att.id}" class="btn btn-secondary btn-sm">
                  View Result
                </a>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function getDifficultyBadgeClass(difficulty) {
  switch ((difficulty || '').toLowerCase()) {
    case 'beginner': return 'badge-success';
    case 'intermediate': return 'badge-indigo';
    case 'advanced': return 'badge-danger';
    default: return 'badge-neutral';
  }
}

function formatDate(isoString) {
  if (!isoString) return 'Recent';
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return 'Recent';
  }
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}
