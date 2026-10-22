/**
 * Quiz Assessment Platform - Instructor Quiz Creator Engine
 * 
 * Enables dynamic question addition, option configuration,
 * validation, preview, and submission.
 */

let questionCounter = 0;

document.addEventListener('DOMContentLoaded', () => {
  // Ensure instructor role
  const currentUser = authAPI.requireRole(['instructor']);
  if (!currentUser) return;

  setupUserInterface(currentUser);
  initQuizBuilder();
});

function setupUserInterface(user) {
  const userNameElements = document.querySelectorAll('.user-name');
  userNameElements.forEach(el => el.textContent = user.full_name || 'Instructor');

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
        message: 'Are you sure you want to sign out?',
        confirmText: 'Sign Out',
        isDanger: true,
        onConfirm: () => authAPI.logout()
      });
    });
  });

  // Mobile menu
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

function initQuizBuilder() {
  const addQuestionBtn = document.getElementById('add-question-btn');
  const questionsContainer = document.getElementById('questions-list-container');
  const quizForm = document.getElementById('create-quiz-form');
  const previewBtn = document.getElementById('preview-quiz-btn');

  // Add initial question
  addDynamicQuestion();

  if (addQuestionBtn) {
    addQuestionBtn.addEventListener('click', () => {
      addDynamicQuestion();
    });
  }

  if (quizForm) {
    quizForm.addEventListener('submit', handleSaveQuiz);
  }

  if (previewBtn) {
    previewBtn.addEventListener('click', handlePreviewQuiz);
  }
}

function addDynamicQuestion(initialData = null) {
  const container = document.getElementById('questions-list-container');
  if (!container) return;

  questionCounter++;
  const qId = questionCounter;

  const item = document.createElement('div');
  item.className = 'dynamic-question-item';
  item.id = `q-block-${qId}`;

  item.innerHTML = `
    <div class="dynamic-q-header">
      <span class="dynamic-q-title">Question <span class="q-display-number">${container.children.length + 1}</span></span>
      <button type="button" class="btn btn-danger-outline btn-sm remove-q-btn" data-qid="${qId}">
        <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
        Remove
      </button>
    </div>

    <div class="form-group">
      <label class="form-label">Question Text <span class="required">*</span></label>
      <input type="text" class="form-control q-text-input" placeholder="e.g. What is the time complexity of binary search?" required value="${initialData ? escapeHTML(initialData.text) : ''}">
    </div>

    <div class="form-group">
      <label class="form-label">Answer Options (Select the radio of the correct answer) <span class="required">*</span></label>
      <div class="builder-options-grid">
        ${[0, 1, 2, 3].map(optIdx => `
          <div class="builder-option-row">
            <input type="radio" name="correct_opt_${qId}" class="correct-option-radio" value="${optIdx}" ${optIdx === 0 ? 'checked' : ''} title="Mark as correct answer">
            <input type="text" class="form-control opt-input opt-input-${optIdx}" placeholder="Option ${String.fromCharCode(65 + optIdx)}" required value="${initialData && initialData.options ? escapeHTML(initialData.options[optIdx] || '') : ''}">
          </div>
        `).join('')}
      </div>
    </div>

    <div class="form-group" style="margin-bottom: 0;">
      <label class="form-label">Explanation / Solution Note (Optional)</label>
      <input type="text" class="form-control q-explanation-input" placeholder="e.g. Binary search cuts the search space in half at each step." value="${initialData ? escapeHTML(initialData.explanation || '') : ''}">
    </div>
  `;

  container.appendChild(item);

  // Hook remove button
  item.querySelector('.remove-q-btn').addEventListener('click', () => {
    if (container.children.length <= 1) {
      showToast('A quiz must have at least one question.', 'warning');
      return;
    }
    item.remove();
    updateQuestionNumbers();
  });

  updateQuestionNumbers();
}

function updateQuestionNumbers() {
  const container = document.getElementById('questions-list-container');
  if (!container) return;

  const blocks = container.querySelectorAll('.dynamic-question-item');
  blocks.forEach((block, idx) => {
    const numDisplay = block.querySelector('.q-display-number');
    if (numDisplay) numDisplay.textContent = idx + 1;
  });

  const countBadge = document.getElementById('total-q-badge');
  if (countBadge) {
    countBadge.textContent = `${blocks.length} Question${blocks.length === 1 ? '' : 's'}`;
  }
}

function gatherFormData() {
  const title = document.getElementById('quiz-title').value.trim();
  const description = document.getElementById('quiz-desc').value.trim();
  const category = document.getElementById('quiz-category').value.trim();
  const difficulty = document.getElementById('quiz-difficulty').value;
  const duration = parseInt(document.getElementById('quiz-duration').value, 10);
  const passingScore = parseInt(document.getElementById('quiz-pass-score').value, 10);

  if (!title) {
    showToast('Please enter a quiz title.', 'error');
    document.getElementById('quiz-title').focus();
    return null;
  }

  if (isNaN(duration) || duration <= 0) {
    showToast('Please provide a valid duration in minutes (min 1).', 'error');
    document.getElementById('quiz-duration').focus();
    return null;
  }

  const container = document.getElementById('questions-list-container');
  const blocks = container.querySelectorAll('.dynamic-question-item');

  if (blocks.length === 0) {
    showToast('Please add at least one question.', 'error');
    return null;
  }

  const questions = [];

  for (let i = 0; i < blocks.length; i++) {
    const block = blocks[i];
    const text = block.querySelector('.q-text-input').value.trim();
    if (!text) {
      showToast(`Question ${i + 1} is missing question text.`, 'error');
      block.querySelector('.q-text-input').focus();
      return null;
    }

    const options = [];
    for (let optIdx = 0; optIdx < 4; optIdx++) {
      const optVal = block.querySelector(`.opt-input-${optIdx}`).value.trim();
      if (!optVal) {
        showToast(`Question ${i + 1} Option ${String.fromCharCode(65 + optIdx)} cannot be empty.`, 'error');
        block.querySelector(`.opt-input-${optIdx}`).focus();
        return null;
      }
      options.push(optVal);
    }

    const checkedRadio = block.querySelector('.correct-option-radio:checked');
    const correctOption = checkedRadio ? parseInt(checkedRadio.value, 10) : 0;
    const explanation = block.querySelector('.q-explanation-input').value.trim();

    questions.push({
      text,
      options,
      correct_option: correctOption,
      explanation
    });
  }

  return {
    title,
    description,
    category: category || 'General',
    difficulty: difficulty || 'Intermediate',
    duration_minutes: duration,
    passing_score_percentage: isNaN(passingScore) ? 60 : passingScore,
    questions
  };
}

function handlePreviewQuiz() {
  const quizData = gatherFormData();
  if (!quizData) return;

  const previewHtml = `
    <div style="max-height: 400px; overflow-y: auto; padding-right: 0.5rem;">
      <div style="margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem;">
        <span class="badge badge-indigo">${escapeHTML(quizData.category)}</span>
        <span class="badge badge-neutral">${escapeHTML(quizData.difficulty)}</span>
        <span class="badge badge-success">${quizData.duration_minutes} Mins</span>
      </div>
      <p style="font-size: 0.875rem; margin-bottom: 1rem; color: var(--text-muted);">${escapeHTML(quizData.description || 'No description provided.')}</p>

      <h5 style="margin-bottom: 0.75rem; font-size: 0.95rem;">Questions (${quizData.questions.length})</h5>
      ${quizData.questions.map((q, idx) => `
        <div style="background: var(--color-slate-50); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 0.875rem; margin-bottom: 0.75rem;">
          <div style="font-weight: 700; margin-bottom: 0.5rem;">Q${idx + 1}: ${escapeHTML(q.text)}</div>
          <div style="font-size: 0.8125rem;">
            ${q.options.map((opt, oIdx) => `
              <div style="padding: 0.2rem 0; ${oIdx === q.correct_option ? 'color: var(--color-emerald-600); font-weight: 700;' : 'color: var(--color-slate-600);'}">
                ${String.fromCharCode(65 + oIdx)}. ${escapeHTML(opt)} ${oIdx === q.correct_option ? '✓ (Correct)' : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `).join('')}
    </div>
  `;

  showConfirmModal({
    title: `Preview: ${quizData.title}`,
    message: previewHtml,
    confirmText: 'Looks Good',
    cancelText: 'Close Preview'
  });
}

async function handleSaveQuiz(e) {
  e.preventDefault();
  const quizData = gatherFormData();
  if (!quizData) return;

  const saveBtn = document.getElementById('save-quiz-btn');
  const originalHtml = saveBtn.innerHTML;
  saveBtn.disabled = true;
  saveBtn.innerHTML = `<span class="spinner"></span> Saving Assessment...`;

  try {
    await quizAPI.create(quizData);
    showToast('Quiz created and published successfully!', 'success');
    setTimeout(() => {
      window.location.href = 'instructor-dashboard.html';
    }, 900);
  } catch (error) {
    saveBtn.disabled = false;
    saveBtn.innerHTML = originalHtml;
    showToast(error.message || 'Failed to save quiz.', 'error');
  }
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}
