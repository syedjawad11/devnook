Write-Host "==========================="
Write-Host "   DEVNOOK LAUNCH SCRIPT   "
Write-Host "==========================="

Write-Host "`n1/4: Updating Astro language statistics..."
python agents/dev-team/update.py

Write-Host "`n2/4: Building the Astro Site..."
npm run build

Write-Host "`n3/4: Publishing all 20 staged seed posts to src/content/..."
python agents/publish/publish.py --count 20

Write-Host "`n4/4: Committing files to git repository..."
git add .
git commit -m "feat: launch devnook.dev — 20 posts + 10 tools"
git branch -M main

Write-Host "`n==========================="
Write-Host "           DONE!           "
Write-Host "==========================="
Write-Host "Your local repository is no longer empty!"
Write-Host ""
Write-Host "NEXT STEPS:"
Write-Host "1. Check if git remote exists: git remote -v"
Write-Host "2. If not, add your GitHub repo: git remote add origin https://github.com/syedjawad11/DevNook-.git"
Write-Host "3. Push the code: git push -u origin main"
Write-Host "4. Go back to Cloudflare Pages, connect the repository, and click 'Begin setup'."
