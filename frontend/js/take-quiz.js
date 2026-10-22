/**
 * Quiz Assessment Platform - Live Quiz Taking Engine
 * 
 * Features:
 * - Distraction-free exam mode
 * - Countdown timer with auto-submit
 * - In-memory state and sessionStorage persistence
 * - Answer selection, clear answer, mark for review
 * - Dynamic question palette navigator
 * - Unload warning & duplicate submission prevention
 */

let quizSession = {
  quizId: null,
  attemptId: null,
  title: '',
  durationMinutes: 15,
  questions: [],
  currentIndex: 0,
  answers: {}, // { questionId: selectedOptionIndex }
  markedForReview: new Set(),
  timeRemainingSeconds: 0,
  timerInterval: null,
  isSubmitting: false,
  isCompleted: false
};

document.addEventListener('DOMContentLoaded', async () => {
  // Ensure user is logged in
  const currentUser = authAPI.requireRole(['student', 'instructor']);
  if (!currentUser) return;

  const urlParams = new URLSearchParams(window.location.search);
  const quizId = urlParams.get('id');

  if (!quizId) {
    showToast('No quiz specified.', 'error');
    setTimeout(() => window.location.href = 'student-dashboard.html', 1500);
    return;
  }

  await initQuizAttempt(quizId);
  setupEventListeners();
  setupUnloadWarning();
});

async function initQuizAttempt(quizId) {
  try {
    // 1. Fetch sanitized questions from server (NO correct answers sent!)
    const quizData = await quizAPI.getQuestionsForAttempt(quizId);
    
    // 2. Start attempt record on server
    const attemptRecord = await attemptAPI.start(quizId);

    quizSession.quizId = quizId;
    quizSession.attemptId = attemptRecord.attempt_id;
    quizSession.title = quizData.title;
    quizSession.durationMinutes = quizData.duration_minutes || 15;
    quizSession.questions = quizData.questions || [];
    quizSession.timeRemainingSeconds = quizSession.durationMinutes * 60;

    // Check if there was an in-progress attempt saved in sessionStorage
    const savedStateKey = `active_quiz_${quizId}_${quizSession.attemptId}`;
    const cachedState = sessionStorage.getItem(savedStateKey);
    if (cachedState) {
      try {
        const parsed = JSON.parse(cachedState);
        quizSession.answers = parsed.answers || {};
        quizSession.markedForReview = new Set(parsed.markedForReview || []);
        quizSession.currentIndex = parsed.currentIndex || 0;
        if (parsed.timeRemainingSeconds > 0) {
          quizSession.timeRemainingSeconds = parsed.timeRemainingSeconds;
        }
      } catch (e) {
        console.warn('Failed to parse cached session:', e);
      }
    }

    // Render Initial View
    document.getElementById('exam-title').textContent = quizSession.title;
    renderPalette();
    loadQuestion(quizSession.currentIndex);
    startTimer();

  } catch (error) {
    console.error('Failed to initialize quiz:', error);
    showToast(error.message || 'Error loading quiz.', 'error');
    document.getElementById('quiz-main-area').innerHTML = `
      <div class="card empty-state">
        <h3 class="empty-state-title">Quiz Unavailable</h3>
        <p class="empty-state-text">${escapeHTML(error.message || 'Unable to start this assessment.')}</p>
        <a href="student-dashboard.html" class="btn btn-primary btn-sm">Return to Dashboard</a>
      </div>
    `;
  }
}

function startTimer() {
  const timerElem = document.getElementById('quiz-timer-display');
  const timerCard = document.getElementById('quiz-timer-card');

  const updateDisplay = () => {
    const minutes = Math.floor(quizSession.timeRemainingSeconds / 60);
    const seconds = quizSession.timeRemainingSeconds % 60;
    timerElem.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

    // Warning style when under 3 minutes
    if (quizSession.timeRemainingSeconds <= 180) {
      timerCard?.classList.add('timer-warning');
    }

    if (quizSession.timeRemainingSeconds <= 0) {
      clearInterval(quizSession.timerInterval);
      showToast('Time has expired! Submitting assessment automatically...', 'warning', 4000);
      handleFinalSubmit(true);
    } else {
      quizSession.timeRemainingSeconds--;
      persistLocalSession();
    }
  };

  updateDisplay();
  quizSession.timerInterval = setInterval(updateDisplay, 1000);
}

function loadQuestion(index) {
  if (index < 0 || index >= quizSession.questions.length) return;
  quizSession.currentIndex = index;

  const currentQ = quizSession.questions[index];
  const total = quizSession.questions.length;

  // Header meta & Progress
  document.getElementById('question-counter').textContent = `Question ${index + 1} of ${total}`;
  const percentage = Math.round(((index + 1) / total) * 100);
  const progressBar = document.getElementById('quiz-progress-bar');
  if (progressBar) progressBar.style.width = `${percentage}%`;

  // Question Text
  document.getElementById('question-text').textContent = currentQ.text;

  // Options
  const optionsContainer = document.getElementById('options-container');
  const selectedChoice = quizSession.answers[currentQ.id];

  const optionLetters = ['A', 'B', 'C', 'D', 'E', 'F'];
  optionsContainer.innerHTML = currentQ.options.map((optText, optIdx) => {
    const isSelected = selectedChoice === optIdx;
    return `
      <div class="option-item ${isSelected ? 'is-selected' : ''}" data-index="${optIdx}">
        <div class="option-badge">${optionLetters[optIdx] || optIdx + 1}</div>
        <span class="option-label-text">${escapeHTML(optText)}</span>
      </div>
    `;
  }).join('');

  // Add click handlers to options
  const optionElements = optionsContainer.querySelectorAll('.option-item');
  optionElements.forEach(item => {
    item.addEventListener('click', () => {
      const optIdx = parseInt(item.getAttribute('data-index'), 10);
      selectOption(currentQ.id, optIdx);
    });
  });

  // Mark for Review Checkbox / Button
  const reviewBtn = document.getElementById('mark-review-btn');
  const isReviewed = quizSession.markedForReview.has(currentQ.id);
  if (reviewBtn) {
    reviewBtn.className = isReviewed ? 'btn btn-warning btn-sm' : 'btn btn-secondary btn-sm';
    reviewBtn.innerHTML = isReviewed 
      ? `★ Marked for Review`
      : `☆ Mark for Review`;
  }

  // Update Navigation buttons
  const prevBtn = document.getElementById('btn-prev-question');
  const nextBtn = document.getElementById('btn-next-question');
  if (prevBtn) prevBtn.disabled = index === 0;
  if (nextBtn) {
    if (index === total - 1) {
      nextBtn.textContent = 'Review & Submit';
    } else {
      nextBtn.textContent = 'Next Question →';
    }
  }

  updatePaletteHighlight();
  persistLocalSession();
}

function selectOption(questionId, optionIndex) {
  quizSession.answers[questionId] = optionIndex;
  
  // Update option DOM styling
  const optionItems = document.querySelectorAll('#options-container .option-item');
  optionItems.forEach(item => {
    const idx = parseInt(item.getAttribute('data-index'), 10);
    if (idx === optionIndex) {
      item.classList.add('is-selected');
    } else {
      item.classList.remove('is-selected');
    }
  });

  updatePaletteHighlight();
  persistLocalSession();
}

function clearAnswer() {
  const currentQ = quizSession.questions[quizSession.currentIndex];
  if (!currentQ) return;

  delete quizSession.answers[currentQ.id];
  const optionItems = document.querySelectorAll('#options-container .option-item');
  optionItems.forEach(item => item.classList.remove('is-selected'));

  updatePaletteHighlight();
  persistLocalSession();
  showToast('Answer cleared for this question.', 'info', 1500);
}

function toggleMarkForReview() {
  const currentQ = quizSession.questions[quizSession.currentIndex];
  if (!currentQ) return;

  if (quizSession.markedForReview.has(currentQ.id)) {
    quizSession.markedForReview.delete(currentQ.id);
  } else {
    quizSession.markedForReview.add(currentQ.id);
  }

  loadQuestion(quizSession.currentIndex);
}

function renderPalette() {
  const paletteGrid = document.getElementById('palette-grid');
  if (!paletteGrid) return;

  paletteGrid.innerHTML = quizSession.questions.map((q, idx) => {
    return `
      <button class="palette-btn" id="palette-btn-${idx}" data-idx="${idx}">
        ${idx + 1}
      </button>
    `;
  }).join('');

  paletteGrid.querySelectorAll('.palette-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.getAttribute('data-idx'), 10);
      loadQuestion(idx);
    });
  });
}

function updatePaletteHighlight() {
  quizSession.questions.forEach((q, idx) => {
    const btn = document.getElementById(`palette-btn-${idx}`);
    if (!btn) return;

    btn.className = 'palette-btn';

    const isCurrent = idx === quizSession.currentIndex;
    const isAnswered = quizSession.answers[q.id] !== undefined;
    const isReview = quizSession.markedForReview.has(q.id);

    if (isAnswered) btn.classList.add('is-answered');
    if (isReview) btn.classList.add('is-review');
    if (isCurrent) btn.classList.add('is-active');
  });

  // Update answered count label
  const total = quizSession.questions.length;
  const answeredCount = Object.keys(quizSession.answers).length;
  const countLabel = document.getElementById('palette-answered-count');
  if (countLabel) {
    countLabel.textContent = `${answeredCount}/${total} Answered`;
  }
}

function setupEventListeners() {
  // Navigation
  document.getElementById('btn-prev-question')?.addEventListener('click', () => {
    if (quizSession.currentIndex > 0) {
      loadQuestion(quizSession.currentIndex - 1);
    }
  });

  document.getElementById('btn-next-question')?.addEventListener('click', () => {
    if (quizSession.currentIndex < quizSession.questions.length - 1) {
      loadQuestion(quizSession.currentIndex + 1);
    } else {
      promptSubmitModal();
    }
  });

  document.getElementById('clear-answer-btn')?.addEventListener('click', clearAnswer);
  document.getElementById('mark-review-btn')?.addEventListener('click', toggleMarkForReview);
  document.getElementById('submit-quiz-trigger')?.addEventListener('click', promptSubmitModal);
}

function promptSubmitModal() {
  const total = quizSession.questions.length;
  const answered = Object.keys(quizSession.answers).length;
  const unanswered = total - answered;
  const markedReview = quizSession.markedForReview.size;

  const summaryHtml = `
    <div style="margin-bottom: 1rem;">
      <p style="margin-bottom: 0.75rem;">Are you sure you want to finish and submit your quiz?</p>
      <div style="background: var(--color-slate-50); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); font-size: 0.875rem;">
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.35rem;">
          <span>Total Questions:</span> <strong>${total}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.35rem; color: var(--color-emerald-600);">
          <span>Answered:</span> <strong>${answered}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.35rem; color: var(--color-rose-600);">
          <span>Unanswered:</span> <strong>${unanswered}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; color: var(--color-amber-600);">
          <span>Marked for Review:</span> <strong>${markedReview}</strong>
        </div>
      </div>
      ${unanswered > 0 ? '<p style="color: var(--color-amber-600); font-size: 0.8125rem; margin-top: 0.75rem;">⚠️ You still have unanswered questions. Unanswered questions will receive 0 marks.</p>' : ''}
    </div>
  `;

  showConfirmModal({
    title: 'Submit Assessment',
    message: summaryHtml,
    confirmText: 'Yes, Submit Quiz',
    cancelText: 'Continue Test',
    onConfirm: () => handleFinalSubmit(false)
  });
}

async function handleFinalSubmit(isAutoExpired = false) {
  if (quizSession.isSubmitting || quizSession.isCompleted) return;
  quizSession.isSubmitting = true;
  clearInterval(quizSession.timerInterval);

  // Disable UI buttons to prevent double submission
  const submitBtns = document.querySelectorAll('#submit-quiz-trigger, #btn-next-question, #btn-prev-question');
  submitBtns.forEach(b => b.disabled = true);

  const timeTakenSeconds = (quizSession.durationMinutes * 60) - Math.max(0, quizSession.timeRemainingSeconds);

  try {
    showToast('Submitting answers and evaluating results...', 'info');

    const result = await attemptAPI.submit(
      quizSession.attemptId,
      quizSession.quizId,
      quizSession.answers,
      timeTakenSeconds
    );

    quizSession.isCompleted = true;
    // Clear cached session
    sessionStorage.removeItem(`active_quiz_${quizSession.quizId}_${quizSession.attemptId}`);

    // Redirect to results page
    window.location.href = `results.html?attemptId=${result.id}`;

  } catch (error) {
    quizSession.isSubmitting = false;
    submitBtns.forEach(b => b.disabled = false);
    showToast(error.message || 'Failed to submit quiz. Please try again.', 'error');
  }
}

function persistLocalSession() {
  if (quizSession.isCompleted) return;
  const stateKey = `active_quiz_${quizSession.quizId}_${quizSession.attemptId}`;
  const data = {
    answers: quizSession.answers,
    markedForReview: Array.from(quizSession.markedForReview),
    currentIndex: quizSession.currentIndex,
    timeRemainingSeconds: quizSession.timeRemainingSeconds
  };
  sessionStorage.setItem(stateKey, JSON.stringify(data));
}

function setupUnloadWarning() {
  window.addEventListener('beforeunload', (e) => {
    if (!quizSession.isCompleted && !quizSession.isSubmitting && quizSession.questions.length > 0) {
      e.preventDefault();
      e.returnValue = 'You have an active assessment in progress. Are you sure you want to leave? Your timer will continue running.';
      return e.returnValue;
    }
  });
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}
