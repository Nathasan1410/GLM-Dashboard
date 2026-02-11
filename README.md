# Z.ai Usage Dashboard

This project provides a simple, auto-updating dashboard to track your Z.ai API usage.

## Setup Instructions

### 1. Create a GitHub Repository

1.  Create a new **Private** repository on GitHub (e.g., `zai-usage-dashboard`).
2.  Do *not* initialize with README, .gitignore, or license if you plan to push this existing folder.

### 2. Push Code to GitHub

Open a terminal in this directory and run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

### 3. Configure Secrets

Go to your repository **Settings** > **Secrets and variables** > **Actions** and add the following secrets:

-   `ZAI_API_KEY`: Your Z.ai API Key.
    -   *Enter your actual API key here*
-   `GH_PAT`: A Personal Access Token with `repo` scope.
    -   Generate this at [GitHub Developer Settings](https://github.com/settings/tokens).
    -   This is required for the Action to push the updated `usage.json` back to the repo.

### 4. Enable GitHub Pages

1.  Go to **Settings** > **Pages**.
2.  Source: **Deploy from a branch**.
3.  Branch: **main** / **root**.
4.  Click **Save**.

### 5. Run the Workflow

1.  Go to the **Actions** tab.
2.  Select **Update Z.ai Usage Data**.
3.  Click **Run workflow**.

Once finished, your dashboard will be live at the URL provided in **Settings > Pages**.

## Local Testing

You can open `index.html` in your browser to see the dashboard. It uses `usage.json` for data.
A dummy `usage.json` is included for testing purposes.
