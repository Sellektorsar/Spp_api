#!/bin/bash
# Скрипт для пуша всех файлов проекта в GitHub репозиторий
# Использование: ./scripts/push_to_github.sh

set -e

echo "=========================================="
echo "Push to GitHub - SmartPack Production API"
echo "=========================================="

# Проверка наличия git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Установите git:"
    echo "   Windows: https://git-scm.com/download/win"
    echo "   Mac: brew install git"
    echo "   Linux: sudo apt install git"
    exit 1
fi

# Проверка что мы в корне проекта
if [ ! -d ".git" ]; then
    echo "❌ Текущая директория не является git-репозиторием"
    echo "   Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Проверка remote
if ! git remote get-url origin &> /dev/null; then
    echo "⚠️ Remote 'origin' не настроен."
    echo "   Добавьте remote:"
    echo "   git remote add origin https://github.com/Sellektorsar/Spp_api.git"
    exit 1
fi

# Отображение статуса
echo ""
echo "📊 Текущий статус git:"
git status --short | head -20
echo "   ... (всего изменений: $(git status --short | wc -l))"

echo ""
echo "📝 Коммит всех изменений..."

# Добавление всех файлов
git add -A

# Проверка есть ли что коммитить
if git diff --cached --quiet; then
    echo "ℹ️  Нет новых изменений для коммита"
else
    # Коммит с описанием
    echo "Введите сообщение коммита (или оставьте пустым для默认值):"
    read -r COMMIT_MSG
    
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update: $(date '+%Y-%m-%d %H:%M') - Test coverage expansion"
    fi
    
    git commit -m "$COMMIT_MSG"
    echo "✅ Коммит создан: $COMMIT_MSG"
fi

echo ""
echo "🚀 Пушим в GitHub..."
git push -u origin main 2>/dev/null || git push -u origin master 2>/dev/null

echo ""
echo "=========================================="
echo "✅ Успешно запушено в GitHub!"
echo "=========================================="
echo ""
echo "📋 Проверить:"
echo "   https://github.com/Sellektorsar/Spp_api"
echo ""
