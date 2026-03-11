/**
 * Vellichor AI — Auth Logic
 * Handles login, registration, and guest mode.
 */

// ─── Password Visibility Toggle ─────────────────────────

function togglePassword() {
    const pwd = document.getElementById('password');
    const btn = document.getElementById('togglePwdBtn');
    if (pwd.type === 'password') {
        pwd.type = 'text';
        btn.textContent = 'Hide';
    } else {
        pwd.type = 'password';
        btn.textContent = 'Show';
    }
}
// ─── Genre Toggle ────────────────────────────────────────

function toggleGenre(el) {
    el.classList.toggle('selected');
}

function getSelectedGenres() {
    const chips = document.querySelectorAll('.genre-chip.selected');
    return Array.from(chips).map(c => c.dataset.genre);
}


// ─── Login ───────────────────────────────────────────────

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('loginError');
    const btn = document.getElementById('loginBtn');
    
    btn.textContent = 'Signing in...';
    btn.disabled = true;
    errorEl.classList.remove('show');
    
    try {
        await api.login(email, password);
        window.location.href = 'dashboard.html';
    } catch (error) {
        errorEl.textContent = error.message || 'Invalid email or password';
        errorEl.classList.add('show');
    } finally {
        btn.textContent = 'Sign In';
        btn.disabled = false;
    }
}


// ─── Register ────────────────────────────────────────────

async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const genres = getSelectedGenres();
    const errorEl = document.getElementById('registerError');
    const btn = document.getElementById('registerBtn');
    
    btn.textContent = 'Creating account...';
    btn.disabled = true;
    errorEl.classList.remove('show');
    
    try {
        await api.register(name, email, password, genres);
        window.location.href = 'dashboard.html';
    } catch (error) {
        errorEl.textContent = error.message || 'Registration failed. Please try again.';
        errorEl.classList.add('show');
    } finally {
        btn.textContent = 'Create Account';
        btn.disabled = false;
    }
}


// ─── Guest Login ─────────────────────────────────────────

function guestLogin() {
    const guestUser = {
        id: 'guest',
        name: 'Guest Reader',
        email: 'guest@vellichor.ai',
        favorite_genres: ['Fantasy', 'Science Fiction', 'Literary Fiction'],
        created_at: new Date().toISOString()
    };
    
    localStorage.setItem('vellichor_token', 'guest-token');
    localStorage.setItem('vellichor_user', JSON.stringify(guestUser));
}
