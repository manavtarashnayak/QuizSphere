/**
 * Quiz Assessment Platform - Quiz Directory Listing
 */

let quizzesMasterList = [];

document.addEventListener('DOMContentLoaded', async () => {
  setupNavigation();
  initSearchAndFilters();
  await loadQuizCatalog();
});

function setupNavigation() {
  const user = tokenStorage.getUser();
  const authNavContainer = document.getElementById('navbar-auth-actions');

  if (authNavContainer) {
    if (user) {
      const dashboardLink = user.role === 'instructor' ? 'instructor-dashboard.html' : 'student-dashboard.html';
      authNavContainer.innerHTML = `
        <a href="${dashboardLink}" class="btn btn-secondary btn-sm">Dashboard</a>
        <button class="btn btn-primary btn-sm" id="logout-btn">Logout</button>
      `;
      document.getElementById('logout-btn')?.addEventListener('click', () => authAPI.logout());
    } else {
      authNavContainer.innerHTML = `
        <a href="login.html" class="btn btn-secondary btn-sm">Log In</a>
        <a href="register.html" class="btn btn-primary btn-sm">Get Started</a>
      `;
    }
  }

  // Mobile menu
  const mobileToggle = document.getElementById('mobile-toggle');
  const navLinks = document.getElementById('nav-links');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('is-open');
    });
  }
}

async function loadQuizCatalog() {
  const gridContainer = document.getElementById('quiz-catalog-grid');
  if (!gridContainer) return;

  // Show loading skeleton / spinner
  gridContainer.innerHTML = `
    <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem;">
      <span class="spinner spinner-dark" style="width: 2.5rem; height: 2.5rem;"></span>
      <p style="margin-top: 1rem; color: var(--text-muted);">Fetching available assessments...</p>
    </div>
  `;

  try {
    const quizzes = await quizAPI.getAll();
    quizzesMasterList = quizzes;
    renderCatalogCards(quizzesMasterList);
    populateCategoryDropdown(quizzesMasterList);
  } catch (error) {
    console.error('Error fetching quiz catalog:', error);
    gridContainer.innerHTML = `
      <div class="card empty-state" style="grid-column: 1 / -1;">
        <div class="empty-state-icon" style="color: var(--color-rose-500);">
          <svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01"/></svg>
        </div>
        <h4 class="empty-state-title">Failed to Load Quizzes</h4>
        <p class="empty-state-text">${escapeHTML(error.message || 'Please check your internet connection or server status.')}</p>
        <button class="btn btn-primary btn-sm" onclick="loadQuizCatalog()">Retry</button>
      </div>
    `;
  }
}

function initSearchAndFilters() {
  const searchInput = document.getElementById('catalog-search');
  const categorySelect = document.getElementById('catalog-category');
  const difficultySelect = document.getElementById('catalog-difficulty');

  const executeFilter = () => {
    const query = (searchInput?.value || '').toLowerCase().trim();
    const cat = categorySelect?.value || '';
    const diff = difficultySelect?.value || '';

    const results = quizzesMasterList.filter(quiz => {
      const matchText = quiz.title.toLowerCase().includes(query) ||
                        (quiz.description && quiz.description.toLowerCase().includes(query));
      const matchCat = !cat || quiz.category === cat;
      const matchDiff = !diff || (quiz.difficulty && quiz.difficulty.toLowerCase() === diff.toLowerCase());
      return matchText && matchCat && matchDiff;
    });

    renderCatalogCards(results);
  };

  if (searchInput) searchInput.addEventListener('input', executeFilter);
  if (categorySelect) categorySelect.addEventListener('change', executeFilter);
  if (difficultySelect) difficultySelect.addEventListener('change', executeFilter);
}

function populateCategoryDropdown(quizzes) {
  const categorySelect = document.getElementById('catalog-category');
  if (!categorySelect) return;

  const categories = [...new Set(quizzes.map(q => q.category).filter(Boolean))];
  categories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat;
    categorySelect.appendChild(opt);
  });
}

function renderCatalogCards(quizzes) {
  const container = document.getElementById('quiz-catalog-grid');
  const countBadge = document.getElementById('catalog-results-count');
  if (!container) return;

  if (countBadge) {
    countBadge.textContent = `${quizzes.length} Assessment${quizzes.length === 1 ? '' : 's'}`;
  }

  if (quizzes.length === 0) {
    container.innerHTML = `
      <div class="card empty-state" style="grid-column: 1 / -1;">
        <div class="empty-state-icon">
          <svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        </div>
        <h4 class="empty-state-title">No matching assessments found</h4>
        <p class="empty-state-text">Try adjusting your search criteria or clearing your active filters.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = quizzes.map(quiz => `
    <div class="quiz-card">
      <div class="quiz-card-header">
        <h3 class="quiz-card-title">${escapeHTML(quiz.title)}</h3>
        <span class="badge ${getDifficultyBadgeClass(quiz.difficulty)}">${escapeHTML(quiz.difficulty || 'Intermediate')}</span>
      </div>
      <p class="quiz-card-desc">${escapeHTML(quiz.description || 'Comprehensive assessment covering key topic competencies.')}</p>
      
      <div class="quiz-card-meta">
        <div class="meta-item">
          <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span>${quiz.question_count || (quiz.questions ? quiz.questions.length : 0)} Questions</span>
        </div>
        <div class="meta-item">
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

function getDifficultyBadgeClass(diff) {
  switch ((diff || '').toLowerCase()) {
    case 'beginner': return 'badge-success';
    case 'intermediate': return 'badge-indigo';
    case 'advanced': return 'badge-danger';
    default: return 'badge-neutral';
  }
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}
