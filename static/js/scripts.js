// Function to toggle the dynamic configuration form based on deployment mode selection
function updateDynamicForm() {
    var modeSelect = document.getElementById('deployment-mode');
    var simpleConfig = document.getElementById('simple-config');
    var expertConfig = document.getElementById('expert-config');

    if (modeSelect.value === 'expert') {
        simpleConfig.style.display = 'none';
        expertConfig.style.display = 'block';
    } else {
        simpleConfig.style.display = 'block';
        expertConfig.style.display = 'none';
    }
}

// Existing functions
function showFeedback() {
    const action = document.querySelector('select[name="action"]').value;
    const feedback = document.getElementById('feedback');
    feedback.textContent = `You selected: ${action}`;
}

function toggleSubTree(event) {
    const subTree = event.target.nextElementSibling;
    if (subTree) {
        subTree.style.display = subTree.style.display === 'none' ? 'block' : 'none';
    }
}

function switchMode(mode) {
    document.getElementById('day-mode').disabled = mode !== 'day';
    document.getElementById('night-mode').disabled = mode !== 'night';
}

async function validateConfig() {
    const configInput = document.getElementById('config-input').value;
    const response = await fetch('/validate_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ config: configInput })
    });
    const result = await response.json();
    const validationFeedback = document.getElementById('validation-feedback');
    if (result.valid) {
        validationFeedback.textContent = 'Configuration is valid.';
        validationFeedback.style.color = 'green';
    } else {
        validationFeedback.textContent = `Invalid configuration: ${result.error}`;
        validationFeedback.style.color = 'red';
    }
}

async function predictConfig() {
    const configInput = document.getElementById('config-input').value;
    const response = await fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ config: configInput })
    });
    const result = await response.json();
    const predictionFeedback = document.getElementById('prediction-feedback');
    if (result.prediction) {
        predictionFeedback.textContent = `Prediction: ${result.prediction}`;
        predictionFeedback.style.color = 'blue';
    } else {
        predictionFeedback.textContent = `Prediction error: ${result.error}`;
        predictionFeedback.style.color = 'red';
    }
}

// Function to toggle sidebars
function toggleSidebar(sidebarId) {
    var sidebar = document.getElementById(sidebarId);
    if (sidebar.style.display === 'none' || sidebar.style.display === '') {
        sidebar.style.display = 'block';
    } else {
        sidebar.style.display = 'none';
    }
}

function toggleStep(id) {
    var content = document.getElementById(id);
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
    } else {
        content.style.display = 'none';
    }
}

// Function to handle chat input
async function handleChatInput(event) {
    if (event.key === 'Enter') {
        const input = document.getElementById('chat-input').value;
        const chatWindow = document.getElementById('chat-window');
        chatWindow.innerHTML += `<div class='user-message'>${input}</div>`;
        document.getElementById('chat-input').value = '';
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: input })
        });
        const result = await response.json();
        chatWindow.innerHTML += `<div class='llm-response'>${result.response}</div>`;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}

// Function to show command suggestions
function showSuggestions() {
    const input = document.getElementById('command-input').value.toLowerCase();
    const suggestions = document.getElementById('suggestions');
    suggestions.innerHTML = '';
    if (input) {
        const filteredCommands = commands.filter(command => command.includes(input));
        filteredCommands.forEach(command => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'suggestion-item';
            suggestionItem.innerText = command;
            suggestionItem.onclick = () => {
                document.getElementById('command-input').value = command;
                suggestions.innerHTML = '';
            };
            suggestions.appendChild(suggestionItem);
        });
    }
}