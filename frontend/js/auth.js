/**
 * Quiz Assessment Platform - Authentication Logic
 * 
 * Handles login, registration, validation, password toggling,
 * strength checking, and demo autofill credentials.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check if session expired banner should show
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('expired')) {
    showAlert('Your session has expired. Please log in again.', 'error');
  }

  initPasswordToggle();
  initLoginForm();
  initRegisterForm();
  initDemoButtons();
});

// Password Show / Hide Toggle
function initPasswordToggle() {
  const toggleButtons = document.querySelectorAll('.password-toggle-btn');
  toggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';

      // Update icon
      if (isPassword) {
        btn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"/></svg>`;
        btn.setAttribute('aria-label', 'Hide password');
      } else {
        btn.innerHTML = `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>`;
        btn.setAttribute('aria-label', 'Show password');
      }
    });
  });
}

// Login Form Handling
function initLoginForm() {
  const loginForm = document.getElementById('login-form');
  if (!loginForm) return;

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlert();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const roleInput = document.querySelector('input[name="role"]:checked');
    const role = roleInput ? roleInput.value : 'student';
    const rememberMe = document.getElementById('remember-me')?.checked ?? true;

    // Client-side Validation
    if (!email) {
      showAlert('Please enter your email address.', 'error');
      document.getElementById('email').focus();
      return;
    }
    if (!isValidEmail(email)) {
      showAlert('Please enter a valid email format (e.g. user@college.edu).', 'error');
      document.getElementById('email').focus();
      return;
    }
    if (!password) {
      showAlert('Please enter your password.', 'error');
      document.getElementById('password').focus();
      return;
    }

    const submitBtn = document.getElementById('login-submit-btn');
    const originalText = submitBtn.innerHTML;
    setLoadingState(submitBtn, true, 'Signing in...');

    try {
      const response = await authAPI.login(email, password, role);
      showToast('Login successful! Redirecting...', 'success');

      setTimeout(() => {
        if (response.user.role === 'instructor') {
          window.location.href = 'instructor-dashboard.html';
        } else {
          window.location.href = 'student-dashboard.html';
        }
      }, 700);
    } catch (err) {
      setLoadingState(submitBtn, false, originalText);
      showAlert(err.message || 'Login failed. Please check your credentials.', 'error');
    }
  });
}

// Registration Form Handling
function initRegisterForm() {
  const registerForm = document.getElementById('register-form');
  if (!registerForm) return;

  const passwordInput = document.getElementById('password');
  if (passwordInput) {
    passwordInput.addEventListener('input', () => {
      evaluatePasswordStrength(passwordInput.value);
    });
  }

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlert();

    const fullName = document.getElementById('fullname').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const roleInput = document.querySelector('input[name="role"]:checked');
    const role = roleInput ? roleInput.value : 'student';

    // Validation
    if (!fullName || fullName.length < 2) {
      showAlert('Please enter your full name (minimum 2 characters).', 'error');
      document.getElementById('fullname').focus();
      return;
    }
    if (!isValidEmail(email)) {
      showAlert('Please enter a valid email address.', 'error');
      document.getElementById('email').focus();
      return;
    }
    if (password.length < 6) {
      showAlert('Password must be at least 6 characters long.', 'error');
      document.getElementById('password').focus();
      return;
    }
    if (password !== confirmPassword) {
      showAlert('Passwords do not match. Please re-enter.', 'error');
      document.getElementById('confirm-password').focus();
      return;
    }

    const submitBtn = document.getElementById('register-submit-btn');
    const originalText = submitBtn.innerHTML;
    setLoadingState(submitBtn, true, 'Creating Account...');

    try {
      const response = await authAPI.register(fullName, email, password, role);
      showToast('Account created successfully!', 'success');

      setTimeout(() => {
        if (response.user.role === 'instructor') {
          window.location.href = 'instructor-dashboard.html';
        } else {
          window.location.href = 'student-dashboard.html';
        }
      }, 800);
    } catch (err) {
      setLoadingState(submitBtn, false, originalText);
      showAlert(err.message || 'Registration failed.', 'error');
    }
  });
}

// Demo Autofill Buttons
function initDemoButtons() {
  const demoStudentBtn = document.getElementById('btn-demo-student');
  const demoInstructorBtn = document.getElementById('btn-demo-instructor');

  if (demoStudentBtn) {
    demoStudentBtn.addEventListener('click', () => {
      const emailField = document.getElementById('email');
      const passwordField = document.getElementById('password');
      const studentRadio = document.getElementById('role-student');

      if (emailField) emailField.value = 'student@college.edu';
      if (passwordField) passwordField.value = 'student123';
      if (studentRadio) studentRadio.checked = true;

      showToast('Student demo credentials filled. Click "Sign In".', 'info', 2000);
    });
  }

  if (demoInstructorBtn) {
    demoInstructorBtn.addEventListener('click', () => {
      const emailField = document.getElementById('email');
      const passwordField = document.getElementById('password');
      const instructorRadio = document.getElementById('role-instructor');

      if (emailField) emailField.value = 'instructor@college.edu';
      if (passwordField) passwordField.value = 'instructor123';
      if (instructorRadio) instructorRadio.checked = true;

      showToast('Instructor demo credentials filled. Click "Sign In".', 'info', 2000);
    });
  }
}

// Password Strength Meter
function evaluatePasswordStrength(password) {
  const bars = [
    document.getElementById('bar-1'),
    document.getElementById('bar-2'),
    document.getElementById('bar-3')
  ];
  const label = document.getElementById('strength-label');
  if (!bars[0] || !label) return;

  // Reset
  bars.forEach(b => {
    b.className = 'strength-bar';
  });

  if (!password) {
    label.textContent = 'Password strength';
    label.style.color = 'var(--color-slate-500)';
    return;
  }

  let score = 0;
  if (password.length >= 6) score++;
  if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password)) score++;
  if (password.length >= 10 && /[^A-Za-z0-9]/.test(password)) score++;

  if (score === 1) {
    bars[0].classList.add('active-weak');
    label.textContent = 'Weak';
    label.style.color = 'var(--color-rose-500)';
  } else if (score === 2) {
    bars[0].classList.add('active-medium');
    bars[1].classList.add('active-medium');
    label.textContent = 'Medium';
    label.style.color = 'var(--color-amber-500)';
  } else if (score >= 3) {
    bars[0].classList.add('active-strong');
    bars[1].classList.add('active-strong');
    bars[2].classList.add('active-strong');
    label.textContent = 'Strong';
    label.style.color = 'var(--color-emerald-500)';
  }
}

// Helpers
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showAlert(message, type = 'error') {
  const alertBox = document.getElementById('auth-alert');
  if (!alertBox) return;

  alertBox.className = `auth-alert auth-alert-${type} is-visible`;
  alertBox.innerHTML = `
    <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01"/></svg>
    <span>${message}</span>
  `;
}

function clearAlert() {
  const alertBox = document.getElementById('auth-alert');
  if (alertBox) {
    alertBox.className = 'auth-alert';
    alertBox.innerHTML = '';
  }
}

function setLoadingState(button, isLoading, text) {
  if (isLoading) {
    button.disabled = true;
    button.innerHTML = `<span class="spinner"></span> <span>${text}</span>`;
  } else {
    button.disabled = false;
    button.innerHTML = text;
  }
}
