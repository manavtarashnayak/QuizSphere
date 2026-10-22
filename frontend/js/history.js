/**
 * Quiz Assessment Platform - Student Attempt History Logic
 */

let historyList = [];

document.addEventListener('DOMContentLoaded', async () => {
  const currentUser = authAPI.requireRole(['student', 'instructor']);
  if (!currentUser) return;

  setupUserInterface(currentUser);
  setupNavigation();
  initSearchAndFilter();
  await loadAttemptHistory();
});

function setupUserInterface(user) {
  const userNameElements = document.querySelectorAll('.user-name');
  userNameElements.forEach(el => el.textContent = user.full_name || 'Student');

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

  const logoutButtons = document.querySelectorAll('.logout-trigger');
  logoutButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      showConfirmModal({
        title: 'Sign Out',
        message: 'Are you sure you want to sign out?',
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

async function loadAttemptHistory() {
  const tbody = document.getElementById('history-table-body');
  if (!tbody) return;

  tbody.innerHTML = `
    <tr>
      <td colspan="7" style="text-align: center; padding: 3rem 1rem;">
        <span class="spinner spinner-dark" style="width: 2rem; height: 2rem;"></span>
        <p style="margin-top: 0.75rem; color: var(--text-muted);">Retrieving your past attempts...</p>
      </td>
    </tr>
  `;

  try {
    const history = await attemptAPI.getHistory();
    historyList = history;
    renderHistoryTable(historyList);
  } catch (error) {
    console.error('Error fetching history:', error);
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; padding: 2rem; color: var(--color-rose-600);">
          Failed to load history: ${escapeHTML(error.message)}
        </td>
      </tr>
    `;
  }
}

function initSearchAndFilter() {
  const searchInput = document.getElementById('history-search');
  const statusFilter = document.getElementById('history-status-filter');

  const apply = () => {
    const query = (searchInput?.value || '').toLowerCase().trim();
    const status = statusFilter?.value || '';

    const filtered = historyList.filter(item => {
      const matchQuery = item.quiz_title.toLowerCase().includes(query);
      const matchStatus = !status || 
        (status === 'passed' && item.passed) || 
        (status === 'failed' && !item.passed);
      return matchQuery && matchStatus;
    });

    renderHistoryTable(filtered);
  };

  if (searchInput) searchInput.addEventListener('input', apply);
  if (statusFilter) statusFilter.addEventListener('change', apply);
}

function renderHistoryTable(items) {
  const tbody = document.getElementById('history-table-body');
  const countBadge = document.getElementById('history-count-badge');
  if (!tbody) return;

  if (countBadge) {
    countBadge.textContent = `${items.length} Attempt${items.length === 1 ? '' : 's'}`;
  }

  if (items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 3.5rem 1rem;">
          <div class="empty-state" style="padding: 0;">
            <div class="empty-state-icon">
              <svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
            </div>
            <h4 class="empty-state-title">No assessment attempts found</h4>
            <p class="empty-state-text">You haven't completed any quizzes matching these criteria yet.</p>
            <a href="quiz-list.html" class="btn btn-primary btn-sm">Explore Quizzes</a>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items.map(att => `
    <tr>
      <td>
        <strong>${escapeHTML(att.quiz_title)}</strong>
      </td>
      <td>${formatDateTime(att.completed_at || att.started_at)}</td>
      <td>${formatDuration(att.time_taken_seconds)}</td>
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
  `).join('');
}

function formatDateTime(isoString) {
  if (!isoString) return 'Recent';
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return 'Recent';
  }
}

function formatDuration(seconds) {
  if (!seconds || isNaN(seconds)) return '0s';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins === 0) return `${secs}s`;
  return `${mins}m ${secs}s`;
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}
