document.addEventListener('DOMContentLoaded', () => {
    fetchUsageData();
    setupRefreshButton();
});

function setupRefreshButton() {
    const btn = document.getElementById('refresh-btn');
    btn.addEventListener('click', async () => {
        const repoOwner = 'Nathasan1410';
        const repoName = 'GLM-Dashboard';

        // 1. Get PAT from local storage or prompt user
        let pat = localStorage.getItem('gh_pat');
        if (!pat) {
            pat = prompt("To refresh data from here, please enter your GitHub Personal Access Token (PAT):");
            if (pat) {
                localStorage.setItem('gh_pat', pat);
            } else {
                return;
            }
        }

        // 2. Trigger Workflow
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Triggering...';

        try {
            const response = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/actions/workflows/update-dashboard.yml/dispatches`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${pat}`,
                    'Accept': 'application/vnd.github.v3+json'
                },
                body: JSON.stringify({ ref: 'main' })
            });

            if (response.ok) {
                alert('Update started! The dashboard will refresh automatically in about 1-2 minutes.');
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Started';
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fa-solid fa-sync"></i> Refresh Data';
                }, 5000);
            } else {
                const err = await response.json();
                throw new Error(err.message || 'Failed to trigger workflow');
            }
        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}. Check your PAT and try again.`);
            // localStorage.removeItem('gh_pat'); // Keep the token, it might be a temporary error
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-sync"></i> Refresh Data';
        }
    });
}

async function fetchUsageData() {
    const container = document.getElementById('dashboard-container');
    const lastUpdatedEl = document.getElementById('last-updated');

    try {
        const response = await fetch('usage.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        // Update last updated time
        lastUpdatedEl.textContent = `Last Updated: ${new Date(data.lastUpdated).toLocaleString()}`;

        // Clear loading message
        container.innerHTML = '';
        const grid = document.createElement('div');
        grid.className = 'dashboard-grid';

        // Render each quota
        data.quotas.forEach(quota => {
            const card = createQuotaCard(quota);
            grid.appendChild(card);
        });

        container.appendChild(grid);

    } catch (error) {
        console.error("Failed to fetch or parse usage data:", error);
        container.innerHTML = `<p style="color: red; text-align: center;">Could not load usage data. Please ensure the GitHub Action has run successfully.</p>`;
        lastUpdatedEl.textContent = 'Error loading data.';
    }
}

function createQuotaCard(item) {
    const percentage = item.limit > 0 && typeof item.used === 'number'
        ? Math.min((item.used / item.limit) * 100, 100)
        : 0;

    // Determine if we should show a progress bar or just text
    const showProgressBar = item.limit > 0 && typeof item.used === 'number';
    const statusClass = typeof item.used === 'string' && (item.used.toLowerCase().includes('error') || item.used.toLowerCase().includes('down')) ? 'status-error' : 'status-ok';

    const cardHTML = `
        <div class="quota-card">
            <div class="card-header">
                <div class="card-icon">
                    <i class="fa-solid fa-server"></i>
                </div>
                <div class="card-title">
                    <h3>${item.title}</h3>
                    ${item.tooltip ? `<span class="tooltip-icon" title="${item.tooltip}"><i class="fa-regular fa-circle-question"></i></span>` : ''}
                    <p class="limit-text">${item.limit > 0 ? `Limit: ${formatNumber(item.limit)}` : ''}</p>
                </div>
            </div>
            
            <div class="usage-stats">
                <h2 class="${statusClass}">${typeof item.used === 'number' ? formatNumber(item.used) : item.used} <span class="unit">${item.unit_text}</span></h2>
                ${showProgressBar ? `<span class="percentage">${percentage.toFixed(1)}%</span>` : ''}
            </div>

            ${showProgressBar ? `
            <div class="progress-container">
                <div class="progress-bar" style="width: ${percentage}%"></div>
            </div>
            ` : ''}
            
            <div class="reset-info">
                <i class="fa-regular fa-clock"></i> Updates every 15 min
            </div>
        </div>
    `;
    const card = document.createElement('div');
    card.innerHTML = cardHTML;
    return card.firstElementChild;
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    return num.toLocaleString();
}


