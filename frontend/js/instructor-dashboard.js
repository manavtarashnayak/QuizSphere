/**
 * Quiz Assessment Platform - Instructor Dashboard Logic
 */

let allQuizzes = [];

document.addEventListener('DOMContentLoaded', async () => {
  // Ensure user is authenticated instructor
  const currentUser = authAPI.requireRole(['instructor']);
  if (!currentUser) return;

  setupUserInterface(currentUser);
  setupNavigation();
  setupSearchAndFilters();
  await loadInstructorData(currentUser);
});

function setupUserInterface(user) {
  const userNameElements = document.querySelectorAll('.user-name');
  userNameElements.forEach(el => el.textContent = user.full_name || 'Instructor');

  const greetingElem = document.getElementById('instructor-greeting');
  if (greetingElem) {
    greetingElem.textContent = `Welcome, ${user.full_name || 'Instructor'}!`;
  }

  const avatarElements = document.querySelectorAll('.user-avatar');
  avatarElements.forEach(el => {
    const initials = (user.full_name || 'I')
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
        message: 'Are you sure you want to sign out of the Instructor portal?',
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

async function loadInstructorData(user) {
  try {
    const quizzes = await quizAPI.getAll();
    allQuizzes = quizzes;

    // Calculate aggregated metrics from demo/server store
    const store = (typeof getDemoStore === 'function') ? getDemoStore() : { attempts: [] };
    const allAttempts = store.attempts || [];

    const totalQuizzes = quizzes.length;
    const totalAttempts = allAttempts.length;
    let avgPerformance = 0;
    if (totalAttempts > 0) {
      const sum = allAttempts.reduce((acc, curr) => acc + (curr.percentage || 0), 0);
      avgPerformance = Math.round(sum / totalAttempts);
    }

    document.getElementById('stat-total-quizzes').textContent = totalQuizzes;
    document.getElementById('stat-total-attempts').textContent = totalAttempts;
    document.getElementById('stat-avg-performance').textContent = `${avgPerformance}%`;
    document.getElementById('stat-active-quizzes').textContent = totalQuizzes;

    renderQuizzesTable(allQuizzes);
  } catch (error) {
    console.error('Error loading instructor data:', error);
    showToast('Failed to load instructor metrics.', 'error');
  }
}

function setupSearchAndFilters() {
  const searchInput = document.getElementById('quiz-search-input');
  const categoryFilter = document.getElementById('quiz-category-filter');

  const applyFilters = () => {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const selectedCategory = categoryFilter ? categoryFilter.value : '';

    const filtered = allQuizzes.filter(quiz => {
      const matchesQuery = quiz.title.toLowerCase().includes(query) ||
                           (quiz.description && quiz.description.toLowerCase().includes(query));
      const matchesCategory = !selectedCategory || quiz.category === selectedCategory;
      return matchesQuery && matchesCategory;
    });

    renderQuizzesTable(filtered);
  };

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (categoryFilter) categoryFilter.addEventListener('change', applyFilters);
}

function renderQuizzesTable(quizzes) {
  const tableContainer = document.getElementById('instructor-quiz-table-body');
  if (!tableContainer) return;

  if (!quizzes || quizzes.length === 0) {
    tableContainer.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; padding: 3rem 1rem;">
          <div class="empty-state" style="padding: 1rem 0;">
            <div class="empty-state-icon">
              <svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
            </div>
            <h4 class="empty-state-title">No Quizzes Found</h4>
            <p class="empty-state-text">Create your first assessment to start testing student skills.</p>
            <a href="create-quiz.html" class="btn btn-primary btn-sm">+ Create New Quiz</a>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tableContainer.innerHTML = quizzes.map(quiz => `
    <tr>
      <td>
        <strong>${escapeHTML(quiz.title)}</strong>
        <div style="font-size: 0.75rem; color: var(--text-muted);">${escapeHTML(quiz.category || 'General')}</div>
      </td>
      <td>${quiz.question_count || (quiz.questions ? quiz.questions.length : 0)}</td>
      <td>${quiz.duration_minutes} Mins</td>
      <td>${formatDate(quiz.created_at)}</td>
      <td><span class="badge badge-success">Active</span></td>
      <td>
        <div class="actions-cell">
          <a href="take-quiz.html?id=${quiz.id}" class="btn btn-secondary btn-sm" title="Preview Quiz as Student">
            Preview
          </a>
          <button class="btn btn-danger-outline btn-sm" onclick="handleDeleteQuiz('${quiz.id}', '${escapeHTML(quiz.title)}')" title="Delete Quiz">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            Delete
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

window.handleDeleteQuiz = function(quizId, quizTitle) {
  showConfirmModal({
    title: 'Delete Assessment',
    message: `Are you sure you want to permanently delete "${quizTitle}"? This action cannot be undone.`,
    confirmText: 'Delete Quiz',
    isDanger: true,
    onConfirm: async () => {
      try {
        await quizAPI.delete(quizId);
        showToast(`Quiz "${quizTitle}" deleted.`, 'success');
        // Refresh list
        allQuizzes = allQuizzes.filter(q => q.id !== quizId);
        renderQuizzesTable(allQuizzes);
        // Update total stat
        const totalElem = document.getElementById('stat-total-quizzes');
        if (totalElem) totalElem.textContent = allQuizzes.length;
      } catch (err) {
        showToast(err.message || 'Failed to delete quiz.', 'error');
      }
    }
  });
};

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
