# Скрипт для пуша всех файлов проекта в GitHub репозиторий
# Для Windows PowerShell
# Использование: powershell -File scripts/push_to_github.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Push to GitHub - SmartPack Production API" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка наличия git
$gitPath = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitPath) {
    Write-Host "❌ Git не установлен. Установите git:" -ForegroundColor Red
    Write-Host "   Скачайте с: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Проверка что мы в корне проекта
if (-not (Test-Path ".git")) {
    Write-Host "❌ Текущая директория не является git-репозиторием" -ForegroundColor Red
    Write-Host "   Запустите скрипт из корневой директории проекта" -ForegroundColor Yellow
    exit 1
}

# Проверка remote
$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-Host "⚠️ Remote 'origin' не настроен." -ForegroundColor Yellow
    Write-Host "   Добавьте remote командой:" -ForegroundColor Yellow
    Write-Host "   git remote add origin https://github.com/Sellektorsar/Spp_api.git" -ForegroundColor Cyan
    exit 1
}

Write-Host "📊 Текущий статус git:" -ForegroundColor Green
git status --short | ForEach-Object { Write-Host "   $_" }

$changesCount = (git status --short | Measure-Object -Line).Lines
Write-Host "   Всего изменений: $changesCount" -ForegroundColor Gray

Write-Host ""
Write-Host "📝 Добавляем все файлы..." -ForegroundColor Green
git add -A

# Проверка есть ли что коммитить
$stagedChanges = git diff --cached --quiet 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "ℹ️  Нет новых изменений для коммита" -ForegroundColor Yellow
} else {
    Write-Host "📝 Введите сообщение коммита (или нажмите Enter для默认值):" -ForegroundColor Yellow
    $commitMsg = Read-Host
    
    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
        $commitMsg = "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm') - Test coverage expansion"
    }
    
    git commit -m $commitMsg
    Write-Host "✅ Коммит создан: $commitMsg" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Пушим в GitHub..." -ForegroundColor Green

# Определяем ветку (main или master)
$branch = "main"
if (-not (git rev-parse --abbrev-ref HEAD -eq "main")) {
    $branch = "master"
}

git push -u origin $branch 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка при пуше. Проверьте авторизацию." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Успешно запушено в GitHub!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Проверить результат:" -ForegroundColor Yellow
Write-Host "   https://github.com/Sellektorsar/Spp_api" -ForegroundColor Cyan
Write-Host ""
