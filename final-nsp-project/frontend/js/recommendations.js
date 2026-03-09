/**
 * Vellichor AI — Recommendations (Open Library)
 * Displays real books from Open Library with covers, search, and detail modals.
 */

let currentGenre = '';
let searchTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    renderSidebar('recommendations.html');
    loadRecommendations();
});


function selectMood(btn, mood) {
    document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    // For moods, search Open Library with mood as keyword
    if (mood) {
        searchOpenLibrary(mood + ' fiction');
    } else {
        loadRecommendations();
    }
}


function toggleFilter(btn) {
    document.querySelectorAll('.reco-filters .tag').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    currentGenre = btn.dataset.genre;

    if (currentGenre) {
        searchOpenLibrary(currentGenre);
    } else {
        loadRecommendations();
    }
}


function handleSearch() {
    const query = document.getElementById('searchInput').value.trim();
    clearTimeout(searchTimeout);
    
    if (query.length >= 3) {
        // Debounce: wait 500ms after typing stops
        searchTimeout = setTimeout(() => searchOpenLibrary(query), 500);
    } else if (query.length === 0) {
        loadRecommendations();
    }
}


async function searchOpenLibrary(query) {
    const grid = document.getElementById('booksGrid');
    showLoadingSkeleton(grid);

    try {
        const data = await api.searchBooks(query);
        renderBooks(data.books || []);
    } catch (err) {
        console.error('Search error:', err);
        showToast('Search failed. Try again.', 'error');
        renderBooks([]);
    }
}


async function loadRecommendations() {
    const grid = document.getElementById('booksGrid');
    showLoadingSkeleton(grid);

    try {
        const data = await api.getRecommendations();
        renderBooks(data.books || []);
    } catch {
        // Fallback: load trending
        try {
            const trending = await api.getTrending();
            renderBooks(trending.books || []);
        } catch {
            renderBooks([]);
        }
    }
}


function showLoadingSkeleton(grid) {
    grid.innerHTML = Array(6).fill(`
        <div class="book-card">
            <div class="book-cover skeleton-cover">
                <div class="skeleton" style="width:100%;height:100%;border-radius:8px;"></div>
            </div>
            <div class="book-info">
                <div class="skeleton" style="width:80%;height:16px;margin-bottom:8px;"></div>
                <div class="skeleton" style="width:50%;height:12px;margin-bottom:8px;"></div>
                <div class="skeleton" style="width:100%;height:40px;"></div>
            </div>
        </div>
    `).join('');
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

    grid.innerHTML = books.map((book, i) => {
        const coverHtml = book.cover_url
            ? `<img src="${book.cover_url}" alt="${book.title}" loading="lazy" onerror="this.parentNode.innerHTML='<span class=\\'cover-placeholder\\'>${book.title}</span>'">`
            : `<span class="cover-placeholder">${book.title}</span>`;
        
        const genres = Array.isArray(book.genre) ? book.genre.slice(0, 2).join(', ') : (book.genre || '');
        const rating = book.rating ? `${icons.star} ${book.rating}` : '';
        const year = book.year ? `(${book.year})` : '';
        const olKey = book.ol_key || '';
        const workId = olKey.replace('/works/', '');

        return `
        <div class="book-card animate-fade-in-up" style="animation-delay: ${i * 0.06}s" onclick="openBookDetail('${workId}')" role="button" tabindex="0">
            <div class="book-cover">
                ${coverHtml}
            </div>
            <div class="book-info">
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author} ${year}</div>
                ${genres ? `<div class="book-genre">${genres}</div>` : ''}
                ${rating ? `<div class="book-rating">${rating}</div>` : ''}
            </div>
        </div>
        `;
    }).join('');
}


// ─── Book Detail Modal ──────────────────────────────────────

async function openBookDetail(workId) {
    if (!workId) return;

    // Create or reuse modal
    let modal = document.getElementById('bookDetailModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'bookDetailModal';
        modal.className = 'book-modal-overlay';
        document.body.appendChild(modal);
    }

    // Show loading state
    modal.innerHTML = `
        <div class="book-modal">
            <button class="modal-close" onclick="closeBookDetail()">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
            <div class="book-modal-body" style="text-align:center;padding:3rem;">
                <div class="skeleton" style="width:60%;height:20px;margin:0 auto 1rem;"></div>
                <div class="skeleton" style="width:40%;height:14px;margin:0 auto;"></div>
            </div>
        </div>
    `;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    try {
        const book = await api.getBookDetails(workId);
        
        if (book.error) {
            showToast('Could not load book details', 'error');
            closeBookDetail();
            return;
        }

        const coverHtml = book.cover_url
            ? `<img src="${book.cover_url}" alt="${book.title}" class="detail-cover-img">`
            : `<div class="detail-cover-placeholder">${book.title}</div>`;

        const subjects = (book.subjects || []).slice(0, 6).map(s => 
            `<span class="detail-tag">${s}</span>`
        ).join('');

        const authors = (book.authors || []).join(', ');
        const description = book.description || 'No description available for this book.';
        const pages = book.pages ? `${book.pages} pages` : '';
        const published = book.first_published || '';

        modal.querySelector('.book-modal').innerHTML = `
            <button class="modal-close" onclick="closeBookDetail()">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
            <div class="book-modal-body">
                <div class="detail-header">
                    <div class="detail-cover">
                        ${coverHtml}
                    </div>
                    <div class="detail-meta">
                        <h2 class="detail-title">${book.title}</h2>
                        <p class="detail-author">by ${authors}</p>
                        <div class="detail-stats">
                            ${published ? `<span class="detail-stat">📅 ${published}</span>` : ''}
                            ${pages ? `<span class="detail-stat">📖 ${pages}</span>` : ''}
                        </div>
                        <div class="detail-actions">
                            <button class="btn btn-primary btn-sm" onclick="addToList('${book.title.replace(/'/g, "\\'")}', '${authors.replace(/'/g, "\\'")}', '')">
                                ${icons.plus} Add to Reading List
                            </button>
                            <a href="${book.ol_url}" target="_blank" rel="noopener" class="btn btn-secondary btn-sm">
                                View on Open Library ↗
                            </a>
                        </div>
                    </div>
                </div>
                <div class="detail-description">
                    <h3>About This Book</h3>
                    <p>${description}</p>
                </div>
                ${subjects ? `
                <div class="detail-subjects">
                    <h3>Subjects & Genres</h3>
                    <div class="detail-tags">${subjects}</div>
                </div>` : ''}
            </div>
        `;

    } catch (err) {
        console.error('Book detail error:', err);
        showToast('Failed to load book details', 'error');
        closeBookDetail();
    }
}


function closeBookDetail() {
    const modal = document.getElementById('bookDetailModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Close on overlay click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('book-modal-overlay')) {
        closeBookDetail();
    }
});

// Close on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeBookDetail();
});


async function addToList(title, author, genre) {
    try {
        await api.addToReadingList({ title, author, genre });
        showToast(`"${title}" added to your reading list`);
    } catch {
        showToast(`"${title}" saved locally`, 'warning');
    }
}
