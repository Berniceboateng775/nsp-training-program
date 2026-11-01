/**
 * Vellichor AI — Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth()) return;
    renderSidebar('dashboard.html');

    const user = api.getUser();
    const welcomeEl = document.getElementById('welcomeMsg');
    if (user && user.name) {
        welcomeEl.textContent = `Hey, ${user.name.split(' ')[0]}.`;
    }

    // Load dynamic stats
    loadDashboardStats();

    // Load trending books for the dashboard
    await loadRecentBooks();
});


function loadDashboardStats() {
    // Pull real counts from localStorage activity tracking
    const stats = JSON.parse(localStorage.getItem('vellichor_stats') || '{}');
    const booksExplored = stats.books_explored || 0;
    const aiConversations = stats.ai_conversations || 0;
    const textsAnalyzed = stats.texts_analyzed || 0;
    const dominantMood = stats.dominant_mood || '—';

    document.getElementById('statBooks').textContent = booksExplored;
    document.getElementById('statChats').textContent = aiConversations;
    document.getElementById('statTexts').textContent = textsAnalyzed;
    document.getElementById('statMood').textContent = dominantMood;
}

// Global: increment a stat counter
function incrementStat(key) {
    const stats = JSON.parse(localStorage.getItem('vellichor_stats') || '{}');
    stats[key] = (stats[key] || 0) + 1;
    localStorage.setItem('vellichor_stats', JSON.stringify(stats));
}

function setStatValue(key, value) {
    const stats = JSON.parse(localStorage.getItem('vellichor_stats') || '{}');
    stats[key] = value;
    localStorage.setItem('vellichor_stats', JSON.stringify(stats));
}


async function loadRecentBooks() {
    const grid = document.getElementById('recentBooks');
    
    try {
        const data = await api.getTrending();
        if (data.books && data.books.length > 0) {
            grid.innerHTML = data.books.map(book => createBookCard(book)).join('');
        } else {
            grid.innerHTML = createMockBooks();
        }
    } catch {
        // Use mock data if backend isn't running
        grid.innerHTML = createMockBooks();
    }
}


function createBookCard(book) {
    // Use real cover image if available
    const coverHtml = book.cover_url
        ? `<img src="${book.cover_url}" alt="${book.title}" loading="lazy" style="width:100%;height:100%;object-fit:cover;" onerror="this.parentNode.innerHTML='<span style=\\'opacity:0.6;position:relative;z-index:1;\\'>${book.title.substring(0, 20)}</span>'">`
        : `<span style="opacity: 0.6; position: relative; z-index: 1;">${book.title.substring(0, 20)}</span>`;

    const coverBg = book.cover_url ? '' : `background: var(--color-gold-glow);`;

    // Clean genre — filter out messy Open Library metadata
    let genre = '';
    if (Array.isArray(book.genre)) {
        genre = book.genre
            .filter(g => !g.includes(':') && !g.includes('=') && g.length < 30)
            .slice(0, 2).join(', ');
    } else {
        genre = book.genre || '';
    }

    const rating = book.rating ? `${icons.star} ${book.rating}` : '';

    return `
        <div class="book-card">
            <div class="book-cover" style="${coverBg}">
                ${coverHtml}
            </div>
            <div class="book-info">
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author}</div>
                ${genre ? `<div class="book-genre">${genre}</div>` : ''}
                ${rating ? `<div class="book-rating">${rating}</div>` : ''}
            </div>
        </div>
    `;
}



function createMockBooks() {
    const mockBooks = [
        { title: 'The Night Circus', author: 'Erin Morgenstern', genre: 'Fantasy', description: 'A breathtaking tale of a mysterious competition between two young magicians.', rating: 4.6 },
        { title: 'Project Hail Mary', author: 'Andy Weir', genre: 'Sci-Fi', description: 'A lone astronaut must save humanity in this gripping interstellar adventure.', rating: 4.8 },
        { title: 'The Song of Achilles', author: 'Madeline Miller', genre: 'Historical', description: 'A devastating retelling of the Iliad through the eyes of Patroclus.', rating: 4.7 },
        { title: 'Klara and the Sun', author: 'Kazuo Ishiguro', genre: 'Literary', description: 'An Artificial Friend observes the world, exploring love and consciousness.', rating: 4.2 },
    ];

    return mockBooks.map(book => createBookCard(book)).join('');
}
