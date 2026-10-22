/**
 * Quiz Assessment Platform - Quiz Result & Review Engine
 * 
 * Visualizes scores, circular percentage gauge, metrics,
 * pass/fail status, and question-by-question review.
 */

document.addEventListener('DOMContentLoaded', async () => {
  const currentUser = authAPI.requireRole(['student', 'instructor']);
  if (!currentUser) return;

  const urlParams = new URLSearchParams(window.location.search);
  const attemptId = urlParams.get('attemptId');

  if (!attemptId) {
    showToast('No attempt ID provided.', 'error');
    setTimeout(() => window.location.href = 'student-dashboard.html', 1500);
    return;
  }

  await loadResult(attemptId);
});

async function loadResult(attemptId) {
  try {
    const result = await attemptAPI.getResult(attemptId);
    renderResultView(result);
  } catch (error) {
    console.error('Error fetching result:', error);
    document.getElementById('results-main-content').innerHTML = `
      <div class="card empty-state">
        <div class="empty-state-icon" style="color: var(--color-rose-500);">
          <svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        </div>
        <h3 class="empty-state-title">Result Not Found</h3>
        <p class="empty-state-text">${escapeHTML(error.message || 'Unable to retrieve this assessment attempt.')}</p>
        <a href="student-dashboard.html" class="btn btn-primary btn-sm">Return to Dashboard</a>
      </div>
    `;
  }
}

function renderResultView(data) {
  const titleElem = document.getElementById('result-quiz-title');
  if (titleElem) titleElem.textContent = data.quiz_title;

  // Percentage & Gauge
  const percentText = document.getElementById('score-percentage-text');
  if (percentText) percentText.textContent = `${data.percentage}%`;

  // Animate SVG Radial Progress
  const circleFill = document.getElementById('score-circle-fill');
  if (circleFill) {
    const radius = 65;
    const circumference = 2 * Math.PI * radius;
    circleFill.style.strokeDasharray = `${circumference}`;
    const offset = circumference - (data.percentage / 100) * circumference;
    
    // Set color based on pass / fail
    if (data.passed) {
      circleFill.style.stroke = 'var(--color-emerald-500)';
    } else {
      circleFill.style.stroke = 'var(--color-rose-500)';
    }

    setTimeout(() => {
      circleFill.style.strokeDashoffset = `${offset}`;
    }, 100);
  }

  // Verdict
  const verdictElem = document.getElementById('result-verdict');
  if (verdictElem) {
    if (data.passed) {
      verdictElem.innerHTML = `<span class="verdict-pass">🎉 Congratulations! You Passed</span>`;
    } else {
      verdictElem.innerHTML = `<span class="verdict-fail">⚠️ Needs Improvement (Failed)</span>`;
    }
  }

  // Stats
  document.getElementById('stat-score').textContent = `${data.score} / ${data.total_questions}`;
  document.getElementById('stat-correct').textContent = data.correct_answers;
  document.getElementById('stat-incorrect').textContent = data.incorrect_answers;
  document.getElementById('stat-time').textContent = formatSeconds(data.time_taken_seconds);

  // Retake link
  const retakeBtn = document.getElementById('btn-retake');
  if (retakeBtn) {
    retakeBtn.href = `take-quiz.html?id=${data.quiz_id}`;
  }

  // Render Detailed Review if available
  if (data.detailed_review && data.detailed_review.length > 0) {
    renderQuestionReview(data.detailed_review);
  } else {
    document.getElementById('review-section').style.display = 'none';
  }
}

function renderQuestionReview(reviews) {
  const container = document.getElementById('review-questions-list');
  if (!container) return;

  container.innerHTML = reviews.map((q, idx) => {
    return `
      <div class="review-question-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.75rem;">
          <span style="font-size: 0.8125rem; font-weight: 700; color: var(--color-indigo-600);">Question ${idx + 1}</span>
          <span class="badge ${q.is_correct ? 'badge-success' : 'badge-danger'}">
            ${q.is_correct ? '✓ Correct' : (q.user_choice === null ? '⊘ Unanswered' : '✗ Incorrect')}
          </span>
        </div>

        <p style="font-weight: 600; color: var(--color-navy-900); margin-bottom: 1rem;">${escapeHTML(q.text)}</p>

        <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem;">
          ${q.options.map((optText, optIdx) => {
            const isUserChoice = q.user_choice === optIdx;
            const isCorrectChoice = q.correct_choice === optIdx;

            let optClass = 'review-option';
            let labelBadge = '';

            if (isCorrectChoice) {
              optClass += ' is-correct';
              labelBadge = '<span class="badge badge-success">Correct Answer</span>';
            } else if (isUserChoice && !isCorrectChoice) {
              optClass += ' is-user-incorrect';
              labelBadge = '<span class="badge badge-danger">Your Choice</span>';
            }

            return `
              <div class="${optClass}">
                <div style="display:flex; align-items:center; gap: 0.5rem;">
                  <strong style="width: 1.5rem;">${String.fromCharCode(65 + optIdx)}.</strong>
                  <span>${escapeHTML(optText)}</span>
                </div>
                ${labelBadge}
              </div>
            `;
          }).join('')}
        </div>

        ${q.explanation ? `
          <div style="background: var(--color-slate-50); border-left: 3px solid var(--color-indigo-600); padding: 0.75rem 1rem; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: 0.875rem;">
            <strong style="color: var(--color-navy-800);">Explanation:</strong>
            <span style="color: var(--text-muted);">${escapeHTML(q.explanation)}</span>
          </div>
        ` : ''}
      </div>
    `;
  }).join('');
}

function formatSeconds(seconds) {
  if (!seconds || isNaN(seconds)) return 'N/A';
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
