# workplace-setup scan for Windows PowerShell — read-only. Installs nothing.
$ok=0; $warn=0; $bad=0
function P($s,$n,$d){ "{0} {1,-26} {2}" -f $s,$n,$d | Write-Output
switch($s){ "OK" {$script:ok++} "!!" {$script:warn++} "XX" {$script:bad++} } }
function Have($c){ [bool](Get-Command $c -ErrorAction SilentlyContinue) }

"-- machine --"
P "OK" "OS" ([System.Environment]::OSVersion.VersionString)
P "OK" "user @ host" "$env:USERNAME @ $env:COMPUTERNAME"
if (Have winget) { P "OK" "winget" "present" } else { P "XX" "winget" "install App Installer from the Microsoft Store" }

"-- required --"
if (Have git) { P "OK" "git" (git --version) } else { P "XX" "git" "winget install Git.Git" }
$agent = if ($env:AGENT_CLI) { $env:AGENT_CLI } else { "codex" }
if (Have $agent) { P "OK" "agent CLI ($agent)" (& $agent --version | Select-Object -First 1) }
elseif (Have npm) { P "XX" "agent CLI ($agent)" "npm install -g @openai/codex" }
else { P "XX" "agent CLI ($agent)" "install Node first, then: npm install -g @openai/codex" }
if (Have git) {
if ((git config --global user.name) -and (git config --global user.email)) { P "OK" "git identity" (git config --global user.name) }
else { P "!!" "git identity" 'git config --global user.name "Your Name"; git config --global user.email you@example.org' } }

"-- recommended --"
if (Have node) { P "OK" "Node.js" (node --version) } else { P "XX" "Node.js" "winget install OpenJS.NodeJS.LTS" }
if (Have gh) { gh auth status *> $null; if ($LASTEXITCODE -eq 0) { P "OK" "GitHub CLI" "logged in" } else { P "!!" "GitHub CLI" "gh auth login" } }
else { P "XX" "GitHub CLI" "winget install GitHub.cli" }
$py = $null; foreach ($c in "py","python","python3") { if (Have $c) { $py=$c; break } }
if ($py) {
$v = & $py -c "import sys;print('%d.%d'%sys.version_info[:2])" 2>$null
if ($LASTEXITCODE -eq 0) { P "OK" "Python" "$v ($py)" } else { P "!!" "Python" "$v is old; want 3.11+ -> winget install Python.Python.3.12" } }
else { P "XX" "Python" "winget install Python.Python.3.12" }

"-- optional --"
if (Have pandoc) { P "OK" "pandoc" "present" } else { P "XX" "pandoc" "winget install JohnMacFarlane.Pandoc" }
if (Have pdftoppm) { P "OK" "poppler (pdftoppm)" "present" } else { P "XX" "poppler (pdftoppm)" "winget install oschwartz10612.Poppler" }
if (Have magick) { P "OK" "ImageMagick" "present" } else { P "XX" "ImageMagick" "winget install ImageMagick.ImageMagick" }
if ((Have soffice) -or (Test-Path "C:\Program Files\LibreOffice\program\soffice.exe")) { P "OK" "LibreOffice" "present" } else { P "XX" "LibreOffice" "winget install TheDocumentFoundation.LibreOffice" }
if (Have ollama) { P "OK" "Ollama (local models)" "present" } else { P "XX" "Ollama (local models)" "winget install Ollama.Ollama" }
$ch = @("C:\Program Files\Google\Chrome\Application\chrome.exe","C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($ch) { P "OK" "headless browser" $ch } else { P "XX" "headless browser" "install Chrome or Edge (HTML -> PDF/PNG)" }

"-- agent skills --"
$sk = if ($env:SKILLS_DIR) { $env:SKILLS_DIR } else { Join-Path $HOME ".agents\skills" }
if (Test-Path $sk) {
$n = (Get-ChildItem $sk -Recurse -Depth 1 -Filter SKILL.md -ErrorAction SilentlyContinue).Count
P "OK" "skills folder" "$sk ($n skills)"
git -C $sk rev-parse *> $null
if ($LASTEXITCODE -eq 0) {
if (git -C $sk remote get-url origin 2>$null) { P "OK" "skills in git" "remote set" } else { P "!!" "skills in git" "no remote -> gh repo create my-agent-skills --private --source $sk --push" }
if (-not (git -C $sk status --porcelain)) { P "OK" "skills committed" "clean" } else { P "!!" "skills committed" "uncommitted edits -> commit + push" } }
else { P "!!" "skills in git" "not a repo -> see SKILL.md section 3" } }
else { P "!!" "skills folder" "missing -> New-Item -ItemType Directory $sk" }
if (Test-Path (Join-Path $sk "workplace-setup\config.md")) { P "OK" "config.md" "present" } else { P "!!" "config.md" "copy config.example.md -> config.md and fill it in" }
if ($sk -match "OneDrive|Dropbox|iCloud") { P "!!" "sync-folder check" "skills inside a cloud-sync folder: move them out" }
""
"-- summary: $ok OK · $warn !! · $bad XX --"
