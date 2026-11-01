/**
 * Vellichor AI — Chatbot Logic
 * Includes chat history (localStorage), conversation memory, guest limits,
 * and document upload (PDF/TXT are indexed server-side for context).
 */

let currentChatId = null;
let attachedTextContent = null;   // TXT contents, sent inline with the next message
let isSending = false;
let lastFailedMessage = null;
const GUEST_MSG_LIMIT = 1;
const HISTORY_TURNS_SENT = 12;

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    renderSidebar('chatbot.html');
    renderChatHistory();
    document.getElementById('chatInput').focus();
    wakeServer();

    // Check if we should load a specific chat from URL hash
    const hash = window.location.hash.replace('#', '');
    if (hash) {
        loadChat(hash);
    }
});


// ─── Server wake-up ──────────────────────────────────────
// The backend sleeps on Render's free tier; ping it as soon as the page
// opens so it's awake by the time the first message is sent.

async function wakeServer() {
    const status = document.getElementById('serverStatus');
    const slowTimer = setTimeout(() => {
        status.hidden = false;
        status.textContent = 'Waking up the server…';
    }, 2500);
    try {
        await api.health();
        status.hidden = true;
    } catch {
        status.hidden = false;
        status.textContent = "Can't reach the server right now";
        status.classList.add('is-error');
    } finally {
        clearTimeout(slowTimer);
    }
}


// ─── Chat History (localStorage) ─────────────────────────

function getChatList() {
    const data = localStorage.getItem('vellichor_chats');
    return data ? JSON.parse(data) : [];
}

function saveChatList(list) {
    localStorage.setItem('vellichor_chats', JSON.stringify(list));
}

function getChatMessages(chatId) {
    const data = localStorage.getItem(`vellichor_chat_${chatId}`);
    return data ? JSON.parse(data) : [];
}

function saveChatMessages(chatId, messages) {
    localStorage.setItem(`vellichor_chat_${chatId}`, JSON.stringify(messages));
}

function createNewChat(title) {
    const id = 'chat_' + Date.now();
    const chat = {
        id: id,
        title: (title || 'New chat').substring(0, 40),
        createdAt: new Date().toISOString(),
        messageCount: 0
    };
    const list = getChatList();
    list.unshift(chat);
    saveChatList(list);
    return chat;
}

function deleteChat(chatId) {
    let list = getChatList();
    list = list.filter(c => c.id !== chatId);
    saveChatList(list);
    localStorage.removeItem(`vellichor_chat_${chatId}`);
    if (currentChatId === chatId) {
        currentChatId = null;
        resetToSuggestions();
    }
    renderChatHistory();
}


// ─── Render Chat History in Sidebar ──────────────────────

function renderChatHistory() {
    const container = document.getElementById('chatHistoryList');
    if (!container) return;

    const chats = getChatList();
    if (chats.length === 0) {
        container.innerHTML = '<div class="chat-history-empty">Nothing yet. Say hi.</div>';
        return;
    }

    container.innerHTML = chats.map(chat => `
        <div class="chat-history-item ${chat.id === currentChatId ? 'active' : ''}" onclick="loadChat('${chat.id}')">
            <span class="chat-history-title">${escapeHTML(chat.title)}</span>
            <button class="chat-history-delete" onclick="event.stopPropagation(); deleteChat('${chat.id}')" title="Delete" aria-label="Delete chat">✕</button>
        </div>
    `).join('');
}


// ─── Load / Start Chats ──────────────────────────────────

function loadChat(chatId) {
    currentChatId = chatId;
    const messages = getChatMessages(chatId);

    const suggestions = document.getElementById('chatSuggestions');
    const messagesContainer = document.getElementById('chatMessages');

    if (messages.length > 0) {
        suggestions.style.display = 'none';
        messagesContainer.style.display = 'flex';
        messagesContainer.innerHTML = '';
        messages.forEach(msg => addMessageToDOM(msg.text, msg.role, msg.time));
        scrollToBottom();
    } else {
        resetToSuggestions();
    }

    renderChatHistory();
    closeSidebar();
}

function startNewChat() {
    currentChatId = null;
    resetToSuggestions();
    document.getElementById('chatInput').value = '';
    document.getElementById('chatInput').focus();
    renderChatHistory();
    closeSidebar();
}

function resetToSuggestions() {
    const suggestions = document.getElementById('chatSuggestions');
    const messagesContainer = document.getElementById('chatMessages');
    suggestions.style.display = '';
    messagesContainer.style.display = 'none';
    messagesContainer.innerHTML = '';
}


// ─── Guest Limits ────────────────────────────────────────

function isGuest() {
    const user = api.getUser();
    return user && user.id === 'guest';
}

function getGuestUsage() {
    const data = localStorage.getItem('vellichor_guest_usage');
    return data ? JSON.parse(data) : { messages: 0, analyses: 0 };
}

function incrementGuestUsage(type) {
    const usage = getGuestUsage();
    usage[type] = (usage[type] || 0) + 1;
    localStorage.setItem('vellichor_guest_usage', JSON.stringify(usage));
    return usage;
}

function checkGuestLimit() {
    if (!isGuest()) return true;
    const usage = getGuestUsage();
    if (usage.messages >= GUEST_MSG_LIMIT) {
        showGuestLimitModal();
        return false;
    }
    return true;
}

function showGuestLimitModal() {
    const existing = document.getElementById('guestLimitModal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'guestLimitModal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="this.parentElement.remove()">
            <div class="modal-card" onclick="event.stopPropagation()">
                <h3>Liking it so far?</h3>
                <p>That was your free guest message. Make a free account to keep chatting, save your chats, and upload PDFs.</p>
                <div class="modal-actions">
                    <a href="register.html" class="btn btn-primary btn-lg">Create a free account</a>
                    <a href="login.html" class="btn btn-secondary btn-lg">Log in</a>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}


// ─── Keyboard & Input ────────────────────────────────────

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
}

function sendSuggestion(text) {
    document.getElementById('chatInput').value = text;
    sendMessage();
}


// ─── File Upload ─────────────────────────────────────────
// TXT is read in the browser and sent with the next message.
// PDF is uploaded and indexed on the server, so every later question
// in the chat can pull the relevant passages.

async function handleChatFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['txt', 'pdf'].includes(ext)) {
        showToast('Only PDF and TXT files work here.', 'error');
        event.target.value = '';
        return;
    }

    const info = document.getElementById('chatFileInfo');
    const label = document.getElementById('chatFileName');
    info.style.display = 'flex';
    label.textContent = `${file.name} · ${(file.size / 1024).toFixed(0)} KB`;

    if (ext === 'txt') {
        const reader = new FileReader();
        reader.onload = (e) => {
            attachedTextContent = e.target.result;
            showToast('Text attached. It goes with your next message.');
        };
        reader.readAsText(file);
        return;
    }

    if (isGuest()) {
        showToast('Make a free account to upload PDFs.', 'warning');
        clearChatFile();
        return;
    }

    label.textContent = `Reading ${file.name}…`;
    try {
        const result = await api.uploadChatDocument(file);
        label.textContent = `${file.name} · ready (${result.total_chunks} passages)`;
        showToast('PDF ready. Ask me anything about it.');
    } catch (error) {
        showToast(error.message || 'Could not read that PDF.', 'error');
        clearChatFile();
    }
}

function clearChatFile() {
    document.getElementById('chatFileInput').value = '';
    document.getElementById('chatFileInfo').style.display = 'none';
    document.getElementById('chatFileName').textContent = '';
    attachedTextContent = null;
}


// ─── Send Message ────────────────────────────────────────

async function sendMessage(retryText = null) {
    if (isSending) return;
    const input = document.getElementById('chatInput');
    const typed = (retryText ?? input.value).trim();
    if (!typed && !attachedTextContent) return;

    if (!checkGuestLimit()) return;

    // Build the message actually sent to the model
    let message = typed;
    let displayMessage = typed;
    if (attachedTextContent && !retryText) {
        const fileContext = attachedTextContent.length > 6000
            ? attachedTextContent.substring(0, 6000) + '\n…[truncated]'
            : attachedTextContent;
        message = typed
            ? `Here is a document I'm reading:\n\n${fileContext}\n\nMy question: ${typed}`
            : `Here is a document I'm reading. What's going on in it, and how does it feel?\n\n${fileContext}`;
        displayMessage = typed ? `📎 ${typed}` : '📎 What\'s going on in this document?';
        clearChatFile();
    }

    if (!currentChatId) {
        currentChatId = createNewChat(typed || 'Document chat').id;
    }

    const suggestions = document.getElementById('chatSuggestions');
    const messagesContainer = document.getElementById('chatMessages');
    suggestions.style.display = 'none';
    messagesContainer.style.display = 'flex';

    // Conversation memory: previous turns, oldest first (before this message)
    const chatMessages = getChatMessages(currentChatId);
    const history = chatMessages
        .filter(m => m.role === 'user' || m.role === 'assistant')
        .slice(-HISTORY_TURNS_SENT)
        .map(m => ({ role: m.role, content: m.sent || m.text }));

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    if (!retryText) {
        addMessageToDOM(displayMessage, 'user', time);
        chatMessages.push({ text: displayMessage, sent: message, role: 'user', time });
        saveChatMessages(currentChatId, chatMessages);
        bumpChatCount();
    }
    removeErrorBubbles();

    input.value = '';
    autoResize(input);

    const typing = showTyping();
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    isSending = true;

    try {
        const data = await api.sendMessage(message, currentChatId, history);
        typing.remove();
        const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        addMessageToDOM(data.reply, 'assistant', replyTime);

        const msgs = getChatMessages(currentChatId);
        msgs.push({ text: data.reply, role: 'assistant', time: replyTime });
        saveChatMessages(currentChatId, msgs);
        lastFailedMessage = null;

        if (isGuest()) incrementGuestUsage('messages');
        const stats = JSON.parse(localStorage.getItem('vellichor_stats') || '{}');
        stats.ai_conversations = (stats.ai_conversations || 0) + 1;
        localStorage.setItem('vellichor_stats', JSON.stringify(stats));
    } catch (error) {
        typing.remove();
        lastFailedMessage = message;
        addErrorBubble(error);
    } finally {
        sendBtn.disabled = false;
        isSending = false;
        input.focus();
    }
}

function bumpChatCount() {
    const list = getChatList();
    const chat = list.find(c => c.id === currentChatId);
    if (chat) { chat.messageCount++; saveChatList(list); }
    renderChatHistory();
}

function retryLastMessage() {
    if (lastFailedMessage) sendMessage(lastFailedMessage);
}


// ─── DOM Helpers ─────────────────────────────────────────

/** Minimal, safe markdown: escapes HTML first, then bold/italic/code/lists/paragraphs. */
function renderMarkdown(text) {
    const safe = escapeHTML(text);
    const inline = (s) => s
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/(^|[^*])\*(?!\s)(.+?)\*(?!\*)/g, '$1<em>$2</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');

    const blocks = [];
    let list = null;
    for (const raw of safe.split('\n')) {
        const line = raw.trimEnd();
        const bullet = line.match(/^\s*(?:[-*•]|\d+[.)])\s+(.*)$/);
        if (bullet) {
            const ordered = /^\s*\d/.test(line);
            if (!list || list.ordered !== ordered) {
                if (list) blocks.push(list);
                list = { ordered, items: [] };
            }
            list.items.push(inline(bullet[1]));
            continue;
        }
        if (list) { blocks.push(list); list = null; }
        if (line.trim() === '') { blocks.push(null); continue; }
        const heading = line.match(/^#{1,4}\s+(.*)$/);
        blocks.push(heading ? `<p><strong>${inline(heading[1])}</strong></p>` : inline(line));
    }
    if (list) blocks.push(list);

    // Join consecutive text lines into paragraphs
    let html = '';
    let para = [];
    const flush = () => { if (para.length) { html += `<p>${para.join('<br>')}</p>`; para = []; } };
    for (const b of blocks) {
        if (b === null) { flush(); continue; }
        if (typeof b === 'object') {
            flush();
            const tag = b.ordered ? 'ol' : 'ul';
            html += `<${tag}>${b.items.map(i => `<li>${i}</li>`).join('')}</${tag}>`;
            continue;
        }
        if (b.startsWith('<p>')) { flush(); html += b; continue; }
        para.push(b);
    }
    flush();
    return html;
}

function addMessageToDOM(text, role, time) {
    const messagesContainer = document.getElementById('chatMessages');
    const content = role === 'assistant' ? renderMarkdown(text) : escapeHTML(text).replace(/\n/g, '<br>');

    messagesContainer.insertAdjacentHTML('beforeend', `
        <div class="chat-message ${role}">
            <div class="message-content">${content}</div>
            <div class="message-time">${escapeHTML(time || '')}</div>
        </div>
    `);
    scrollToBottom();
}

function showTyping() {
    const messagesContainer = document.getElementById('chatMessages');
    const el = document.createElement('div');
    el.className = 'typing-indicator';
    el.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    messagesContainer.appendChild(el);
    scrollToBottom();
    return el;
}

function addErrorBubble(error) {
    const messagesContainer = document.getElementById('chatMessages');
    const offline = error instanceof TypeError; // fetch() network failure
    const reason = offline
        ? "I couldn't reach the server. It might still be waking up."
        : (error.message || 'Something went wrong on my end.');
    messagesContainer.insertAdjacentHTML('beforeend', `
        <div class="chat-message assistant chat-error">
            <div class="message-content">
                <p>${escapeHTML(reason)}</p>
                <button class="btn btn-secondary btn-sm" onclick="retryLastMessage()">Try again</button>
            </div>
        </div>
    `);
    scrollToBottom();
}

function removeErrorBubbles() {
    document.querySelectorAll('.chat-error').forEach(el => el.remove());
}

function scrollToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}
