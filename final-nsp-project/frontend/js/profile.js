/**
 * Vellichor AI — Profile Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth()) return;
    renderSidebar('profile.html');
    loadProfile();
    loadReadingList();
});


function toggleGenre(el) {
    el.classList.toggle('selected');
}


function loadProfile() {
    const user = api.getUser();
    if (!user) return;

    document.getElementById('profileAvatar').textContent = user.name ? user.name.charAt(0).toUpperCase() : '?';
    document.getElementById('profileName').textContent = user.name || 'Reader';
    document.getElementById('profileEmail').textContent = user.email || '';
    document.getElementById('profileDate').textContent = user.created_at ? `Member since ${formatDate(user.created_at)}` : '';
    document.getElementById('prefName').value = user.name || '';

    // Highlight saved genres
    const genres = user.favorite_genres || [];
    document.querySelectorAll('#profileGenres .genre-chip').forEach(chip => {
        if (genres.includes(chip.dataset.genre)) {
            chip.classList.add('selected');
        }
    });
}


async function savePreferences(event) {
    event.preventDefault();

    const name = document.getElementById('prefName').value.trim();
    const chips = document.querySelectorAll('#profileGenres .genre-chip.selected');
    const genres = Array.from(chips).map(c => c.dataset.genre);

    try {
        const updated = await api.updateProfile({ name, favorite_genres: genres });
        api.setUser(updated);
        showToast('Preferences saved successfully');
        document.getElementById('profileName').textContent = name;
        document.getElementById('profileAvatar').textContent = name.charAt(0).toUpperCase();
    } catch {
        // Update locally
        const user = api.getUser();
        user.name = name;
        user.favorite_genres = genres;
        api.setUser(user);
        showToast('Preferences saved locally');
        document.getElementById('profileName').textContent = name;
        document.getElementById('profileAvatar').textContent = name.charAt(0).toUpperCase();
    }
}


async function loadReadingList() {
    const container = document.getElementById('readingList');

    try {
        const data = await api.getReadingList();
        if (data.books && data.books.length > 0) {
            container.innerHTML = data.books.map(book => `
                <div class="reading-item">
                    <div class="item-info">
                        <div class="item-title">${book.title}</div>
                        <div class="item-meta">${book.author} · ${book.genre} · Added ${formatDate(book.added_at)}</div>
                    </div>
                </div>
            `).join('');
        }
    } catch {
        // Keep default empty state
    }
}


function clearReadingList() {
    if (confirm('Are you sure you want to clear your reading list? This cannot be undone.')) {
        document.getElementById('readingList').innerHTML = `
            <div class="empty-state" style="padding: var(--space-8);">
                <p style="color: var(--color-text-muted); font-size: var(--text-sm);">Reading list cleared.</p>
            </div>
        `;
        showToast('Reading list cleared');
    }
}


function resetAccount() {
    if (confirm('Are you sure you want to reset all your data? This will clear preferences, reading history, and conversations.')) {
        localStorage.removeItem('vellichor_user');
        localStorage.removeItem('vellichor_token');
        showToast('Account data reset');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500);
    }
}
