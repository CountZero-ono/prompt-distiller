const PRESETS = {
    russian_voice: `Слушай, короче, у меня тут какая-то дичь с пленкой 120 формата. Я сканирую на Epson V850, и на всех кадрах посередине идет тонкая белая вертикальная полоса. Я уже 20 минут пытаюсь понять, это я стекло заляпал или в SilverFast какая-то галка слетела. Подскажи, как эту полосу убрать шаг за шагом? И еще, напомни, до скольки наша лаба сегодня принимает заказы?`,
    rambling_homelab: `Hey man, so I'm running a Proxmox cluster with like 3 nodes, and I noticed node 2 has 95% ZFS pool memory usage, but I don't know if ARC is just taking up all RAM or if there's a memory leak in one of my docker containers in LXC 104. Can you give me a bash command to check ZFS ARC limits, also how do I cap ARC to 8GB? Please keep it simple and give me direct commands only.`,
    client_email: `Уважаемый клиент, извиняюсь что так долго не отвечать, просто у нас на прошлой неделе был завал с проявкой E-6 слайдов, проявитель подсел. Короче ваши 5 катушек готовый, сканы залил на диск. Напиши вежливый короткий email клиенту на английском языке, что заказ готов и ссылка активна 14 дней.`
};

function loadPreset(key) {
    if (PRESETS[key]) {
        document.getElementById('rawPromptInput').value = PRESETS[key];
    }
}

async function processPrompt() {
    const rawInput = document.getElementById('rawPromptInput').value.trim();
    if (!rawInput) {
        alert("Please enter a prompt or select a preset!");
        return;
    }

    const targetLang = document.getElementById('targetLangSelect').value;
    const model = document.getElementById('modelSelect').value;
    const processBtn = document.getElementById('processBtn');

    // UI Loading State
    processBtn.disabled = true;
    processBtn.innerHTML = '<span>⏳ Processing Pipeline...</span>';

    try {
        const response = await fetch('/v1/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                raw_prompt: rawInput,
                target_language: targetLang,
                model: model
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);
    } catch (err) {
        console.error("Processing failed:", err);
        alert("Error connecting to Engine API. Check server logs.");
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = '<span>⚡ Distill & Execute</span>';
    }
}

function renderResults(data) {
    const distillation = data.distillation || {};
    
    // Stats Banner
    document.getElementById('statsBanner').classList.remove('hidden');
    document.getElementById('statRawTokens').innerText = distillation.estimated_raw_tokens || 0;
    document.getElementById('statDistilledTokens').innerText = distillation.estimated_distilled_tokens || 0;
    document.getElementById('statSavings').innerText = `-${distillation.token_savings_percent || 0}%`;
    document.getElementById('statIntent').innerText = distillation.intent || 'general';

    // Distilled Prompt Box
    document.getElementById('distilledOutput').innerText = distillation.distilled_prompt || 'No distillation output.';

    // Constraints List
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

    // Final Response Box
    document.getElementById('finalResponseOutput').innerText = data.final_response || 'No response output.';
}
