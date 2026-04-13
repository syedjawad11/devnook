# Required GitHub Actions Secrets

Set these in: GitHub repo → Settings → Secrets and variables → Actions

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| GH_PAT | GitHub Personal Access Token (repo scope) | GitHub → Settings → Developer settings → PATs |
| GOOGLE_SERVICE_ACCOUNT_JSON | Google service account JSON key (full content) | Google Cloud Console → IAM → Service Accounts → Keys |

## GSC Setup Steps
1. Go to console.cloud.google.com
2. Create project or use existing
3. Enable "Web Search Indexing API"
4. Create service account: IAM & Admin → Service Accounts → Create
5. Grant it no project roles (it only needs GSC access)
6. Create JSON key: Service Account → Keys → Add Key → JSON
7. In Google Search Console (search.google.com/search-console):
   - Go to Settings → Users and permissions
   - Add service account email as Owner
8. Copy the entire JSON key content → GitHub Secret: GOOGLE_SERVICE_ACCOUNT_JSON
