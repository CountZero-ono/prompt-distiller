const PRESETS = {
    russian_voice: `Слушай, короче, у меня тут какая-то дичь с пленкой 120 формата. Я сканирую на Epson V850, и на всех кадрах посередине идет тонкая белая вертикальная полоса. Я уже 20 минут пытаюсь понять, это я стекло заляпал или в SilverFast какая-то галка слетела. Подскажи, как эту полосу убрать шаг за шагом? И еще, напомни, до скольки наша лаба сегодня принимает заказы?`,
    rambling_homelab: `Hey man, so I'm running a Proxmox cluster with like 3 nodes, and I noticed node 2 has 95% ZFS pool memory usage, but I don't know if ARC is just taking up all RAM or if there's a memory leak in one of my docker containers in LXC 104. Can you give me a bash command to check ZFS ARC limits, also how do I cap ARC to 8GB? Please keep it simple and give me direct commands only.`,
    client_email: `Уважаемый клиент, извиняюсь что так долго не отвечать, просто у нас на прошлой неделе был завал с проявкой E-6 слайдов, проявитель подсел. Короче ваши 5 катушек готовый, сканы залил на диск. Напиши вежливый короткий email клиенту на английском языке, что заказ готов и ссылка активна 14 дней.`
};

let MODEL_REGISTRY = {};
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

document.addEventListener('DOMContentLoaded', async () => {
    await fetchModelRegistry();
    loadSavedSettings();
});

async function fetchModelRegistry() {
    try {
        const res = await fetch('/v1/models');
        if (res.ok) {
            MODEL_REGISTRY = await res.json();
            populateProviderSelects();
        }
    } catch (err) {
        console.error("Failed to load model registry:", err);
    }
}

function populateProviderSelects() {
    const mainSelect = document.getElementById('providerSelectMain');
    const modalSelect = document.getElementById('modalProviderSelect');
    
    mainSelect.innerHTML = '';
    modalSelect.innerHTML = '';

    Object.keys(MODEL_REGISTRY).forEach(pKey => {
        const p = MODEL_REGISTRY[pKey];
        const opt = document.createElement('option');
        opt.value = pKey;
        opt.innerText = p.name + (p.free_tier ? ' (Free)' : '');
        
        mainSelect.appendChild(opt.cloneNode(true));
        modalSelect.appendChild(opt);
    });

    onMainProviderChange();
}

function onMainProviderChange() {
    const pKey = document.getElementById('providerSelectMain').value;
    const modelSelect = document.getElementById('modelSelectMain');
    modelSelect.innerHTML = '';

    if (MODEL_REGISTRY[pKey]) {
        MODEL_REGISTRY[pKey].models.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.innerText = `${m.label}`;
            modelSelect.appendChild(opt);
        });
    }
    
    document.getElementById('activeModelLabel').innerText = pKey.toUpperCase();
}

function renderModalProviderSettings() {
    const pKey = document.getElementById('modalProviderSelect').value;
    const pInfo = MODEL_REGISTRY[pKey];
    if (!pInfo) return;

    const apiKeyContainer = document.getElementById('apiKeyContainer');
    const apiBaseContainer = document.getElementById('apiBaseContainer');
    const helperContainer = document.getElementById('freeKeyHelper');

    if (pInfo.requires_api_key) {
        apiKeyContainer.classList.remove('hidden');
        if (pInfo.free_tier && pInfo.key_url) {
            helperContainer.innerHTML = `💡 <strong>Free Key Access:</strong> <a href="${pInfo.key_url}" target="_blank">Get free ${pInfo.name} key ↗</a>`;
        } else if (pInfo.key_url) {
            helperContainer.innerHTML = `🔑 <strong>Developer API Console:</strong> <a href="${pInfo.key_url}" target="_blank">Get ${pInfo.name} API key ↗</a>`;
        } else {
            helperContainer.innerHTML = '';
        }
    } else {
        apiKeyContainer.classList.add('hidden');
        helperContainer.innerHTML = '';
    }

    // Show apiBaseContainer for local server providers
    if (['llamacpp', 'vllm', 'lmstudio', 'ollama', 'custom_local'].includes(pKey) || !pInfo.requires_api_key) {
        apiBaseContainer.classList.remove('hidden');
        const storedBases = JSON.parse(localStorage.getItem('distiller_api_bases') || '{}');
        document.getElementById('apiBaseInput').value = storedBases[pKey] || pInfo.default_api_base || 'http://127.0.0.1:8080/v1';
    } else {
        apiBaseContainer.classList.add('hidden');
    }

    const distillSelect = document.getElementById('modalDistillModelSelect');
    const execSelect = document.getElementById('modalExecModelSelect');
    distillSelect.innerHTML = '';
    execSelect.innerHTML = '';

    pInfo.models.forEach(m => {
        const dOpt = document.createElement('option');
        dOpt.value = m.id;
        dOpt.innerText = m.label;
        if (m.id === pInfo.distillation_default) dOpt.selected = true;
        distillSelect.appendChild(dOpt);

        const eOpt = document.createElement('option');
        eOpt.value = m.id;
        eOpt.innerText = m.label;
        if (m.id === pInfo.execution_default) eOpt.selected = true;
        execSelect.appendChild(eOpt);
    });

    const storedKeys = JSON.parse(localStorage.getItem('distiller_api_keys') || '{}');
    document.getElementById('apiKeyInput').value = storedKeys[pKey] || '';
}

function openSettingsModal() {
    document.getElementById('settingsModal').classList.remove('hidden');
    renderModalProviderSettings();
}

function closeSettingsModal() {
    document.getElementById('settingsModal').classList.add('hidden');
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('apiKeyInput');
    input.type = input.type === 'password' ? 'text' : 'password';
}

function saveSettings() {
    const pKey = document.getElementById('modalProviderSelect').value;
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    const apiBase = document.getElementById('apiBaseInput').value.trim();
    const customModel = document.getElementById('customModelInput').value.trim();

    const storedKeys = JSON.parse(localStorage.getItem('distiller_api_keys') || '{}');
    if (apiKey) {
        storedKeys[pKey] = apiKey;
    } else {
        delete storedKeys[pKey];
    }
    localStorage.setItem('distiller_api_keys', JSON.stringify(storedKeys));

    const storedBases = JSON.parse(localStorage.getItem('distiller_api_bases') || '{}');
    if (apiBase) {
        storedBases[pKey] = apiBase;
    } else {
        delete storedBases[pKey];
    }
    localStorage.setItem('distiller_api_bases', JSON.stringify(storedBases));

    if (customModel) {
        localStorage.setItem('distiller_custom_model', customModel);
    } else {
        localStorage.removeItem('distiller_custom_model');
    }

    document.getElementById('providerSelectMain').value = pKey;
    onMainProviderChange();
    closeSettingsModal();
    alert("Settings saved successfully!");
}

function loadSavedSettings() {
    const customModel = localStorage.getItem('distiller_custom_model');
    if (customModel) {
        document.getElementById('customModelInput').value = customModel;
    }
}

function loadPreset(key) {
    if (PRESETS[key]) {
        document.getElementById('rawPromptInput').value = PRESETS[key];
    }
}

/* Voice Recorder Logic */
async function toggleVoiceRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await uploadAndTranscribeAudio(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        
        document.getElementById('recordBtn').classList.add('recording');
        document.getElementById('recordIcon').innerText = '⏹️';
        document.getElementById('recordLabel').innerText = 'Stop & Transcribe';
    } catch (err) {
        console.error("Microphone access denied or unequipped:", err);
        alert("Microphone access denied or unavailable in your browser.");
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        document.getElementById('recordBtn').classList.remove('recording');
        document.getElementById('recordIcon').innerText = '🎤';
        document.getElementById('recordLabel').innerText = 'Record Voice Note';
    }
}

async function uploadAndTranscribeAudio(blob) {
    const formData = new FormData();
    formData.append('file', blob, 'voice_input.wav');

    const rawTextarea = document.getElementById('rawPromptInput');
    rawTextarea.value = "⏳ Transcribing audio note...";

    const providerKey = document.getElementById('providerSelectMain').value;
    const storedKeys = JSON.parse(localStorage.getItem('distiller_api_keys') || '{}');
    const apiKey = storedKeys[providerKey] || '';

    try {
        const response = await fetch(`/v1/transcribe?api_key=${encodeURIComponent(apiKey)}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(`Transcription HTTP ${response.status}`);
        const data = await response.json();
        rawTextarea.value = data.text || "No speech detected.";
    } catch (err) {
        console.error("Audio transcription failed:", err);
        alert("Audio transcription failed. Using fallback transcript.");
    }
}

async function processPrompt() {
    const rawInput = document.getElementById('rawPromptInput').value.trim();
    if (!rawInput) {
        alert("Please enter a prompt, record a voice note, or select a preset!");
        return;
    }

    const targetLang = document.getElementById('targetLangSelect').value;
    const providerKey = document.getElementById('providerSelectMain').value;
    const model = document.getElementById('modelSelectMain').value;
    const customModel = localStorage.getItem('distiller_custom_model');

    const storedKeys = JSON.parse(localStorage.getItem('distiller_api_keys') || '{}');
    const storedBases = JSON.parse(localStorage.getItem('distiller_api_bases') || '{}');
    const apiKey = storedKeys[providerKey] || '';
    const apiBase = storedBases[providerKey] || (MODEL_REGISTRY[providerKey] ? MODEL_REGISTRY[providerKey].default_api_base : '');

    const processBtn = document.getElementById('processBtn');
    processBtn.disabled = true;
    processBtn.innerHTML = '<span>⏳ Processing Pipeline...</span>';

    try {
        const payload = {
            raw_prompt: rawInput,
            target_language: targetLang,
            provider: providerKey,
            distillation_model: customModel || model,
            execution_model: customModel || model,
            api_key: apiKey,
            api_base: apiBase
        };

        const response = await fetch('/v1/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);
    } catch (err) {
        console.error("Processing failed:", err);
        alert("Error connecting to Engine API. Check server status or settings.");
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = '<span>⚡ Distill & Execute</span>';
    }
}

function renderResults(data) {
    const distillation = data.distillation || {};
    
    document.getElementById('statsBanner').classList.remove('hidden');
    document.getElementById('statRawTokens').innerText = distillation.estimated_raw_tokens || 0;
    document.getElementById('statDistilledTokens').innerText = distillation.estimated_distilled_tokens || 0;
    document.getElementById('statSavings').innerText = `-${distillation.token_savings_percent || 0}%`;
    document.getElementById('statIntent').innerText = distillation.intent || 'general';

    document.getElementById('distilledOutput').innerText = distillation.distilled_prompt || 'No distillation output.';

    const constraintsList = document.getElementById('constraintsList');
    constraintsList.innerHTML = '';
    const constraints = distillation.extracted_constraints || [];
    if (constraints.length === 0) {
        constraintsList.innerHTML = '<li class="placeholder-text">None detected</li>';
    } else {
        constraints.forEach(c => {
            const li = document.createElement('li');
            li.innerText = c;
            constraintsList.appendChild(li);
        });
    }

    document.getElementById('finalResponseOutput').innerText = data.final_response || 'No response output.';
}
