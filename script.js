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
            localStorage.removeItem('gh_pat'); // Clear invalid token
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

function createQuotaCard(quota) {
    const card = document.createElement('div');
    card.className = 'quota-card';

    const used = quota.used || 0;
    const limit = quota.limit || 1;
    const percentage = Math.min((used / limit) * 100, 100);

    // Choose icon based on title or context
    let iconClass = 'fa-solid fa-cube'; // default
    let iconWrapperClass = 'icon-default';

    const lowerTitle = quota.title.toLowerCase();
    if (lowerTitle.includes('token')) {
        iconClass = 'fa-solid fa-coins';
        iconWrapperClass = 'icon-tokens';
    } else if (lowerTitle.includes('request') || lowerTitle.includes('api')) {
        iconClass = 'fa-solid fa-network-wired';
        iconWrapperClass = 'icon-requests';
    }

    // Determine progress bar styling
    let progressBarClass = '';
    let percentageColor = '#10b981'; // success green

    if (percentage > 90) {
        progressBarClass = 'critical';
        percentageColor = '#ef4444';
    } else if (percentage > 75) {
        progressBarClass = 'high';
        percentageColor = '#f59e0b';
    }

    // Format reset time
    const resetTime = quota.resetTime ? new Date(quota.resetTime).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Never';

    card.innerHTML = `
        <div class="quota-header">
            <div class="icon-wrapper ${iconWrapperClass}">
                <i class="${iconClass}"></i>
            </div>
            <div style="text-align: right;">
                <h3 class="quota-title">${quota.title}</h3>
                <span class="quota-limit">Limit: ${formatNumber(limit)}</span>
            </div>
        </div>
        
        <div class="usage-stats">
            <span class="current-usage">${formatNumber(used)}</span>
            <span class="percentage-badge" style="color: ${percentageColor}">${percentage.toFixed(1)}%</span>
        </div>

        <div class="progress-container">
            <div class="progress-bar ${progressBarClass}" style="width: ${percentage}%"></div>
        </div>

        <div class="reset-info">
            <i class="fa-regular fa-clock"></i>
            <span>Resets: ${resetTime}</span>
        </div>
    `;
    return card;
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    return num.toLocaleString();
}
