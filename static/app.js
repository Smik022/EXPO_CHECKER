const API_URL = "http://127.0.0.1:8000/api";

const scanBtn = document.getElementById('scanBtn');
const pathInput = document.getElementById('pathInput');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const statusText = document.getElementById('statusText');
const findingsList = document.getElementById('findingsList');
const appState = { isScanning: false };

scanBtn.addEventListener('click', async () => {
    const path = pathInput.value.trim();
    if (!path) return alert("Please enter a valid path");

    scanBtn.disabled = true;
    findingsList.innerHTML = ''; // Clear previous results

    try {
        const res = await fetch(`${API_URL}/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path })
        });
        const data = await res.json();

        if (data.status === 'started') {
            startPolling();
        } else {
            alert(data.message);
            scanBtn.disabled = false;
        }
    } catch (e) {
        alert("Failed to connect to backend");
        scanBtn.disabled = false;
    }
});

function startPolling() {
    progressContainer.style.display = 'block';
    appState.isScanning = true;

    const interval = setInterval(async () => {
        try {
            const res = await fetch(`${API_URL}/status`);
            const status = await res.json();

            updateUI(status);

            if (!status.is_scanning) {
                clearInterval(interval);
                appState.isScanning = false;
                scanBtn.disabled = false;
                loadResults(); // Final load to ensure we have everything
            }
        } catch (e) {
            clearInterval(interval);
            statusText.textContent = "Connection lost";
        }
    }, 500);
}

function updateUI(status) {
    progressBar.style.width = `${status.progress}%`;
    statusText.textContent = status.message;

    if (status.error) {
        statusText.style.color = '#ef4444';
        statusText.textContent = `Error: ${status.error}`;
    } else {
        statusText.style.color = '#94a3b8';
    }
}

async function loadResults() {
    const res = await fetch(`${API_URL}/results`);
    const findings = await res.json();

    findingsList.innerHTML = '';

    if (findings.length === 0) {
        findingsList.innerHTML = `<div style="text-align:center; padding: 2rem; color: #4ade80;">No secrets found! 🎉</div>`;
        return;
    }

    findings.forEach(finding => {
        const div = document.createElement('div');
        div.className = 'finding-card';
        div.innerHTML = `
            <div class="finding-header">
                <span class="finding-type">${finding.secret_type}</span>
                <span class="finding-meta">${finding.date.split('T')[0]} • ${finding.author}</span>
            </div>
            <div style="margin-bottom: 0.5rem; font-size: 0.9rem;">
                Commit: <code>${finding.commit_hash.substring(0, 7)}</code><br>
                File: <code>${finding.file_path}</code>
            </div>
            <code class="secret-value" title="Hover to reveal">${finding.line_content}</code>
        `;
        findingsList.appendChild(div);
    });
}
