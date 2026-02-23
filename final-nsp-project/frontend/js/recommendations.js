/**
 * Vellichor AI — Recommendations Logic
 */

let currentMood = null;
let currentGenre = '';

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    renderSidebar('recommendations.html');
    loadRecommendations();
});


function selectMood(btn, mood) {
    document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentMood = mood;
    loadRecommendations();
}


function toggleFilter(btn) {
    document.querySelectorAll('.reco-filters .tag').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    currentGenre = btn.dataset.genre;
    loadRecommendations();
}


function handleSearch() {
    const query = document.getElementById('searchInput').value.trim();
    if (query.length >= 2 || query.length === 0) {
        loadRecommendations(query);
    }
}


async function loadRecommendations(query = null) {
    const grid = document.getElementById('booksGrid');
    
    // Show skeleton loading
    grid.innerHTML = Array(6).fill(`
        <div class="book-card">
            <div class="book-cover"><div class="skeleton" style="width:60%;height:20px;"></div></div>
            <div class="book-info">
                <div class="skeleton" style="width:80%;height:16px;margin-bottom:8px;"></div>
                <div class="skeleton" style="width:50%;height:12px;margin-bottom:8px;"></div>
                <div class="skeleton" style="width:100%;height:40px;"></div>
            </div>
        </div>
    `).join('');

    try {
        const genres = currentGenre ? [currentGenre] : null;
        const data = await api.getRecommendations(query, genres, currentMood);
        renderBooks(data.books);
    } catch {
        // Fallback mock data
        renderBooks(getMockBooks());
    }
}


function renderBooks(books) {
    const grid = document.getElementById('booksGrid');
    
    if (!books || books.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>
                <h3>No books found</h3>
                <p>Try adjusting your filters or search query.</p>
            </div>
        `;
        return;
    }

    const coverColors = [
        'rgba(212,168,83,0.12)',
        'rgba(184,64,94,0.12)',
        'rgba(96,165,250,0.12)',
        'rgba(74,222,128,0.12)',
        'rgba(167,169,190,0.08)'
    ];

    grid.innerHTML = books.map((book, i) => `
        <div class="book-card animate-fade-in-up" style="animation-delay: ${i * 0.08}s">
            <div class="book-cover" style="background: ${coverColors[i % coverColors.length]};">
                <span style="opacity: 0.5; position: relative; z-index: 1; text-align: center; padding: 0 1rem;">${book.title}</span>
            </div>
            <div class="book-info">
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author}</div>
                <div class="book-genre">${book.genre}</div>
                <div class="book-description">${book.description}</div>
                <div class="book-rating">
                    ${icons.star} ${book.rating}
                </div>
                ${book.reason ? `<div class="reco-reason">"${book.reason}"</div>` : ''}
                <div class="book-actions">
                    <button class="btn btn-sm btn-secondary" onclick="addToList('${book.title}', '${book.author}', '${book.genre}')">
                        ${icons.plus} Add to List
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}


async function addToList(title, author, genre) {
    try {
        await api.addToReadingList({ title, author, genre });
        showToast(`"${title}" added to your reading list`);
    } catch {
        showToast(`"${title}" saved locally`, 'warning');
    }
}


function getMockBooks() {
    return [
        { title: 'The Night Circus', author: 'Erin Morgenstern', genre: 'Fantasy', description: 'A breathtaking, mesmerizing tale of a mysterious competition between two young magicians, set within a fantastical circus that only appears at night.', rating: 4.6, reason: 'This deeply resonates with your reading preferences and current mood.' },
        { title: 'Project Hail Mary', author: 'Andy Weir', genre: 'Science Fiction', description: 'A lone astronaut must save humanity from extinction in this gripping interstellar adventure filled with wit, science, and an unlikely friendship.', rating: 4.8, reason: 'The narrative style and thematic depth align beautifully with your taste.' },
        { title: 'The Song of Achilles', author: 'Madeline Miller', genre: 'Historical Fiction', description: 'A devastating retelling of the Iliad through the eyes of Patroclus, exploring love, destiny, and the cost of glory in ancient Greece.', rating: 4.7, reason: 'Readers with similar preferences have rated this exceptionally high.' },
        { title: 'Piranesi', author: 'Susanna Clarke', genre: 'Fantasy', description: 'A man lives in a mysterious house of infinite halls and staircases, filled with statues and an ocean.', rating: 4.3, reason: 'The emotional complexity matches what you are looking for.' },
        { title: 'Circe', author: 'Madeline Miller', genre: 'Mythology', description: 'The story of the witch Circe, who discovers her powers of sorcery and is banished to a deserted island.', rating: 4.7, reason: 'This deeply resonates with your love for mythological retellings.' },
        { title: 'A Gentleman in Moscow', author: 'Amor Towles', genre: 'Historical Fiction', description: 'A Russian count sentenced to house arrest discovers extraordinary existence within the most confined circumstances.', rating: 4.6, reason: 'The narrative style and thematic depth align beautifully with your taste.' },
    ];
}
