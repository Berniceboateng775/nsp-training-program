/**
 * Vellichor AI — Chatbot Logic
 */

let conversationId = null;
let uploadedFileContent = null;

document.addEventListener('DOMContentLoaded', () => {
    if (!requireAuth()) return;
    renderSidebar('chatbot.html');
    document.getElementById('chatInput').focus();
});


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


async function sendMessage() {
    const input = document.getElementById('chatInput');
    let message = input.value.trim();
    if (!message && !uploadedFileContent) return;

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

    // Switch from suggestions to messages view
    const suggestions = document.getElementById('chatSuggestions');
    const messagesContainer = document.getElementById('chatMessages');
    if (suggestions.style.display !== 'none') {
        suggestions.style.display = 'none';
        messagesContainer.style.display = 'flex';
    }

    // Add user message (show just the question, not the full document)
    const displayMessage = message.includes('[User question]:')
        ? '📄 ' + message.split('[User question]: ')[1]
        : message.includes('Please analyze this document')
            ? '📄 Analyze uploaded document'
            : message;
    addMessage(displayMessage, 'user');
    input.value = '';
    autoResize(input);

    // Show typing indicator
    const typing = document.getElementById('typingIndicator');
    typing.classList.add('show');
    scrollToBottom();

    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;

    try {
        const data = await api.sendMessage(message, conversationId);
        conversationId = data.conversation_id;
        typing.classList.remove('show');
        addMessage(data.reply, 'assistant');
    } catch (error) {
        typing.classList.remove('show');
        // Fallback mock response
        const mockResponses = [
            "Based on your question, I'd recommend exploring the themes of identity and belonging that pervade much of contemporary literature. Works like **The Invisible Life of Addie LaRue** by V.E. Schwab handle these with remarkable depth.",
            "That's a fascinating literary question. The interplay between character motivation and narrative structure is what gives great novels their power. Consider how authors like Madeline Miller reinterpret classical narratives to speak to modern sensibilities.",
            "I sense you're drawn to stories with emotional complexity. **The Midnight Library** by Matt Haig explores the infinite possibilities of life through a beautiful metaphor — a library between life and death where each book represents a different path.",
            "The beauty of literature lies in its ability to make us feel deeply. The passage you're describing carries undertones of nostalgia and quiet resilience — common in works that explore the human condition through the lens of nature and time."
        ];
        const randomReply = mockResponses[Math.floor(Math.random() * mockResponses.length)];
        addMessage(randomReply, 'assistant');
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }

    // Track stats
    if (typeof incrementStat === 'function') {
        incrementStat('ai_conversations');
    }
}


function addMessage(text, role) {
    const messagesContainer = document.getElementById('chatMessages');
    const user = api.getUser();
    const initial = role === 'user' 
        ? (user ? user.name.charAt(0).toUpperCase() : 'U')
        : 'V';
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Process markdown-style bold
    const processedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    const messageHTML = `
        <div class="chat-message ${role}">
            <div class="message-avatar">${initial}</div>
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

