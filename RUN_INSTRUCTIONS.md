# Руководство по запуску и эксплуатации SPP API Client

Актуальная документация для версии **5.3.0**.

---

## 1. Подготовка окружения

### 1.1. Требования
*   Python 3.9+
*   Git

### 1.2. Установка зависимостей
Выполните установку зависимостей для разработки и тестирования:

```powershell
# Создание виртуального окружения (рекомендуется)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Установка зависимостей
pip install -r requirements.txt
pip install pytest-cov allure-pytest responses locust
```

---

## 2. Конфигурация

### 2.1. Переменные окружения (.env)
Для работы с реальным API (не моками) создайте файл `.env` в корне проекта:

```env
# Базовый URL API (Stage/Prod)
SPP_API_URL=https://api.stage.spp.ru

# Токен доступа (Bearer)
SPP_API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Таймаут запросов (сек)
SPP_API_TIMEOUT=30
```

### 2.2. Конфигурация тестов
Настройки тестов находятся в `pyproject.toml` и `pytest.ini`.
Порог покрытия кода (Quality Gate): **80%**.

---

## 3. Запуск тестов

Проект поддерживает трехуровневую пирамиду тестирования.

### 3.1. Unit-тесты (Быстрые, Изолированные)
Проверяют логику клиентов с использованием моков (без сети).

```powershell
python -m pytest tests/unit
```

### 3.2. Интеграционные тесты (Stateful)
Проверяют цепочки вызовов и сохранение состояния (`TestContext`).

```powershell
python -m pytest tests/integration
```

### 3.3. E2E-тесты (Сценарии)
Имитируют поведение пользователя. По умолчанию используют заглушку (Stub) в CI, но могут быть настроены на реальный стенд.

```powershell
python -m pytest tests/e2e
```

### 3.4. Полный прогон с отчетом о покрытии
```powershell
python -m pytest --cov=src --cov-report=html
```
*Отчет будет доступен в `htmlcov/index.html`.*

---

## 4. Нагрузочное тестирование (Performance)

Используется инструмент **Locust**.

### 4.1. Конфигурация
Параметры нагрузки задаются в файле `locust.conf`:
*   `users`: Количество одновременных пользователей.
*   `host`: Целевой хост.
*   `run-time`: Длительность теста.

### 4.2. Запуск
```powershell
python -m locust --config=locust.conf
```
После запуска доступен веб-интерфейс по адресу `http://localhost:8089` (если не включен `headless = true`).

---

## 5. Использование в приложениях

### 5.1. Пример кода (Development/Production)

```python
import os
from src.utils.http import APIClient
from src.api.application.change_app_conf import change_app_conf
from src.models import ChangeAppConf

# 1. Инициализация клиента
client = APIClient(
    base_url=os.getenv("SPP_API_URL", "http://localhost:8000"),
    token=os.getenv("SPP_API_TOKEN")
)

# 2. Подготовка данных (с валидацией Pydantic)
config = ChangeAppConf(
    product_group=["milk"], 
    production_type=["line"]
)

# 3. Вызов метода
try:
    response = change_app_conf(client, body=config)
    if response.status_code == 200:
        print("Конфигурация успешно обновлена")
    else:
        print(f"Ошибка: {response.text}")
except Exception as e:
    print(f"Сетевая ошибка: {e}")
```

---

## 6. CI/CD Pipeline

Проект настроен для GitLab CI (`.gitlab-ci.yml`).

**Этапы пайплайна:**
1.  **Test**: Запуск всех тестов + проверка покрытия (не менее 80%).
2.  **Artifacts**: Сохранение отчетов Allure и Coverage XML.
3.  **Deploy**: (Заглушка) Деплой в PyPI или Artifactory при пуше в `main`.

---

## 7. Обновление API

При изменении спецификации `openapi.json` выполните:

1.  **Обновление моделей:**
    ```powershell
    python scripts/generate_models.py
    ```
2.  **Актуализация клиентов:**
    ```powershell
    python scripts/autonomous_filler.py
    python scripts/refactor_clients.py
    ```
