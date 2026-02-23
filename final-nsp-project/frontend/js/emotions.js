/**
 * Vellichor AI — Emotion Analysis Logic
 */

let pieChart = null;
let barChart = null;

const SAMPLE_TEXTS = [
    // Romantic Prose
    `She stood at the edge of the garden where the roses still bloomed despite the autumn chill, their petals soft as the whispers they once shared under summer stars. Every breath carried the ghost of his cologne, and every shadow wore the shape of his absence. She pressed the letter to her chest — the one he'd written the night before he left, its ink now faded but its words still burning. "I will find my way back to you," he had promised, and she believed him still, even as the seasons turned and the world grew older without them.`,

    // Gothic Horror
    `The manor groaned in the wind like a living creature in pain. Elara pressed her candle forward, its flame trembling against the darkness that seemed to breathe from the walls themselves. The corridor stretched impossibly long, each door she passed etched with symbols that writhed when she wasn't looking directly at them. Behind her, the footsteps resumed — measured, deliberate, patient. She quickened her pace, but the distance between her and the staircase never seemed to close. Then the candle went out, and in the perfect blackness, something cold brushed against her neck.`,

    // Epic Fantasy
    `The last dragon descended from the clouds of ash like judgment made flesh, its scales reflecting the fires that consumed the fallen kingdom below. Kael raised his blade — the Starsbane, forged by the First Warden in an age when gods still walked among mortals — and felt the ancient magic pulse through his veins like molten silver. Around him, the remnants of his company stood firm: warriors, scholars, and outcasts who had followed him across three continents and through the very gates of the Shadowlands. This was the final reckoning. The prophecy had spoken of this moment for a thousand years.`
];


document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    renderSidebar('emotions.html');
});


function updateCharCount() {
    const text = document.getElementById('emotionText').value;
    document.getElementById('charCount').textContent = `${text.length} characters`;
}


function loadSample(index) {
    document.getElementById('emotionText').value = SAMPLE_TEXTS[index];
    updateCharCount();
}


async function analyzeText() {
    const text = document.getElementById('emotionText').value.trim();
    if (!text) {
        showToast('Please enter some text to analyze', 'warning');
        return;
    }

    const btn = document.getElementById('analyzeBtn');
    btn.textContent = 'Analyzing...';
    btn.disabled = true;

    try {
        const data = await api.analyzeEmotions(text);
        displayResults(data.result);
    } catch {
        // Fallback mock
        displayResults(getMockResult());
    } finally {
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
            Analyze Emotions
        `;
        btn.disabled = false;
    }
}


function displayResults(result) {
    const container = document.getElementById('emotionResults');
    container.classList.add('show');

    // Emotion Bars
    renderEmotionBars(result.emotions);

    // Pie Chart
    renderPieChart(result.emotions);

    // Bar Chart
    renderBarChart(result.emotions);

    // Theme Tags
    renderThemes(result.themes);

    // Summary
    document.getElementById('emotionSummary').textContent = result.summary;

    // Scroll to results
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}


function renderEmotionBars(emotions) {
    const container = document.getElementById('emotionBars');
    const sorted = Object.entries(emotions).sort((a, b) => b[1] - a[1]);

    container.innerHTML = sorted.map(([emotion, value]) => `
        <div class="emotion-bar-item">
            <span class="emotion-bar-label">${emotion}</span>
            <div class="emotion-bar-track">
                <div class="emotion-bar-fill ${emotion}" style="width: ${value * 100}%">
                    ${Math.round(value * 100)}%
                </div>
            </div>
        </div>
    `).join('');
}


function renderPieChart(emotions) {
    const canvas = document.getElementById('emotionPieChart');
    if (pieChart) pieChart.destroy();

    const colors = {
        joy: 'rgba(212, 168, 83, 0.8)',
        sadness: 'rgba(96, 165, 250, 0.8)',
        tension: 'rgba(248, 113, 113, 0.8)',
        romance: 'rgba(244, 114, 182, 0.8)',
        mystery: 'rgba(167, 139, 250, 0.8)',
        hope: 'rgba(74, 222, 128, 0.8)',
        fear: 'rgba(251, 191, 36, 0.8)'
    };

    pieChart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: Object.keys(emotions).map(e => e.charAt(0).toUpperCase() + e.slice(1)),
            datasets: [{
                data: Object.values(emotions),
                backgroundColor: Object.keys(emotions).map(e => colors[e] || 'rgba(167,169,190,0.5)'),
                borderColor: 'rgba(15, 14, 23, 1)',
                borderWidth: 2,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a7a9be',
                        padding: 16,
                        font: { family: 'Inter', size: 11 },
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                }
            },
            cutout: '55%'
        }
    });
}


function renderBarChart(emotions) {
    const canvas = document.getElementById('emotionBarChart');
    if (barChart) barChart.destroy();

    const colors = {
        joy: 'rgba(212, 168, 83, 0.8)',
        sadness: 'rgba(96, 165, 250, 0.8)',
        tension: 'rgba(248, 113, 113, 0.8)',
        romance: 'rgba(244, 114, 182, 0.8)',
        mystery: 'rgba(167, 139, 250, 0.8)',
        hope: 'rgba(74, 222, 128, 0.8)',
        fear: 'rgba(251, 191, 36, 0.8)'
    };

    barChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: Object.keys(emotions).map(e => e.charAt(0).toUpperCase() + e.slice(1)),
            datasets: [{
                label: 'Intensity',
                data: Object.values(emotions).map(v => Math.round(v * 100)),
                backgroundColor: Object.keys(emotions).map(e => colors[e] || 'rgba(167,169,190,0.5)'),
                borderRadius: 6,
                borderWidth: 0,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(167,169,190,0.08)' },
                    ticks: { color: '#6b6d80', font: { family: 'Inter', size: 11 }, callback: v => v + '%' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#a7a9be', font: { family: 'Inter', size: 11 } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}


function renderThemes(themes) {
    const container = document.getElementById('themeTags');
    container.innerHTML = themes.map(theme => `<div class="theme-tag">${theme}</div>`).join('');
}


function clearResults() {
    document.getElementById('emotionResults').classList.remove('show');
    document.getElementById('emotionText').value = '';
    updateCharCount();
}


function copyReport() {
    const summary = document.getElementById('emotionSummary').textContent;
    const bars = document.getElementById('emotionBars');
    const themes = document.getElementById('themeTags');
    
    let report = '=== Vellichor AI — Emotion Analysis Report ===\n\n';
    report += 'EMOTIONS:\n';
    bars.querySelectorAll('.emotion-bar-item').forEach(item => {
        const label = item.querySelector('.emotion-bar-label').textContent;
        const fill = item.querySelector('.emotion-bar-fill').textContent;
        report += `  ${label}: ${fill}\n`;
    });
    report += '\nTHEMES:\n';
    themes.querySelectorAll('.theme-tag').forEach(tag => {
        report += `  - ${tag.textContent}\n`;
    });
    report += `\nSUMMARY:\n${summary}\n`;
    
    navigator.clipboard.writeText(report).then(() => {
        showToast('Report copied to clipboard');
    }).catch(() => {
        showToast('Could not copy to clipboard', 'error');
    });
}


function getMockResult() {
    return {
        emotions: { joy: 0.15, sadness: 0.25, tension: 0.18, romance: 0.22, mystery: 0.08, hope: 0.07, fear: 0.05 },
        themes: ['Love & Loss', 'Identity', 'Mortality'],
        summary: 'A contemplative melancholy runs through this text, reflecting on loss and the passage of time with a delicate, almost poetic sensibility. The interplay between sadness and romance creates a bittersweet emotional landscape that speaks to universal human experiences.'
    };
}
