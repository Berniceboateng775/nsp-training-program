/**
 * Vellichor AI — Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth()) return;
    renderSidebar('dashboard.html');

    const user = api.getUser();
    const welcomeEl = document.getElementById('welcomeMsg');
    if (user && user.name) {
        welcomeEl.textContent = `Welcome back, ${user.name}`;
    }

    // Load trending books for the dashboard
    await loadRecentBooks();
});


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
    const coverColors = [
        'rgba(212,168,83,0.15)',
        'rgba(184,64,94,0.15)',
        'rgba(96,165,250,0.15)',
        'rgba(74,222,128,0.15)'
    ];
    const randomColor = coverColors[Math.floor(Math.random() * coverColors.length)];
    
    return `
        <div class="book-card">
            <div class="book-cover" style="background: ${randomColor};">
                <span style="opacity: 0.6; position: relative; z-index: 1;">${book.title.substring(0, 20)}</span>
            </div>
            <div class="book-info">
                <div class="book-title">${book.title}</div>
                <div class="book-author">${book.author}</div>
                <div class="book-genre">${book.genre}</div>
                <div class="book-description">${book.description}</div>
                <div class="book-rating">
                    ${icons.star} ${book.rating}
                </div>
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
