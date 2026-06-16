// --- GLOBAL STATES ---
let currentTab = 'chat';
let globalTTSEnabled = false; // Disable auto-readout by default to avoid abrupt audio
let currentSpeechUtterance = null;
let currentSpeakerButton = null;

// Quiz State
let quizQuestions = [];
let quizCurrentIndex = 0;
let quizScore = 0;
let quizAnswered = false;

// --- PAGE INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
    // Poll model status on startup
    checkModelStatus();
    setInterval(checkModelStatus, 5000); // Check every 5 seconds
    
    // Auto-adjust textarea height on input
    const inputArea = document.getElementById("chat-input");
    inputArea.addEventListener("input", function() {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight) + "px";
    });

    // Load Timeline data
    loadTimelineData();
});

// --- TAB SWITCHING ---
function switchTab(tabName) {
    if (currentTab === tabName) return;
    
    // Stop speaking when switching tabs
    stopSpeaking();

    // Toggle active view
    document.querySelectorAll(".view-section").forEach(view => {
        view.classList.remove("active");
    });
    document.getElementById(`view-${tabName}`).classList.add("active");

    // Toggle active button
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.classList.remove("active");
    });
    document.getElementById(`btn-${tabName}`).classList.add("active");

    currentTab = tabName;
}

// --- MODEL STATUS POLLING ---
async function checkModelStatus() {
    try {
        const response = await fetch("/api/status");
        const data = await response.json();
        const statusText = document.getElementById("status-text");
        const statusDot = document.getElementById("status-dot");
        
        statusText.textContent = data.status;
        
        if (data.status.includes("Ready")) {
            statusDot.className = "status-dot ready";
        } else {
            statusDot.className = "status-dot pulsing";
        }
    } catch (e) {
        console.error("Error fetching model status: ", e);
    }
}

// --- CHAT INTERACTION & LOGIC ---

// Cache conversation history locally
let chatMessages = [
    {
        role: "system",
        content: "You are an expert history tutor trained on Indian History NCERT textbooks. Answer the user's question accurately based on NCERT guidelines."
    }
];

function handleEnter(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendSuggested(queryText) {
    switchTab('chat');
    const inputArea = document.getElementById("chat-input");
    inputArea.value = queryText;
    sendMessage();
}

async function sendMessage() {
    const inputArea = document.getElementById("chat-input");
    const query = inputArea.value.trim();
    if (!query) return;

    // Clear and reset height
    inputArea.value = "";
    inputArea.style.height = "auto";

    // 1. Append User Bubble
    appendMessage("user", query);
    chatMessages.push({ role: "user", content: query });

    // 2. Append Typing Indicator
    const messageArea = document.getElementById("message-area");
    const typingBubble = document.createElement("div");
    typingBubble.className = "message bot-message typing-indicator-bubble";
    typingBubble.innerHTML = `
        <div class="avatar"><i class="fa-solid fa-building-columns"></i></div>
        <div class="message-content">
            <div class="message-header">
                <span class="sender-name">Chronicles of India Bot</span>
                <span class="timestamp">Thinking</span>
            </div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messageArea.appendChild(typingBubble);
    messageArea.scrollTop = messageArea.scrollHeight;

    // 3. Query API
    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ messages: chatMessages })
        });
        
        if (!response.ok) throw new Error("API call failed");
        
        const data = await response.json();
        
        // Remove typing indicator
        messageArea.removeChild(typingBubble);
        
        // Append Bot response
        appendMessage("bot", data.answer, data.sources);
        chatMessages.push({ role: "assistant", content: data.answer });

        // Auto TTS if enabled globally
        if (globalTTSEnabled) {
            const cleanTextForAudio = data.answer.replace(/[\*\#\`\_]/g, '');
            const botMessages = document.getElementsByClassName("bot-message");
            const lastBotMessage = botMessages[botMessages.length - 1];
            const speakerBtn = lastBotMessage.querySelector(".btn-speak");
            speakText(cleanTextForAudio, speakerBtn);
        }

    } catch (err) {
        console.error(err);
        messageArea.removeChild(typingBubble);
        appendMessage("bot", "Forgive me, traveler. An error occurred in the archives. Please try asking your question again.");
    }
}

function appendMessage(role, text, sources = []) {
    const messageArea = document.getElementById("message-area");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role === 'user' ? 'user-message' : 'bot-message'}`;

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const avatarIcon = role === 'user' ? 'fa-user' : 'fa-building-columns';
    const sender = role === 'user' ? 'Student' : 'Chronicles of India Bot';

    // Format bolding and lists in markdown simply for display
    const formattedText = formatSimpleMarkdown(text);

    let sourcesHtml = "";
    let speakActionHtml = "";

    if (role === 'bot') {
        speakActionHtml = `
            <div class="message-actions">
                <button class="mini-action-btn btn-speak" title="Listen to answer" onclick="speakMessageBubble(this)">
                    <i class="fa-solid fa-volume-high"></i>
                </button>
            </div>
        `;

        if (sources && sources.length > 0) {
            const sourceTags = sources.map(src => `${src.class} (${src.title})`).join(" | ");
            sourcesHtml = `
                <div class="message-footer">
                    <span class="sources-list"><i class="fa-solid fa-book-open"></i> Source: ${sourceTags}</span>
                    ${speakActionHtml}
                </div>
            `;
        } else {
            sourcesHtml = `
                <div class="message-footer">
                    <span class="sources-list"><i class="fa-solid fa-circle-info"></i> Fallback Knowledge Base</span>
                    ${speakActionHtml}
                </div>
            `;
        }
    }

    messageDiv.innerHTML = `
        <div class="avatar"><i class="fa-solid ${avatarIcon}"></i></div>
        <div class="message-content">
            <div class="message-header">
                <span class="sender-name">${sender}</span>
                <span class="timestamp">${time}</span>
            </div>
            <p>${formattedText}</p>
            ${sourcesHtml}
        </div>
    `;

    messageArea.appendChild(messageDiv);
    messageArea.scrollTop = messageArea.scrollHeight;
}

// Basic custom markdown parsing to render clean bullet points and bolding
function formatSimpleMarkdown(text) {
    let cleanText = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Replace linebreaks with <br>
    cleanText = cleanText.replace(/\n/g, "<br>");
    
    // Bold parsing (**text**)
    cleanText = cleanText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    
    // Bullet point replacement (e.g. * or - at start of lines)
    cleanText = cleanText.replace(/(?:^|<br>)\s*[\*\-]\s+(.*?)(?=<br>|$)/g, "<br><span style='padding-left:1.5rem; display:inline-block;'>• $1</span>");
    
    return cleanText;
}

// --- TEXT-TO-SPEECH (TTS) WORKFLOW ---

function toggleGlobalTTS() {
    globalTTSEnabled = !globalTTSEnabled;
    const btn = document.getElementById("btn-tts-toggle");
    
    if (globalTTSEnabled) {
        btn.innerHTML = `<i class="fa-solid fa-volume-high" style="color: var(--color-primary-dark)"></i>`;
        btn.title = "Auto Read-out ON";
    } else {
        btn.innerHTML = `<i class="fa-solid fa-volume-xmark"></i>`;
        btn.title = "Auto Read-out OFF";
        stopSpeaking();
    }
}

function stopSpeaking() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
    if (currentSpeakerButton) {
        currentSpeakerButton.innerHTML = `<i class="fa-solid fa-volume-high"></i>`;
        currentSpeakerButton = null;
    }
}

function speakMessageBubble(btnElement) {
    // Get text content of the message
    const messageContentDiv = btnElement.closest(".message-content");
    const paragraphs = Array.from(messageContentDiv.querySelectorAll("p"));
    let fullText = paragraphs.map(p => p.innerText).join("\n");
    
    // Strip sources out
    fullText = fullText.replace(/Source:.*$/g, '');

    if (currentSpeechUtterance && window.speechSynthesis.speaking && currentSpeakerButton === btnElement) {
        // Toggle Stop if clicked on currently playing button
        stopSpeaking();
        return;
    }

    // Stop whatever is playing
    stopSpeaking();

    // Set active button
    currentSpeakerButton = btnElement;
    btnElement.innerHTML = `<i class="fa-solid fa-stop" style="color: var(--color-error)"></i>`;

    speakText(fullText, btnElement);
}

function speakText(text, btnElement) {
    if (!window.speechSynthesis) {
        console.warn("Speech synthesis not supported in this browser.");
        return;
    }

    currentSpeechUtterance = new SpeechSynthesisUtterance(text);
    
    // Search for a natural English voice
    const voices = window.speechSynthesis.getVoices();
    let selectedVoice = voices.find(voice => voice.lang.includes("en-IN")) || // English India (fitting!)
                     voices.find(voice => voice.lang.includes("en-US")) || // English US
                     voices.find(voice => voice.lang.includes("en"));      // Generic English
                     
    if (selectedVoice) {
        currentSpeechUtterance.voice = selectedVoice;
    }
    
    currentSpeechUtterance.rate = 1.0;
    
    currentSpeechUtterance.onend = () => {
        if (btnElement) {
            btnElement.innerHTML = `<i class="fa-solid fa-volume-high"></i>`;
        }
        currentSpeakerButton = null;
    };

    currentSpeechUtterance.onerror = () => {
        if (btnElement) {
            btnElement.innerHTML = `<i class="fa-solid fa-volume-high"></i>`;
        }
        currentSpeakerButton = null;
    };

    window.speechSynthesis.speak(currentSpeechUtterance);
}

// Fix voices loading asynchronously in some browsers
if (window.speechSynthesis && window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = () => {};
}

// --- TIMELINE LOADING & RENDERING ---
async function loadTimelineData() {
    try {
        const response = await fetch("/api/timeline");
        const timelineData = await response.json();
        
        const timelineList = document.getElementById("timeline-list");
        timelineList.innerHTML = "";
        
        timelineData.forEach(event => {
            const itemDiv = document.createElement("div");
            itemDiv.className = "timeline-item";
            
            itemDiv.innerHTML = `
                <div class="timeline-node"></div>
                <div class="timeline-card">
                    <div class="timeline-card-header">
                        <h3>${event.title}</h3>
                        <div>
                            <span class="timeline-date">${event.date}</span>
                            <span class="timeline-era-tag" style="margin-left: 0.75rem;">${event.era}</span>
                        </div>
                    </div>
                    <p>${event.description}</p>
                    <button class="timeline-query-btn" onclick="sendSuggested('${event.search_query.replace(/'/g, "\\'")}')">
                        <i class="fa-solid fa-comments"></i> Consult Tutor
                    </button>
                </div>
            `;
            timelineList.appendChild(itemDiv);
        });
    } catch (e) {
        console.error("Error loading timeline data:", e);
    }
}

// --- PRACTICE QUIZ MODULE ---
async function startQuiz() {
    try {
        const response = await fetch("/api/quiz");
        quizQuestions = await response.json();
        
        // Reset States
        quizCurrentIndex = 0;
        quizScore = 0;
        
        // Hide Screens
        document.getElementById("quiz-start").classList.remove("active");
        document.getElementById("quiz-end").classList.remove("active");
        
        // Show Question Card
        document.getElementById("quiz-question-card").classList.add("active");
        
        showQuestion();
    } catch (e) {
        console.error("Error starting quiz: ", e);
        alert("Failed to load quiz from the archives.");
    }
}

function showQuestion() {
    quizAnswered = false;
    const q = quizQuestions[quizCurrentIndex];
    
    // Progress UI
    document.getElementById("quiz-progress-text").textContent = `Question ${quizCurrentIndex + 1} of ${quizQuestions.length}`;
    const percent = ((quizCurrentIndex + 1) / quizQuestions.length) * 100;
    document.getElementById("quiz-progress-fill").style.width = `${percent}%`;
    
    // Set Question Text
    document.getElementById("quiz-question-text").textContent = q.question;
    
    // Set Options
    const optionsContainer = document.getElementById("quiz-options-container");
    optionsContainer.innerHTML = "";
    
    const optionLabels = ["A", "B", "C", "D"];
    q.options.forEach((opt, idx) => {
        const btn = document.createElement("button");
        btn.className = "option-btn";
        btn.onclick = () => selectOption(idx, btn);
        btn.innerHTML = `
            <span class="option-number">${optionLabels[idx]}</span>
            <span class="option-val">${opt}</span>
        `;
        optionsContainer.appendChild(btn);
    });
    
    // Reset Explanation Box
    document.getElementById("quiz-explanation-box").style.display = "none";
    
    // Disable Next Button
    document.getElementById("btn-quiz-next").disabled = true;
}

function selectOption(selectedIndex, btnElement) {
    if (quizAnswered) return; // Prevent double selecting
    quizAnswered = true;
    
    const q = quizQuestions[quizCurrentIndex];
    const correctIdx = q.correct;
    
    // Disable all option buttons
    const buttons = document.querySelectorAll("#quiz-options-container .option-btn");
    buttons.forEach(btn => btn.disabled = true);
    
    // Evaluate answer
    if (selectedIndex === correctIdx) {
        btnElement.classList.add("correct");
        quizScore++;
    } else {
        btnElement.classList.add("wrong");
        // Highlight correct answer
        buttons[correctIdx].classList.add("correct");
    }
    
    // Show Explanation
    document.getElementById("quiz-explanation-text").textContent = q.explanation;
    document.getElementById("quiz-explanation-box").style.display = "block";
    
    // Enable Next Button
    document.getElementById("btn-quiz-next").disabled = false;
}

function nextQuestion() {
    quizCurrentIndex++;
    if (quizCurrentIndex < quizQuestions.length) {
        showQuestion();
    } else {
        showQuizEnd();
    }
}

function showQuizEnd() {
    // Hide Question Screen
    document.getElementById("quiz-question-card").classList.remove("active");
    
    // Show End Screen
    document.getElementById("quiz-end").classList.add("active");
    
    // Update Score display
    document.getElementById("quiz-final-score").textContent = `${quizScore} / ${quizQuestions.length}`;
    
    // Custom feedback message
    const msg = document.getElementById("quiz-evaluation-message");
    if (quizScore === 5) {
        msg.textContent = "Excellent work, historian! You have mastered the NCERT curriculum! 🌟";
    } else if (quizScore >= 3) {
        msg.textContent = "Good effort! You have a solid grasp of major historical events. 📚";
    } else {
        msg.textContent = "A great learning opportunity. Review the textbooks and challenge yourself again! 📖";
    }
}
