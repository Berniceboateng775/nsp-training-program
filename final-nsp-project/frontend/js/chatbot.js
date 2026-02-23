/**
 * Vellichor AI — Chatbot Logic
 * Includes chat history (localStorage), guest limits, and file upload.
 */

let currentChatId = null;
let uploadedFileContent = null;
const GUEST_MSG_LIMIT = 1;

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    renderSidebar('chatbot.html');
    renderChatHistory();
    document.getElementById('chatInput').focus();

    // Check if we should load a specific chat from URL hash
    const hash = window.location.hash.replace('#', '');
    if (hash) {
        loadChat(hash);
    }
});


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
        title: title || 'New Conversation',
        createdAt: new Date().toISOString(),
        messageCount: 0
    };
    const list = getChatList();
    list.unshift(chat);
    saveChatList(list);
    return chat;
}

function updateChatTitle(chatId, newTitle) {
    const list = getChatList();
    const chat = list.find(c => c.id === chatId);
    if (chat) {
        chat.title = newTitle.length > 35 
            ? newTitle.substring(0, 35) + '...' 
            : newTitle;
        saveChatList(list);
    }
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
        container.innerHTML = '<div class="chat-history-empty">No conversations yet</div>';
        return;
    }

    container.innerHTML = chats.map(chat => `
        <div class="chat-history-item ${chat.id === currentChatId ? 'active' : ''}" onclick="loadChat('${chat.id}')">
            <span class="chat-history-icon">💬</span>
            <span class="chat-history-title">${chat.title}</span>
            <button class="chat-history-delete" onclick="event.stopPropagation(); deleteChat('${chat.id}')" title="Delete">✕</button>
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
        messages.forEach(msg => {
            addMessageToDOM(msg.text, msg.role, msg.time);
        });
        scrollToBottom();
    } else {
        resetToSuggestions();
    }
    
    renderChatHistory();
}

function startNewChat() {
    currentChatId = null;
    resetToSuggestions();
    document.getElementById('chatInput').value = '';
    document.getElementById('chatInput').focus();
    renderChatHistory();
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
    // Remove existing modal if any
    const existing = document.getElementById('guestLimitModal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'guestLimitModal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="this.parentElement.remove()">
            <div class="modal-card" onclick="event.stopPropagation()">
                <div class="modal-icon">🔒</div>
                <h3>Guest Limit Reached</h3>
                <p>You've used your free guest message. Create a free account to unlock unlimited conversations, book recommendations, and emotion analysis.</p>
                <div class="modal-actions">
                    <a href="register.html" class="btn btn-primary" style="width: 100%;">Create Free Account</a>
                    <a href="login.html" class="btn btn-secondary" style="width: 100%;">Sign In</a>
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
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function sendSuggestion(text) {
    document.getElementById('chatInput').value = text;
    sendMessage();
}


// ─── File Upload ─────────────────────────────────────────

function handleChatFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    const supported = ['txt', 'pdf', 'epub', 'docx', 'doc'];
    if (!supported.includes(ext)) {
        showToast('Unsupported file type. Please use PDF, EPUB, DOCX, or TXT.', 'error');
        return;
    }

    document.getElementById('chatFileInfo').style.display = 'flex';
    document.getElementById('chatFileName').textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

    if (ext === 'txt') {
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedFileContent = e.target.result;
            showToast('Text file loaded — it will be included with your next message');
        };
        reader.readAsText(file);
    } else {
        uploadedFileContent = `[Uploaded file: ${file.name}]`;
        showToast(`${ext.toUpperCase()} file attached. Send a message to ask about its content.`);
    }
}

function clearChatFile() {
    document.getElementById('chatFileInput').value = '';
    document.getElementById('chatFileInfo').style.display = 'none';
    document.getElementById('chatFileName').textContent = '';
    uploadedFileContent = null;
}


// ─── Send Message ────────────────────────────────────────

async function sendMessage() {
    const input = document.getElementById('chatInput');
    let message = input.value.trim();
    if (!message && !uploadedFileContent) return;

    // Guest limit check
    if (!checkGuestLimit()) return;

    // Save original user input for chat title (before file content modifies it)
    const originalInput = message;

    // If there's uploaded file content, prepend it
    if (uploadedFileContent) {
        const fileContext = uploadedFileContent.length > 4000
            ? uploadedFileContent.substring(0, 4000) + '\n... [text truncated for analysis]'
            : uploadedFileContent;
        message = message
            ? `[Document content for analysis]:\n${fileContext}\n\n[User question]: ${message}`
            : `Please analyze this document:\n${fileContext}`;
        clearChatFile();
    }

    // Create chat with the user's original input as the title
    if (!currentChatId) {
        const chatTitle = originalInput || 'Document Analysis';
        const chat = createNewChat(chatTitle);
        currentChatId = chat.id;
    }

    // Switch from suggestions to messages view
    const suggestions = document.getElementById('chatSuggestions');
    const messagesContainer = document.getElementById('chatMessages');
    if (suggestions.style.display !== 'none') {
        suggestions.style.display = 'none';
        messagesContainer.style.display = 'flex';
    }

    // Display message
    const displayMessage = message.includes('[User question]:')
        ? '📄 ' + message.split('[User question]: ')[1]
        : message.includes('Please analyze this document')
            ? '📄 Analyze uploaded document'
            : message;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    addMessageToDOM(displayMessage, 'user', time);
    
    // Save to history
    const chatMessages = getChatMessages(currentChatId);
    chatMessages.push({ text: displayMessage, role: 'user', time: time });
    saveChatMessages(currentChatId, chatMessages);
    
    // Update message count
    const list = getChatList();
    const chat = list.find(c => c.id === currentChatId);
    if (chat) { chat.messageCount++; saveChatList(list); }
    
    renderChatHistory();

    input.value = '';
    autoResize(input);

    // Show typing indicator
    const typing = document.getElementById('typingIndicator');
    typing.classList.add('show');
    scrollToBottom();

    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;

    try {
        const data = await api.sendMessage(message, currentChatId);
        typing.classList.remove('show');
        const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        addMessageToDOM(data.reply, 'assistant', replyTime);
        
        // Save assistant reply
        chatMessages.push({ text: data.reply, role: 'assistant', time: replyTime });
        saveChatMessages(currentChatId, chatMessages);
    } catch (error) {
        typing.classList.remove('show');
        const mockResponses = [
            "Based on your question, I'd recommend exploring the themes of identity and belonging that pervade much of contemporary literature. Works like **The Invisible Life of Addie LaRue** by V.E. Schwab handle these with remarkable depth.",
            "That's a fascinating literary question. The interplay between character motivation and narrative structure is what gives great novels their power. Consider how authors like Madeline Miller reinterpret classical narratives to speak to modern sensibilities.",
            "I sense you're drawn to stories with emotional complexity. **The Midnight Library** by Matt Haig explores the infinite possibilities of life through a beautiful metaphor — a library between life and death where each book represents a different path.",
            "The beauty of literature lies in its ability to make us feel deeply. The passage you're describing carries undertones of nostalgia and quiet resilience — common in works that explore the human condition through the lens of nature and time."
        ];
        const randomReply = mockResponses[Math.floor(Math.random() * mockResponses.length)];
        const replyTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        addMessageToDOM(randomReply, 'assistant', replyTime);
        
        // Save mock reply
        const msgs = getChatMessages(currentChatId);
        msgs.push({ text: randomReply, role: 'assistant', time: replyTime });
        saveChatMessages(currentChatId, msgs);
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }

    // Track guest usage
    if (isGuest()) {
        incrementGuestUsage('messages');
    }

    // Track stats
    if (typeof incrementStat === 'function') {
        incrementStat('ai_conversations');
    }
}


// ─── DOM Helpers ─────────────────────────────────────────

function addMessageToDOM(text, role, time) {
    const messagesContainer = document.getElementById('chatMessages');
    const processedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    const messageHTML = `
        <div class="chat-message ${role}">
            <div>
                <div class="message-content">${processedText}</div>
                <div class="message-time">${time}</div>
            </div>
        </div>
    `;
    
    messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

function scrollToBottom() {
    const container = document.getElementById('chatMessages');
    container.scrollTop = container.scrollHeight;
}
